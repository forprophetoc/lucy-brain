"""gen_controls_review.py — emit CONTROLS-REVIEW.md straight FROM the live control
suite in controls.py (introspection, not hand-authored), so the review document can
never drift from the code that actually runs. No engine, no network, no transmission.

Run:  python gen_controls_review.py   ->   writes CONTROLS-REVIEW.md
"""
import inspect
import re
import pathlib
from datetime import datetime

import controls
from controls import CONTROLS
from harness import INBOUND_EVENT_TYPES

OUT = pathlib.Path(__file__).parent / "CONTROLS-REVIEW.md"

FIELD_RE = re.compile(r"""r(?:\.get\(|\[)\s*['"](\w+)['"]""")
REGEX_RE = re.compile(r"\b([A-Z][A-Z0-9_]*_RE)\b")


def _src(fn):
    try:
        return inspect.getsource(fn)
    except (OSError, TypeError):
        return "<source unavailable>"


def _fields_checked(src):
    return sorted(set(FIELD_RE.findall(src)))


def _regexes_used(src):
    out = []
    for name in sorted(set(REGEX_RE.findall(src))):
        rx = getattr(controls, name, None)
        if rx is not None and hasattr(rx, "pattern"):
            out.append((name, rx.pattern))
    return out


def _quiet(scheduled_at):
    m = re.search(r"T(\d{2}):", scheduled_at or "")
    if not m:
        return ""
    hour = int(m.group(1))
    return "  **(quiet hours 21:00-08:00)**" if not (8 <= hour < 21) else ""


def _control_section(c):
    cid = c["control_id"]
    assert_ev = c["assert_event"]
    events = c["events"]
    asserting = next((e for e in events if e["event_id"] == assert_ev), events[-1])
    is_inbound = asserting["event_type"] in INBOUND_EVENT_TYPES
    canary = "deliberate" in cid

    if canary:
        sendcat = "**SEND** (inbound -> send_now) — but assertion FAILS on purpose (canary)"
    elif is_inbound:
        sendcat = "**SEND** (inbound -> engine forces send_now)"
    else:
        sendcat = "**NO-SEND / dark** (proactive; not an inbound)"

    L = [f"## {cid}", "", f"- **Send vs no-send:** {sendcat}",
         f"- **Asserting event:** `{assert_ev}` (`{asserting['event_type']}`)"]

    # Contact setup (what seeds Lucy's context). phone withheld; never shown.
    contact = c["contacts"][0] if c["contacts"] else {}
    setup = {k: contact.get(k) for k in ("package", "estimate_amount", "tags",
                                         "first_name", "last_name", "city", "service")
             if contact.get(k)}
    note = contact.get("persona_note")
    L.append(f"- **Contact setup (context seed):** {setup}")
    if note:
        L.append(f"  - persona_note (WITHHELD from Lucy by the harness): {note!r}")

    # Exact input Lucy receives, step by step (prior steps seed memory).
    L.append("- **Exact input Lucy receives (in order):**")
    for e in events:
        tag = "  <- ASSERTING" if e["event_id"] == assert_ev else ""
        L.append(f"  - `{e['event_id']}` step=`{e.get('arc_step','')}` "
                 f"type=`{e['event_type']}` at `{e['scheduled_at']}`{_quiet(e['scheduled_at'])}{tag}")
        if e.get("inbound_text"):
            L.append(f"    - inbound_text: {e['inbound_text']!r}")
        if e.get("expected_behavior"):
            L.append(f"    - (harness-only note, NOT shown to Lucy): {e['expected_behavior']!r}")
    if len(events) > 1:
        L.append("  - *(earlier step(s) run first and seed this contact's memory/thread "
                 "before the asserting event.)*")

    # Expected behavior — author's plain English, lives in code.
    L.append(f"- **Expected behavior (plain English):** {c['expectation']}")

    # Assertion — fields checked, the literal regexes that drive PASS/FAIL, and source.
    src = _src(c["assert_fn"])
    L.append(f"- **Assertion checks these fields:** {_fields_checked(src)}")
    rxs = _regexes_used(src)
    if rxs:
        L.append("- **Patterns that decide PASS/FAIL (verbatim from code):**")
        for name, pat in rxs:
            L.append(f"  - `{name}` = `{pat}`")
    L.append("- **Assertion (verbatim source):**")
    L.append("  ```python")
    for line in src.rstrip().splitlines():
        L.append("  " + line)
    L.append("  ```")
    L.append("")
    return "\n".join(L)


def main():
    real = [c for c in CONTROLS if "deliberate" not in c["control_id"]]
    canaries = [c for c in CONTROLS if "deliberate" in c["control_id"]]

    head = [
        "# Lucy Control Suite — Review Sheet",
        "",
        f"*Auto-generated from `controls.py` by `gen_controls_review.py` on "
        f"{datetime.now().isoformat(timespec='seconds')}. Do not hand-edit — "
        f"regenerate so it can't drift from the code that runs.*",
        "",
        f"**{len(real)} real controls + {len(canaries)} canary.** "
        "This is Oscar's to review and correct.",
        "",
        "## How sending & scoring work (applies to all controls)",
        "",
        "- **Inbound** (`inbound_reply`): the engine deterministically forces "
        "`send_now` (an inbound is never silent) — so in a live run it WOULD transmit. "
        "If the model returns an empty reply or errors, it escalates to Oscar instead "
        "(still not silent).",
        "- **Proactive** (e.g. `estimate_ready`): subject to quiet hours (21:00-08:00 "
        "local). A proactive event in quiet hours stays dark (no send).",
        "- The harness strips `expected_behavior` and `persona_note` before the model "
        "sees anything — those are scoring notes only, never inputs to Lucy.",
        "- Many inbound controls score via the shared `_reply_or_escalation` rule:",
        "",
        "  ```python",
    ]
    head += ["  " + l for l in _src(controls._reply_or_escalation).rstrip().splitlines()]
    head += [
        "  ```",
        "",
        "  i.e. **PASS** = the draft is harm-free AND (it's a clean escalation to Oscar "
        "OR a non-empty reply that shows the required positive signal); **FAIL** = a "
        "harmful pattern appears, or there's no escalation and the reply is empty/missing "
        "the positive signal.",
        "",
        "---",
        "",
    ]

    body = [_control_section(c) for c in real]
    tail = ["---", "", "# Canary (must FAIL — proves the checker bites)", ""]
    tail += [_control_section(c) for c in canaries]

    OUT.write_text("\n".join(head + body + tail), encoding="utf-8")
    print(f"wrote {OUT} ({OUT.stat().st_size} bytes; {len(real)} real + {len(canaries)} canary)")


if __name__ == "__main__":
    main()
