"""audit.py — shared, crash-proof, append-only result log for the control runners.

Both controls.py (checker) and controls_live.py (live runner) write ONE JSON line
per control AS the result is produced, before any printing, and flush immediately.
A render/encoding crash afterward can never lose the trail. The on-screen reports
READ BACK from this log, so what you see on screen == what is on disk.

Row schema (per control):
  run_id, event="control", at (ISO), ts (epoch),
  control_id, contact_id, send_decision, sent_live, message (VERBATIM), result
  ("PASS"/"FAIL"), error, plus any extra fields a runner wants (gate_reasons, etc.)

History is preserved (append-only). Reports show only the latest run via run_id.
"""
import json
import time
from datetime import datetime


def new_run_id():
    return datetime.now().strftime("%Y%m%dT%H%M%S")


def log_row(path, **fields):
    fields.setdefault("ts", time.time())
    fields.setdefault("at", datetime.now().isoformat(timespec="seconds"))
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(fields, ensure_ascii=False) + "\n")
        f.flush()


def read_rows(path):
    rows = []
    try:
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        rows.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
    except FileNotFoundError:
        return []
    return rows


def latest_run_id(path):
    ids = [r.get("run_id") for r in read_rows(path) if r.get("run_id")]
    return ids[-1] if ids else None


def latest_control_rows(path):
    """Control rows from the most recent run only (what a report should show)."""
    run_id = latest_run_id(path)
    if run_id is None:
        return []
    return [r for r in read_rows(path)
            if r.get("run_id") == run_id and r.get("event") == "control"]
