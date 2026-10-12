#!/usr/bin/env python3
"""
make_fresh_report.py — FRESH_SMOKE_REPORT.md from bakeoff_results/fresh_muse{,_spicy}.json.
Two columns (Muse regular | Muse Spicy): totals table, per-scenario summary table, a "fixed?" section
for the 6 hard-smoke reruns (vs the saved hard_muse{,_spicy} runs), every scenario where Spicy decided
differently, then the full reply, decision, checks and latency for every run.

Run: py -3.14 make_fresh_report.py
"""
import json
import os
from collections import Counter

import fresh_scenarios as F
import hard_scenarios as H
from make_bakeoff_report import choice, totals

COLUMNS = [("fresh_muse", "Muse regular"), ("fresh_muse_spicy", "Muse Spicy")]
PRIOR = {"fresh_muse": "hard_muse", "fresh_muse_spicy": "hard_muse_spicy"}
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "FRESH_SMOKE_REPORT.md")
# The checks each rerun scenario was brought back to prove (2026-10-11 fixes).
FIX_CHECKS = {
    7: ["intro_only_first_message"],
    10: ["cant_speak_to_other_customer", "no_other_crews_framing", "no_confirm_deny_199", "states_449"],
    11: ["no_yes_to_lifetime", "no_free_guarantee_lifetime"],
    13: ["cash_or_card_on_completion", "no_online_or_check_payment"],
    14: ["no_spray_with_infant", "no_recommend_infant", "no_dogs_outside", "dogs_fine"],
    15: ["states_85", "about_a_week", "custom_color"],
}


def load(label):
    with open(os.path.join(F.RESULTS_DIR, f"{label}.json"), encoding="utf-8") as fh:
        return json.load(fh)


def by_key(data):
    out = {}
    for r in data["rows"]:
        out.setdefault(r["key"], []).append(r)
    return out


def decision(r):
    return "ESCALATE" if r["response"].get("send_decision") == "escalate_human" else "send"


def fmt(c):
    return ", ".join(f"{v}× {k}" for k, v in sorted(c.items()))


def plan():
    return [(F.key(set_, s["id"]), set_, s) for set_, s, _, _ in F.cases()]


def label_of(k, s):
    return f"{k} {s['name']}" if k.startswith("F") else f"{k} (hard rerun) {s['name']}"


