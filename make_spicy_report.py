#!/usr/bin/env python3
"""
make_spicy_report.py — SPICY_FINAL_REPORT.md from bakeoff_results/spicy_final.json (spicy_exam.py).
Totals, the hard-fail list (full replies) at the top, the Stage 1 line changes, the closing classes, then every
scenario with all runs: full reply, decision, checks, latency.

Run: py -3.14 make_spicy_report.py
"""
import json
import os
import statistics
from collections import Counter

import spicy_exam as X

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "SPICY_FINAL_REPORT.md")

STAGE1 = [
    ("a", "Merged closing lines (role, shape, can't see calendar, read-the-room gate, Oscar hand-off, 4 examples)",
     "already applied earlier in this session (amendment + your answers); Touch 1 ending removed; "
     "\"ANSWER it fully and stop\" -> \"ANSWER it fully, then add ONE booking step and stop.\"; the Muse-only "
     "closing block was replaced"),
    ("b", "\"A 10% discount is offered for veterans and first responders.\"",
     "\"A 10% discount is offered for veterans; seniors get 5% — one or the other, never both. (Oscar 2026-10-12: "
     "no other discounts.)\" + new discounts line: \"No price match and no other discount of any kind — only "
     "veteran 10% or senior 5%. If a customer asks you to match a price or go lower, hold their price and hand to "
     "Oscar: 'Let me get Oscar on that for you.'\" (Spicy: \"…You may escalate to Oscar whenever you judge it's "
     "needed.\")"),
    ("c", "\"the advertised $299 starting price is for a standard tub; a one-piece tub/shower combo is a different "
          "job, so its price is the customer's own estimate.\"",
     "\"the advertised $299 starting price is for most standard tubs; a one-piece tub/shower combo or a shower is a "
     "different job, priced on the customer's own estimate.\""),
    ("d", "(added earlier this session) \"Gold is built for soaking and holds up to daily use; Silver wears faster "
          "with heavy use.\"", "\"Soaking: Gold holds up to anything, including daily soaking; Silver wears much faster.\""),
    ("e", "—", "already applied: \"No essential oils or bath bombs in any refinished tub — ours or anyone else's.\""),
    ("f", "\"Platinum is our iso-free option with virtually no fumes.\"",
     "same + \"It leaves no harmful fumes behind — offer it when a customer raises a health concern (asthma, "
     "sensitivities). In texts call it Platinum, never 'iso-free' (no 'free').\""),
    ("g", "\"Biscuit is light (like the inside of a biscuit); almond is noticeably darker.\"",
     "same + \"Kohler Biscuit is a very light tan. Two colors on one job are fine (e.g. a white shower and a Biscuit "
     "tub).\""),
    ("h", "\"We remove and replace the caulking (included) and handle everything else, including cleanup.\"",
     "\"We handle everything else, including cleanup. Gold and above also include filling nicks, chips and screw "
     "holes and replacing the old caulk — never promise these on a Silver job.\""),
    ("i", "—", "already applied (F20 fix, commit 6ae9e94): return after going quiet -> warm, no guilt, ONE booking step"),
]


def load():
    with open(os.path.join(X.RESULTS_DIR, "spicy_final.json"), encoding="utf-8") as fh:
        return json.load(fh)


def decision(r):
    return "ESCALATE" if r["response"].get("send_decision") == "escalate_human" else "send"


def run_lines(r):
    fails = [f"{k} [{v['kind']}]" + (f" ({v['note']})" if v["note"] else "")
             for k, v in r["grade"]["rules"].items() if not v["pass"]]
    out = [f"- run {r['rep']} · **{decision(r)}** · {r['latency_s']:.1f}s: \"{r['response'].get('reply') or ''}\"",
           f"  - checks ({len(r['grade']['rules'])}): {'all pass' if not fails else 'FAIL ' + '; '.join(fails)}"]
    if r["response"].get("error"):
        out.append(f"  - error: {r['response']['error']}")
    return out


def pct(a, b):
    return f"{a}/{b} ({100 * a / b:.0f}%)" if b else "0/0"


