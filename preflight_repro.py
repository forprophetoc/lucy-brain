#!/usr/bin/env python3
"""Today's failure, replayed through compose() with the model mocked (same pattern as
test_timed_followup.InboundPhotoScopeGuard._run). Customer WITH an estimate on record
(estimate link in history) says "I'm ready to book"; the mocked model answers with the
photo-ask opener. Run with HC_VARIANT unset, then HC_VARIANT=spicy."""
import contextlib
import io
import os
import sys
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.chdir(os.path.dirname(os.path.abspath(__file__)))

import harness
from hc_compose_service import compose

PHOTO = "Great! Just text a photo of your tub to (239) 539-4777 and I'll send you an estimate."
CLEAN = "Perfect — here are the next openings to get you booked."
EST_THREAD = [{"from": "lucy", "text": "Your estimate is ready: https://app.esticlose.com/estimate/bathtub-pros/p1",
               "ts": "2026-10-05T10:00:00-04:00"}]


def req(**extra):
    r = {"trigger": "inbound_reply", "now": "2026-10-05T18:10:00.000Z", "contact_id": "C1",
         "identity": {"first_name": "Sam"}, "inbound_text": "I'm ready to book",
         "history": EST_THREAD, "memory": {}}
    r.update(extra)
    return r


def run(variant):
    env = {"HC_BACKEND": "api"}
    if variant is not None:
        env["HC_VARIANT"] = variant
    replies = [PHOTO, CLEAN]
    calls = []

    def fake_infer(context, backend, *a, **k):
        calls.append(context)
        return harness._infer_result(action_type="suggest_message", confidence="high",
                                     suggested_customer_message=replies[len(calls) - 1],
                                     send_decision="send_now")

    with mock.patch.dict(os.environ, env, clear=False):
        if variant is None:
            os.environ.pop("HC_VARIANT", None)
        os.environ.pop("ANTHROPIC_API_KEY", None)
        with mock.patch("harness.infer", fake_infer), contextlib.redirect_stdout(io.StringIO()):
            resp = compose(req())
    print(f"HC_VARIANT={variant!r:10} infer_calls={len(calls)} send_decision={resp['send_decision']!r} "
          f"reply={resp['reply']!r}")
    return resp


r1 = run(None)
r2 = run("spicy")
# PRE-FIX expectations (Stage 2): guards ON -> revised; guards OFF (spicy) -> photo ask ships.
# POST-FIX expectations (Stage 3+): BOTH runs revise the photo ask away.
print("variant_unset_reply_is_clean:", r1["reply"] == CLEAN)
print("variant_spicy_reply_is_photo_ask:", r2["reply"] == PHOTO)
