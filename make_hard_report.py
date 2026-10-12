#!/usr/bin/env python3
"""
make_hard_report.py — HARD_SMOKE_REPORT.md from bakeoff_results/hard_muse{,_spicy}.json.
Phone-readable: one section per scenario, one block per column, full reply for every run.

Run: py -3.14 make_hard_report.py
"""
import json
import os
from collections import Counter

from hard_scenarios import RESULTS_DIR, SCENARIOS
from make_bakeoff_report import by_scenario, choice, totals

COLUMNS = [("hard_muse", "Muse regular"), ("hard_muse_spicy", "Muse Spicy")]
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "HARD_SMOKE_REPORT.md")


def load(label):
    with open(os.path.join(RESULTS_DIR, f"{label}.json"), encoding="utf-8") as fh:
        return json.load(fh)


def decision(r):
    return "ESCALATE" if r["response"].get("send_decision") == "escalate_human" else "send"


def main():
    data = {k: by_scenario(load(k)) for k, _ in COLUMNS}
    T = {k: totals(data[k]) for k, _ in COLUMNS}
    L = ["# Lucy hard smoke — Muse regular vs Muse Spicy", "",
         "_20 hard customer texts × 3 runs per column through `compose()`, HC_BACKEND=muse, now_et "
         "2026-10-12T14:10:00-04:00. Hard rules are graded by code; escalation is shown for Oscar, not graded._",
         "", "## Totals", ""]
    esc = {k: sum(decision(r) == "ESCALATE" for v in data[k].values() for r in v) for k, _ in COLUMNS}
    for key, label in (("runs", "Runs passing every check"), ("rules", "Individual checks passed"),
                       ("scen_full", "Scenarios 3/3"), ("consistent", "Consistent across 3 runs (same pass/fail + decision)"),
                       ("median", "Median latency"), ("max", "Max latency"), ("errors", "Inference errors"),
                       ("guards", "Code guard rewrites/escalations fired")):
        L.append(f"**{label}**")
        for k, name in COLUMNS:
            L.append(f"- {name}: {T[k][key]}")
        L.append("")
    L.append("**Escalated to Oscar (report-only)**")
    for k, name in COLUMNS:
        L.append(f"- {name}: {esc[k]}/60 runs")
    L.append("")

    L += ["## Where Spicy decided differently", ""]
    diffs = []
    for s in SCENARIOS:
        g = Counter(decision(r) for r in data["hard_muse"][s["id"]])
        sp = Counter(decision(r) for r in data["hard_muse_spicy"][s["id"]])
        if g != sp:
            diffs.append(s["id"])
            fmt = lambda c: ", ".join(f"{v}× {k}" for k, v in sorted(c.items()))
            L.append(f"- **#{s['id']} {s['name']}** — regular: {fmt(g)} → spicy: {fmt(sp)}")
    if not diffs:
        L.append("- none: every scenario had the same send/escalate counts")
    L.append("")

    L.append("## Per scenario")
    for s in SCENARIOS:
        L += ["", f"### #{s['id']} {s['name']}", f"**Context:** {s['context']}  ",
              f"**Customer:** {s['inbound']}"]
        for k, name in COLUMNS:
            rows = data[k][s["id"]]
            n = sum(r["grade"]["all_pass"] for r in rows)
            L += ["", f"**{name} — {n}/3 pass** · latency {', '.join(f'{r['latency_s']:.1f}' for r in rows)}s"]
            for r in rows:
                fails = [rule + (f" ({v['note']})" if v["note"] else "")
                         for rule, v in r["grade"]["rules"].items() if not v["pass"]]
                extra = " · ".join(choice(r).split(" · ")[1:])
                L.append(f"- run {r['rep']} · **{decision(r)}**{' · ' + extra if extra else ''}: "
                         f"\"{r['response'].get('reply') or ''}\"")
                L.append(f"  - checks: {'all pass' if not fails else 'FAIL ' + '; '.join(fails)}")
                if r["response"].get("error"):
                    L.append(f"  - error: {r['response']['error']}")
    L.append("")
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write("\n".join(L))
    print(f"written: {OUT}")
    for k, name in COLUMNS:
        print(name, T[k], "escalated", esc[k])
    print("spicy decided differently:", diffs)


if __name__ == "__main__":
    main()