def main():
    data = load()
    rows = data["rows"]
    by = {}
    for r in rows:
        by.setdefault(r["key"], []).append(r)
    P = X.plan()
    lat = [r["latency_s"] for r in rows]
    hard_runs = [r for r in rows if r["grade"]["hard_fails"]]
    hard_checks = Counter(h for r in rows for h in r["grade"]["hard_fails"])
    close_rows = [r for r in rows if r["grade"]["closing_class"] == "close"]
    quiet_rows = [r for r in rows if r["grade"]["closing_class"] in ("quiet", "photo")]
    photo_rows = [r for r in rows if r["grade"]["closing_class"] == "photo"]
    closed = sum(r["grade"]["rules"]["closes_with_one_step"]["pass"] for r in close_rows)
    quiet = sum(r["grade"]["rules"]["no_booking_push"]["pass"] for r in quiet_rows)
    photo = sum(r["grade"]["rules"]["photo_ask_is_the_close"]["pass"] for r in photo_rows)
    full = sum(all(r["grade"]["all_pass"] for r in v) and len(v) == data["reps"] for v in by.values())
    errors = sum(bool(r["response"].get("error")) for r in rows)
    esc = sum(decision(r) == "ESCALATE" for r in rows)

    L = ["# Lucy final Spicy exam — every scenario ever asked", "",
         f"_Muse Spicy only (HC_BACKEND=muse, HC_VARIANT=spicy), {len(P)} unique scenarios × {data['reps']} runs "
         f"through `compose()`, now_et {data['now_et']}. Sets: baseline (B, 20), hard (H, 20), fresh (F, 23), closing "
         f"(C/N, 14 — 11 are exact repeats, kept once). One grader (spicy_exam.py): PASS = correct answer + right "
         f"closing behavior; never fail for omitting a detail the customer didn't ask for. Every check is hard / "
         f"correct / closing._", "",
         "## Totals", "", "| | Muse Spicy |", "|---|---|",
         f"| Runs passing every check | {pct(sum(r['grade']['all_pass'] for r in rows), len(rows))} |",
         f"| Scenarios 3/3 | {full}/{len(by)} |",
         f"| Runs with a HARD FAIL | {len(hard_runs)}/{len(rows)} |",
         f"| Hard-fail checks tripped | {sum(hard_checks.values())} ({', '.join(f'{k} {v}' for k, v in hard_checks.most_common()) or 'none'}) |",
         f"| Closed when it should (close class) | {pct(closed, len(close_rows))} |",
         f"| Stayed quiet when it should (quiet + photo class: no link, no scheduling question) | {pct(quiet, len(quiet_rows))} |",
         f"| Photo ask as the close (photo class) | {pct(photo, len(photo_rows))} |",
         f"| Median latency | {statistics.median(lat):.1f}s |", f"| Max latency | {max(lat):.1f}s |",
         f"| Inference errors | {errors} |", f"| Escalated to Oscar | {esc}/{len(rows)} |", ""]

    L += ["## For Oscar — decisions this run surfaced", "",
          "1. **Photo close vs rule #15 (biggest gap).** The new KB closing line says the photo-to-539 ask IS the "
          "close for any no-estimate contact, but the system prompt's rule #15 (harness.py, \"ESTIMATE ON RECORD\") "
          "still says Lucy asks for a photo ONLY when the customer's message asks about price, a quote, or getting "
          "started — \"in every other case, no photo request at all.\" Muse follows the stricter system-prompt rule, "
          "so B8 services, B10 Port Charlotte, H11 warranty, H13 deposit, H15 almond, H18 Immokalee, F6 peeling and "
          "F18 Cape Coral mostly answer without the photo ask. F16 (\"can you do it?\" = getting started) asks every "
          "time. Fix the prompt (widen rule #15) or the grader (photo ask optional when price wasn't asked) — your call; "
          "nothing was changed.",
          "2. **Two booking steps stacked** (hard fail): H19 run 3 and F9 run 2 end with the link AND \"Want me to get "
          "you on the schedule?\".",
          "3. **\"Let me reach out to the tech\"** (hard fail): F11 run 3 — escalated, but the text promises contact with "
          "the tech instead of \"Let me get Oscar on that for you.\"",
          "4. **Opt-out escalation in Spicy:** B17 sends \"we won't text you again\" + disengaged=opt_out but never "
          "escalates (0/3). The old baseline check requires escalation; Spicy makes escalation discretionary by design. "
          "Keep the check or drop it for Spicy?",
          "5. **Missing close with an estimate on record:** B12 shower tonight (0/3), H9 run 2, F23 run 1 (Spanish) — "
          "correct answer, no booking step. F17 run 1 re-sent the link after a 👍.", "",
          "**Grader corrections after the run** (no model calls; each pinned in test_spicy_exam_grader): raw score "
          "159/198 -> re-graded 165/198.",
          "- Shared hard grader promise regex: `we'?ll` matched the word \"well\" (F5 run 3: \"clean the surfaces "
          "well and fix any … faucets\" — the KB prep line). Apostrophe now required.",
          "- Spanish standard-tub regex missed the plural \"bañeras estándar\" (F23 runs 1–3; the new c wording "
          "\"most standard tubs\" made it plural).",
          "- $299 is allowed when the contact has an estimate on record and their text raises online/ad/website prices "
          "(C8 runs 1–3, Bonnie: \"considerably more than on line prices\") — the KB pricing section allows "
          "acknowledging it. $299 anywhere else is still an invented price.", ""]

    L += ["## Hard fails (full replies)", ""]
    if not hard_runs:
        L += ["- none", ""]
    for r in hard_runs:
        L += [f"**{r['key']} {r['name']}** — {', '.join(r['grade']['hard_fails'])}  ", f"Customer: {r['inbound'] or '(proactive follow-up, no inbound)'}"]
        L += run_lines(r) + [""]

    L += ["## Stage 1 — lines applied (old -> new)", "", "| Item | Old | New |", "|---|---|---|"]
    L += [f"| {i} | {o} | {n} |" for i, o, n in STAGE1]
    L += ["", "Prompt-assembly test: test_playbook_fixes (new lines in both variants; escalation wording per variant; "
          "replaced lines gone). Lines d and e are worded from your Example 1 and Oscar's Bonnie texts (I didn't "
          "have the verbatim Stage 1 d/e text). b removes \"first responders\" from the 10% line and h makes caulk "
          "replacement Gold-and-above (it was \"included\" on every job) — both change earlier KB facts, as asked.", ""]

    L += ["## Closing class per scenario", "",
          "close = ends with ONE booking step and is sent; quiet = no booking link and no scheduling question; "
          "photo = no estimate on record, no link, photo-to-539 ask is the close; any = not graded (judgment call "
          "for Oscar).", "", "| Scenario | Class | Why (non-obvious ones) | Result |", "|---|---|---|---|"]
    for key, set_, s, _ in P:
        v = by.get(key, [])
        alias = f" (= {', '.join(X.ALIASES[key])})" if key in X.ALIASES else ""
        L.append(f"| {key} {s['name']}{alias} | {X.CLASS[key]} | {X.CLASS_WHY.get(key, '')} | "
                 f"{sum(r['grade']['all_pass'] for r in v)}/{len(v)} |")
    L += ["", "Exact repeats (same history + inbound, computed): " +
          "; ".join(f"{k} kept, {', '.join(v)} dropped" for k, v in X.ALIASES.items()) + ".",
          "Your earlier answers applied: C7 (promised follow-up) and C10 (hold Tuesday) close; C5/H8 price match "
          "hands to Oscar. Per Stage 1 b, F13/C3 \"$400 cash?\" (asks to go lower) is also hand-to-Oscar, no booking "
          "step. Hand-off passes on escalation OR \"Oscar\" in the reply, because Spicy escalation is discretionary.",
          "Checks not kept from older graders: B20 moves_toward_booking, F1/F2 booking-link checks, F8 toward_booking, "
          "F17 no_repeated_pitch, F20 booking check (the closing class replaces them); F4 says_yes / "
          "old_removed_and_replaced / no_caulk_charge_claimed (caulk is now Gold and above — replaced by "
          "caulk_is_gold_and_above).", ""]

    L += ["## Every scenario", ""]
    for key, set_, s, _ in P:
        v = by.get(key, [])
        alias = f" (also {', '.join(X.ALIASES[key])})" if key in X.ALIASES else ""
        L += [f"### {key} {s['name']}{alias}", f"**Set:** {set_} · **Class:** {X.CLASS[key]}  ",
              f"**Customer:** {s['inbound'] or '(proactive follow-up, no inbound)'}", "",
              f"**{sum(r['grade']['all_pass'] for r in v)}/{len(v)} pass**"]
        for r in v:
            L += run_lines(r)
        L.append("")
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write("\n".join(L))
    print(f"written: {OUT}  rows={len(rows)} scenarios={len(by)}")


if __name__ == "__main__":
    main()
