#!/usr/bin/env python3
"""
make_bakeoff_report.py — BAKEOFF_REPORT.md from bakeoff_results/{deepseek,muse,muse_spicy}.json.
Phone-readable: one section per scenario, one block per column, no wide tables.

Run: py -3.14 make_bakeoff_report.py
"""
import json
import os
import statistics
from collections import Counter

from baseline_scenarios import RESULTS_DIR, SCENARIOS

COLUMNS = [("deepseek", "DeepSeek (guarded)"), ("muse", "Muse (guarded)"), ("muse_spicy", "Muse Spicy")]
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "BAKEOFF_REPORT.md")


def load(label):
    with open(os.path.join(RESULTS_DIR, f"{label}.json"), encoding="utf-8") as fh:
        return json.load(fh)


def by_scenario(data):
    out = {}
    for r in data["rows"]:
        out.setdefault(r["scenario"], []).append(r)
    return out


def choice(r):
    """What the brain decided: send/escalate plus the scheduling/disengagement signals."""
    resp = r["response"]
    facts = resp.get("facts") or {}
    parts = [resp.get("send_decision") or "-"]
    if resp.get("followup_at"):
        parts.append(f"followup_at={resp['followup_at']}")
    if facts.get("followup_date"):
        parts.append(f"followup_date={facts['followup_date']}")
    if facts.get("disengaged"):
        parts.append(f"disengaged={facts['disengaged']}")
    return " · ".join(parts)


def majority(values):
    return Counter(values).most_common(1)[0][0]


def totals(rows_by):
    rows = [r for v in rows_by.values() for r in v]
    lat = [r["latency_s"] for r in rows]
    rule_n = sum(len(r["grade"]["rules"]) for r in rows)
    rule_p = sum(v["pass"] for r in rows for v in r["grade"]["rules"].values())
    consistent = sum(1 for v in rows_by.values()
                     if len({r["grade"]["all_pass"] for r in v}) == 1 and len({choice(r) for r in v}) == 1)
    identical = sum(1 for v in rows_by.values() if len({r["response"]["reply"] for r in v}) == 1)
    full = sum(1 for v in rows_by.values() if all(r["grade"]["all_pass"] for r in v))
    errors = sum(1 for r in rows if r["response"].get("error"))
    return {
        "runs": f"{sum(r['grade']['all_pass'] for r in rows)}/{len(rows)}",
        "runs_pct": 100 * sum(r["grade"]["all_pass"] for r in rows) / len(rows),
        "rules": f"{rule_p}/{rule_n} ({100 * rule_p / rule_n:.1f}%)",
        "scen_full": f"{full}/{len(rows_by)}",
        "consistent": f"{consistent}/{len(rows_by)}",
        "identical": f"{identical}/{len(rows_by)}",
        "median": f"{statistics.median(lat):.1f}s",
        "max": f"{max(lat):.1f}s",
        "errors": errors,
        "guards": "; ".join(f"#{r['scenario']} run {r['rep']}: {ln.replace('[HC] ', '')}"
                            for r in rows for ln in r.get("log") or [] if "->" in ln) or "none",
    }


def main():
    data = {k: by_scenario(load(k)) for k, _ in COLUMNS}
    L = ["# Lucy bake-off — DeepSeek vs Muse vs Muse Spicy", ""]
    L.append(f"_20 scenarios × 3 runs per column through `compose()` (production path), now_et "
             f"2026-10-12T14:10:00-04:00. Grader measures hard rules only; it never blocks or rewrites._")
    L.append("")
    L.append("## Totals")
    L.append("")
    T = {k: totals(data[k]) for k, _ in COLUMNS}
    for key, label in (("runs", "Runs passing every hard rule"), ("rules", "Individual rule checks passed"),
                       ("scen_full", "Scenarios 3/3"), ("consistent", "Consistent across 3 runs (same pass/fail + decision)"),
                       ("identical", "Byte-identical reply all 3 runs"), ("median", "Median latency"),
                       ("max", "Max latency"), ("errors", "Inference errors"),
                       ("guards", "Code guard rewrites/escalations fired (spicy has none by design)")):
        L.append(f"**{label}**")
        for k, name in COLUMNS:
            L.append(f"- {name}: {T[k][key]}")
        L.append("")

    # Spicy vs guarded Muse: scenarios where the majority decision differs.
    L.append("## Where Spicy chose differently from guarded Muse")
    L.append("")
    diffs = []
    for s in SCENARIOS:
        g = data["muse"][s["id"]]
        sp = data["muse_spicy"][s["id"]]
        gc = Counter(choice(r) for r in g)
        sc = Counter(choice(r) for r in sp)
        if gc != sc:
            diffs.append(s["id"])
            L.append(f"- **#{s['id']} {s['name']}** — guarded: {dict(gc)} → spicy: {dict(sc)}")
    if not diffs:
        L.append("- none: every scenario had the same decision counts")
    L.append("")

    L.append("## Per scenario")
    for s in SCENARIOS:
        L.append("")
        L.append(f"### #{s['id']} {s['name']}")
        L.append(f"**Customer:** {s['inbound'] or '_(proactive sweep, no inbound)_'}  ")
        L.append(f"**Estimate on record:** {'$' + str(s['estimate']) if s['estimate'] else 'none'}")
        for k, name in COLUMNS:
            rows = data[k][s["id"]]
            n_pass = sum(r["grade"]["all_pass"] for r in rows)
            lats = ", ".join(f"{r['latency_s']:.1f}" for r in rows)
            L.append("")
            L.append(f"**{name} — {n_pass}/3 pass** · latency {lats}s")
            seen = {}
            for r in rows:
                seen.setdefault((r["response"]["reply"], choice(r)), []).append(r)
            for (reply, ch), rs in seen.items():
                reps = ",".join(str(r["rep"]) for r in rs)
                fails = sorted({f"{rule}" + (f" ({v['note']})" if v["note"] else "")
                                for r in rs for rule, v in r["grade"]["rules"].items() if not v["pass"]})
                L.append(f"- run {reps}: \"{reply}\"")
                L.append(f"  - decision: {ch}")
                L.append(f"  - rules: {'all pass' if not fails else 'FAIL ' + '; '.join(fails)}")
                err = rs[0]["response"].get("error")
                if err:
                    L.append(f"  - error: {err}")
    L.append("")
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write("\n".join(L))
    print(f"written: {OUT}")
    for k, name in COLUMNS:
        print(name, T[k])
    print("spicy differs:", diffs)


if __name__ == "__main__":
    main()
