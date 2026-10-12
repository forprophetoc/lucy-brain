#!/usr/bin/env python3
"""
f20_rerun.py — reruns fresh scenario F20 ("sorry, been crazy busy" after 3 unanswered follow-ups) through
compose() after the 2026-10-12 return-after-quiet playbook line, graded by fresh_scenarios.grade.

Run:  py -3.14 f20_rerun.py <label> [reps]      (label: f20_muse | f20_muse_spicy)
      env: HC_BACKEND=muse (+ HC_VARIANT=spicy); key read from the Midwife .env.
"""
import contextlib
import io
import json
import os
import sys
import time

import fresh_scenarios as F
from baseline_scenarios import load_keys


def run(label: str, reps: int = 3) -> dict:
    from hc_compose_service import compose
    s = F.BY_ID[20]
    req = F.build_request(s)
    rows = []
    for rep in range(1, reps + 1):
        log = io.StringIO()
        t0 = time.perf_counter()
        with contextlib.redirect_stdout(log):
            resp = compose(req)
        latency = round(time.perf_counter() - t0, 2)
        g = F.grade(s, resp)
        rows.append({"set": "fresh", "scenario": 20, "key": "F20", "name": s["name"], "rep": rep,
                     "inbound": s["inbound"], "response": resp, "latency_s": latency, "grade": g,
                     "log": [ln for ln in log.getvalue().splitlines() if "FAILED" in ln or "->" in ln]})
        mark = "PASS" if g["all_pass"] else "FAIL " + ",".join(k for k, v in g["rules"].items() if not v["pass"])
        print(f"[{label}] F20 rep{rep} {latency:>6}s {resp.get('send_decision'):<15} {mark}", flush=True)
        print(f"    {resp.get('reply')!r}", flush=True)
    out = {"label": label, "backend": os.environ.get("HC_BACKEND"), "variant": os.environ.get("HC_VARIANT") or "",
           "now_et": F.NOW_ET, "reps": reps, "rows": rows}
    path = os.path.join(F.RESULTS_DIR, f"{label}.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, ensure_ascii=False)
    print(f"written: {path}  {sum(r['grade']['all_pass'] for r in rows)}/{len(rows)} pass")
    return out


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    load_keys()
    run(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 3)
