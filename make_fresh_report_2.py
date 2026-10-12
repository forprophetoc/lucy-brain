#!/usr/bin/env python3
"""
make_fresh_report_2.py — FRESH_SMOKE_REPORT_2.md: the 2026-10-12 grader corrections (every check changed,
old -> new), the saved Fresh Smoke replies re-graded (before = grades as committed in 1bf2206, after = today's
grader; no new model calls), and the F20 reruns after the return-after-quiet playbook line.

Run: py -3.14 make_fresh_report_2.py
"""
import json
import os
import subprocess

import fresh_scenarios as F
from make_fresh_report import COLUMNS, by_key, decision, label_of, load, plan

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "FRESH_SMOKE_REPORT_2.md")
BEFORE_COMMIT = "1bf2206"
F20_RUNS = [("f20_muse", "Muse regular"), ("f20_muse_spicy", "Muse Spicy")]

CHANGES = [
    ("F1", "says_2_to_3_weeks (required) + booking_link", "booking_link_or_real_availability (link, or the KB 2–3 week "
     "lead time); no_invented_dates unchanged"),
    ("F3", "mattress_blanket_towel (required)", "dropped — customer asked only whether to remove the doors"),
    ("F4", "included (must say it's included)", "no_caulk_charge_claimed (fails only if a charge/price is attached to "
     "caulk) — customer didn't ask about cost"),
    ("F5", "dust_walls + crew_does_rest (required)", "dropped; added no_invented_prep (fails on prep items not in the "
     "KB: furniture, cabinets, turning off water, pets out, paint/tape/sand…); remove_personal_items kept"),
    ("F6", "about_5_hours (required)", "dropped; must_strip_first + not_over_old_coating kept"),
    ("F7", "custom_85 + about_a_week (required)", "dropped — customer asked what colors, not price or lead time; a "
     "wrong custom price still fails no_invented_price; kohler_white_biscuit kept"),
    ("F8", "photos_and_invoice + cash_or_card_on_completion (required)", "dropped; added no_wrong_payment_info "
     "(online, checks, deposit, upfront, Zelle/Venmo/PayPal, financing) + toward_booking (link, or a scheduling / "
     "check-back step); says_yes + no_need_to_be_home kept"),
    ("F9", "platinum_option (required)", "dropped — an upsell the customer didn't ask about; fume_extraction + "
     "no_medical_claims kept"),
    ("F10", "states_427 (required)", "total_427_if_stated (fails only if a total other than $427 appears); "
     "five_pct + not_stacked kept"),
    ("F13", "holds_449 (must restate $449)", "dropped; never_a_new_number + no_accept_400 kept"),
    ("F14", "honest_identity + apologetic (required phrasing)", "honest (fails on a human claim or on telling the "
     "customer they did ask); no_sales_push kept"),
    ("F16", "about_5_hours (required)", "dropped — customer asked only whether we do jacuzzi tubs"),
    ("F20", "toward_booking (link, or any mention of book/schedule)", "booking_link_or_sched_question (the link, or a "
     "direct scheduling question ending in '?'); warm, no_guilt, no_pressure kept"),
    ("F21–F23", "holds_estimate (must restate $649)", "dropped; standard_vs_combo, no_discount_no_new_number, "
     "not_defensive, no_bait_echo, nothing_invented_why kept"),
]
UNCHANGED_NOTES = [
    "Hard-rule checks (hard_scenarios.hard_checks: invented price/policy/years/service, banned words, fault, "
    "refund/repair promise, human claim, internal tools, times, 320 chars, intro, payment, title) — unchanged.",
    "Kept as \"must mention\" because the customer asked: F2 booking_link (asked for a day), F3 customer_removes_doors, "
    "F4 says_yes/old_removed_and_replaced (asked about caulk), F5 remove_personal_items (asked about prep), F7 "
    "kohler_white_biscuit, F8 no_need_to_be_home, F9 fume_extraction (asked if it's toxic), F10 five_pct, F15 "
    "full_day (asked how long), F16/F18 says_yes, F21–F23 standard_vs_combo (asked why).",
    "Kept as tone/playbook rules (not a detail): F11 apologizes + escalates, F12 not-held/no pressure, F17 brief/no "
    "repeated pitch, F19 empathy first/zero pressure, F20 warm/no guilt.",
    "Hard reruns H7–H15 are graded by hard_scenarios.grade, which this amendment did not change (all 36 runs already "
    "passed).",
]


def committed(label):
    raw = subprocess.check_output(["git", "show", f"{BEFORE_COMMIT}:bakeoff_results/{label}.json"], cwd=HERE)
    return json.loads(raw.decode("utf-8"))


def npass(rows):
    return sum(r["grade"]["all_pass"] for r in rows)


def run_lines(r):
    fails = [k + (f" ({v['note']})" if v["note"] else "") for k, v in r["grade"]["rules"].items() if not v["pass"]]
    return [f"- run {r['rep']} · **{decision(r)}** · {r['latency_s']:.1f}s: \"{r['response'].get('reply') or ''}\"",
            f"  - checks ({len(r['grade']['rules'])}): {'all pass' if not fails else 'FAIL ' + '; '.join(fails)}"]