def main():
    data = {k: by_key(load(k)) for k, _ in COLUMNS}
    T = {k: totals(data[k]) for k, _ in COLUMNS}
    P = plan()
    n_rows = {k: sum(len(v) for v in data[k].values()) for k, _ in COLUMNS}
    esc = {k: sum(decision(r) == "ESCALATE" for v in data[k].values() for r in v) for k, _ in COLUMNS}
    L = ["# Lucy fresh smoke — Muse regular vs Muse Spicy", "",
         f"_23 fresh scenarios + 6 hard-smoke reruns (#7, #10, #11, #13, #14, #15) × 3 runs per column through "
         f"`compose()`, HC_BACKEND=muse, now_et {F.NOW_ET}. Hard rules graded by code. F = fresh, H = hard rerun. "
         f"Combo estimate for F21–F23 is ${F.COMBO_PRICE}._", "",
         "## Totals", "", "| | Muse regular | Muse Spicy |", "|---|---|---|"]
    for key, name in (("runs", "Runs passing every check"), ("rules", "Individual checks passed"),
                      ("scen_full", "Scenarios 3/3"), ("consistent", "Consistent across 3 runs"),
                      ("median", "Median latency"), ("max", "Max latency"), ("errors", "Inference errors")):
        L.append(f"| {name} | {T['fresh_muse'][key]} | {T['fresh_muse_spicy'][key]} |")
    L.append(f"| Escalated to Oscar | {esc['fresh_muse']}/{n_rows['fresh_muse']} | "
             f"{esc['fresh_muse_spicy']}/{n_rows['fresh_muse_spicy']} |")
    for set_, name in (("F", "Fresh only (23)"), ("H", "Hard reruns only (6)")):
        cells = []
        for k, _ in COLUMNS:
            rows = [r for kk, v in data[k].items() if kk.startswith(set_) for r in v]
            cells.append(f"{sum(r['grade']['all_pass'] for r in rows)}/{len(rows)}")
        L.append(f"| {name} runs passing | {cells[0]} | {cells[1]} |")
    L += ["", f"Code guard rewrites (regular): {T['fresh_muse']['guards']}", ""]

    L += ["## Per scenario summary", "", "| Scenario | Regular | Spicy | Regular decided | Spicy decided |",
          "|---|---|---|---|---|"]
    for k, set_, s in P:
        cells = []
        for col, _ in COLUMNS:
            rows = data[col].get(k, [])
            cells.append(f"{sum(r['grade']['all_pass'] for r in rows)}/{len(rows)}")
        decs = [fmt(Counter(decision(r) for r in data[col].get(k, []))) for col, _ in COLUMNS]
        L.append(f"| {label_of(k, s)} | {cells[0]} | {cells[1]} | {decs[0]} | {decs[1]} |")
    L.append("")

    L += ["## Fixed? — the 6 hard-smoke reruns", "",
          "_Before = the saved hard-smoke runs (commit 4769711), re-graded with today's grader; after = this run._", ""]
    for col, name in COLUMNS:
        prior = {}
        for r in load(PRIOR[col])["rows"]:
            prior.setdefault(r["scenario"], []).append(r)
        L += [f"**{name}**", "", "| Scenario | Before | After | Fix checks after | Fixed? |", "|---|---|---|---|---|"]
        for sid in F.RERUN_HARD:
            before = [H.grade(H.BY_ID[sid], r["response"]) for r in prior.get(sid, [])]
            after = data[col].get(f"H{sid}", [])
            b = sum(g["all_pass"] for g in before)
            a = sum(r["grade"]["all_pass"] for r in after)
            fc = []
            for chk in FIX_CHECKS[sid]:
                n = sum(r["grade"]["rules"].get(chk, {}).get("pass", False) for r in after)
                fc.append(f"{chk} {n}/{len(after)}")
            fixed = "yes" if a == len(after) else ("partly" if a > b else "no")
            L.append(f"| H{sid} {H.BY_ID[sid]['name']} | {b}/{len(before)} | {a}/{len(after)} | {'; '.join(fc)} | {fixed} |")
        L.append("")

    L += ["## Where Spicy decided differently", ""]
    diffs = []
    for k, set_, s in P:
        g = Counter(decision(r) for r in data["fresh_muse"].get(k, []))
        sp = Counter(decision(r) for r in data["fresh_muse_spicy"].get(k, []))
        if g != sp:
            diffs.append(k)
            L.append(f"- **{label_of(k, s)}** — regular: {fmt(g)} → spicy: {fmt(sp)}")
    if not diffs:
        L.append("- none: every scenario had the same send/escalate counts")
    L.append("")

    L += ["## Notes", "",
          "- Grader fixes made after the runs, for false negatives only (each pinned in test_fresh_grader): F3 "
          "\"before **we** arrive, remove the doors\" and \"we remove the caulking\" were being read as \"we remove "
          "the doors\"; F6 accepts \"the failed coating has to be **removed** first\" as the strip step. Saved "
          "replies were re-graded; no model calls repeated.",
          "- F5 misses \"crew does the rest\" in 6/6 runs: the model quotes the older AUTO \"appointment prep\" KB "
          "line (water, power, AC, faucets) instead of the PLAYBOOK prep line. The two lines overlap; Oscar to "
          "decide whether to merge them.",
          "- F14 replies use the KB wrong-number script (\"Oh, that's strange! We just received a request from "
          "this number\"). Failures are a missing apology or identity, or \"I'm Lucy with Bathtub Pros\" mid-thread "
          "(the only mid-thread intro allowed is \"I'm Lucy, Oscar's online assistant\").",
          "- F7's text \"What colors do you have?\" (architect's wording) also appears in hard #12's history.",
          "- Hard grader: caulk sentences no longer count as a refund/repair promise (an included service).", ""]
    L.append("## Every run")
    for k, set_, s in P:
        L += ["", f"### {label_of(k, s)}", f"**Context:** {s['context']}  ", f"**Customer:** {s['inbound']}"]
        for col, name in COLUMNS:
            rows = data[col].get(k, [])
            n = sum(r["grade"]["all_pass"] for r in rows)
            L += ["", f"**{name} — {n}/{len(rows)} pass** · latency {', '.join(f'{r['latency_s']:.1f}' for r in rows)}s"]
            for r in rows:
                fails = [rule + (f" ({v['note']})" if v["note"] else "")
                         for rule, v in r["grade"]["rules"].items() if not v["pass"]]
                extra = " · ".join(choice(r).split(" · ")[1:])
                L.append(f"- run {r['rep']} · **{decision(r)}**{' · ' + extra if extra else ''} · "
                         f"{r['latency_s']:.1f}s: \"{r['response'].get('reply') or ''}\"")
                L.append(f"  - checks ({len(r['grade']['rules'])}): "
                         f"{'all pass' if not fails else 'FAIL ' + '; '.join(fails)}")
                if r["response"].get("error"):
                    L.append(f"  - error: {r['response']['error']}")
    L.append("")
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write("\n".join(L))
    print(f"written: {OUT}")
    for k, name in COLUMNS:
        print(name, T[k], "escalated", esc[k], "rows", n_rows[k], "scenarios", len(data[k]))
    print("spicy decided differently:", diffs)


if __name__ == "__main__":
    main()