def main():
    now = {c: by_key(load(c)) for c, _ in COLUMNS}
    before = {c: by_key(committed(c)) for c, _ in COLUMNS}
    f20 = {c: load(c)["rows"] for c, _ in F20_RUNS}
    P = plan()
    L = ["# Lucy fresh smoke 2 — grader corrections + F20 fix", "",
         f"_Muse only, regular vs Spicy. Stage 1 re-grades the saved Fresh Smoke replies (commit {BEFORE_COMMIT}) "
         "with the corrected grader — no new model calls. Stage 2 adds the return-after-quiet playbook line and "
         f"reruns F20 ×3 per column through `compose()` (HC_BACKEND=muse, now_et {F.NOW_ET}). Grading principle "
         "(Oscar): a reply passes if it answers the customer correctly and moves toward booking; it never fails "
         "for leaving out a detail the customer didn't ask for._", "",
         "## Totals", "", "| | Muse regular | Muse Spicy |", "|---|---|---|"]
    cells = lambda f: " | ".join(f(c) for c, _ in COLUMNS)
    tot = lambda d, c: f"{sum(npass(v) for v in d[c].values())}/{sum(len(v) for v in d[c].values())}"
    L.append(f"| Saved runs, old grader | {cells(lambda c: tot(before, c))} |")
    L.append(f"| Saved runs, corrected grader | {cells(lambda c: tot(now, c))} |")
    full = lambda c: f"{sum(npass(v) == len(v) for v in now[c].values())}/{len(now[c])}"
    L.append(f"| Scenarios 3/3, corrected grader | {cells(full)} |")
    f20cell = {c2: f"{npass(f20[c2])}/{len(f20[c2])}" for c2, _ in F20_RUNS}
    L.append(f"| F20 rerun after playbook fix | {f20cell['f20_muse']} | {f20cell['f20_muse_spicy']} |")

    def with_f20(c, c2):
        rows = [r for k, v in now[c].items() if k != "F20" for r in v] + f20[c2]
        return f"{npass(rows)}/{len(rows)}"
    L.append(f"| All 29 with F20 rerun swapped in | {with_f20('fresh_muse', 'f20_muse')} | "
             f"{with_f20('fresh_muse_spicy', 'f20_muse_spicy')} |")
    L += ["", "Caveat: only F20 was rerun with the new playbook line. The other 28 scenarios are the saved replies "
          "from before it, so the last row combines runs from before and after the change. A full 29-scenario "
          "rerun would show whether the new line changes any other reply (e.g. F17 👍, F19 widow, F12 defer).", ""]

    L += ["## Stage 1 — every check changed (old -> new)", "", "| Scenario | Old | New |", "|---|---|---|"]
    L += [f"| {s} | {o} | {n} |" for s, o, n in CHANGES]
    L += ["", "Not changed:", ""] + [f"- {n}" for n in UNCHANGED_NOTES] + [""]

    L += ["## Per scenario — re-graded saved runs", "",
          "| Scenario | Regular old | Regular new | Spicy old | Spicy new |", "|---|---|---|---|---|"]
    for k, set_, s in P:
        row = []
        for c, _ in COLUMNS:
            row += [f"{npass(before[c].get(k, []))}/{len(before[c].get(k, []))}",
                    f"{npass(now[c].get(k, []))}/{len(now[c].get(k, []))}"]
        L.append(f"| {label_of(k, s)} | " + " | ".join(row) + " |")
    L.append("")

    L += ["## Still failing after re-grade (saved runs)", ""]
    for c, name in COLUMNS:
        for k, set_, s in P:
            for r in now[c].get(k, []):
                if not r["grade"]["all_pass"]:
                    L += [f"**{name} · {label_of(k, s)}**"] + run_lines(r) + [""]
    L += ["F20 (all 6 saved runs) is the gap Stage 2 fixes. Spicy F14 run 3 says \"I'm Lucy with Bathtub Pros in "
          "Naples\" mid-thread (hard intro rule). Spicy F17 run 1 re-sends the booking link after a 👍.", ""]

    L += ["## Stage 2 — F20 fix", "",
          "Playbook line added to lucy-kb.md (PLAYBOOK, both variants — the spicy variant edits the same system "
          "prompt):", "",
          "> When a customer comes back after going quiet (\"sorry, been busy\", \"still interested\", any reply "
          "after unanswered follow-ups), reply warm and short — no guilt, never mention the texts they missed — "
          "then take ONE direct booking step: the booking link (https://calendar.bathtubpros.com) or a direct "
          "scheduling question (\"want me to get you on the schedule?\"). Never just \"here when you're ready.\"", "",
          "Prompt-assembly test: test_playbook_fixes `h_return_after_quiet` asserts the line is in the assembled "
          "system prompt for regular and HC_VARIANT=spicy — passes.", "",
          f"**Customer:** {F.BY_ID[20]['inbound']}  ", f"**Context:** {F.BY_ID[20]['context']}", ""]
    for c2, name in F20_RUNS:
        rows = f20[c2]
        L += [f"**{name} — {npass(rows)}/{len(rows)} pass** · latency "
              f"{', '.join(f'{r['latency_s']:.1f}' for r in rows)}s"]
        for r in rows:
            L += run_lines(r)
        L.append("")
    L += ["Every F20 reply uses both the scheduling question and the link in one text. Oscar to say whether that "
          "counts as \"ONE booking step\"; the grader accepts it.", ""]

    L += ["## Every saved run, re-graded", ""]
    for k, set_, s in P:
        L += [f"### {label_of(k, s)}", f"**Context:** {s['context']}  ", f"**Customer:** {s['inbound']}", ""]
        for c, name in COLUMNS:
            rows = now[c].get(k, [])
            L.append(f"**{name} — {npass(rows)}/{len(rows)} pass**")
            for r in rows:
                L += run_lines(r)
            L.append("")
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write("\n".join(L))
    print(f"written: {OUT}")


if __name__ == "__main__":
    main()
