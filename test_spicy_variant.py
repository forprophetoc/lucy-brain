"""
Spicy-variant unit tests (no network, no model). HC_VARIANT=spicy returns the model's raw reply
with no guard calls; HC_VARIANT unset is normal Lucy, unchanged.

Run: python -m unittest -v test_spicy_variant
"""
import contextlib
import io
import os
import unittest
from unittest import mock

import harness
from hc_compose_service import compose

GUARDS = ("enforce_inbound_timing", "enforce_no_proactive_photo", "enforce_inbound_photo_scope",
          "enforce_text_cap", "_revise_reply")
RAW = ("Text a photo of your tub to (239) 539-4777 so we can quote it! " + "x" * 400)


def _req(trigger="due_date_sweep", inbound=""):
    return {"trigger": trigger, "now_et": "2026-10-12T14:10:00-04:00", "contact_id": "C1",
            "identity": {"first_name": "Sam"}, "inbound_text": inbound,
            "history": [{"from": "lucy", "text": "Your estimate is $449.", "ts": "2026-10-08T10:00:00-04:00"}]}


def _fake_infer(reply, **extra):
    def f(context, backend, *a, **k):
        base = dict(action_type="suggest_message", confidence="high",
                    suggested_customer_message=reply, send_decision="send_now")
        base.update(extra)
        return harness._infer_result(**base)
    return f


class SpicyGuardBypass(unittest.TestCase):
    def _run(self, variant, req, infer):
        env = {"HC_BACKEND": "muse"}
        if variant:
            env["HC_VARIANT"] = variant
        patches = {g: mock.patch(f"harness.{g}", wraps=getattr(harness, g)) for g in GUARDS}
        with mock.patch.dict(os.environ, env), mock.patch("harness.infer", infer), \
                contextlib.ExitStack() as st, contextlib.redirect_stdout(io.StringIO()):
            os.environ.pop("RENDER", None)
            if not variant:
                os.environ.pop("HC_VARIANT", None)
            mocks = {g: st.enter_context(p) for g, p in patches.items()}
            resp = compose(req)
        return resp, mocks

    def test_spicy_returns_raw_reply_no_guard_calls(self):
        for trig, inbound in (("due_date_sweep", ""), ("inbound_reply", "What's my price?")):
            with self.subTest(trigger=trig):
                resp, mocks = self._run(" spicy ", _req(trig, inbound), _fake_infer(RAW))
                self.assertEqual(resp["reply"], RAW.strip())  # photo ask + >320 chars, untouched
                self.assertEqual(resp["send_decision"], "send_now")
                for g, m in mocks.items():
                    self.assertEqual(m.call_count, 0, f"{g} called under spicy")

    def test_spicy_keeps_model_escalation_decision(self):
        resp, _ = self._run("spicy", _req("inbound_reply", "Call me"),
                            _fake_infer("I'll have Oscar call you.", escalate_oscar=True))
        self.assertEqual(resp["send_decision"], "escalate_human")

    def test_normal_path_runs_guards(self):
        resp, mocks = self._run("", _req(), _fake_infer(RAW))
        self.assertEqual(resp["send_decision"], "escalate_human")  # retries return the same -> escalate
        for g in ("enforce_no_proactive_photo", "enforce_inbound_photo_scope", "enforce_text_cap"):
            self.assertEqual(mocks[g].call_count, 1, g)
        self.assertGreaterEqual(mocks["_revise_reply"].call_count, 1)

    def test_spicy_ignored_on_render(self):
        with mock.patch.dict(os.environ, {"HC_VARIANT": "spicy", "RENDER": "true"}), \
                contextlib.redirect_stdout(io.StringIO()):
            self.assertFalse(harness.spicy_variant())
            self.assertEqual(harness._prompts(), (harness.SYSTEM_PROMPT, harness.OUTPUT_INSTRUCTION))

    def test_service_refuses_to_boot_with_variant(self):
        src = open("hc_compose_service.py", encoding="utf-8").read()
        self.assertIn('if (os.environ.get("HC_VARIANT") or "").strip():\n        raise SystemExit', src)


class SpicyPromptText(unittest.TestCase):
    def _spicy(self):
        with mock.patch.dict(os.environ, {"HC_VARIANT": "spicy"}):
            os.environ.pop("RENDER", None)
            return harness._prompts()

    def test_normal_prompts_are_the_originals(self):
        with mock.patch.dict(os.environ, {}):
            os.environ.pop("HC_VARIANT", None)
            system, instr = harness._prompts()
        self.assertIs(system, harness.SYSTEM_PROMPT)
        self.assertIs(instr, harness.OUTPUT_INSTRUCTION)

    def test_every_edit_applied_and_nothing_else(self):
        system, instr = self._spicy()
        for old, new in harness.SPICY_EDITS:
            self.assertNotIn(old, system)
            self.assertIn(new, system)
        for old, new in harness.SPICY_OUTPUT_EDITS:
            self.assertNotIn(old, instr)
            self.assertIn(new, instr)
        # Reverting each edit restores the normal text byte-for-byte: nothing else changed.
        for old, new in harness.SPICY_EDITS:
            system = system.replace(new, old, 1)
        for old, new in harness.SPICY_OUTPUT_EDITS:
            instr = instr.replace(new, old, 1)
        self.assertEqual(system, harness.SYSTEM_PROMPT)
        self.assertEqual(instr, harness.OUTPUT_INSTRUCTION)

    def test_no_mandated_escalation_left(self):
        system, instr = self._spicy()
        for phrase in ("set\nescalate_oscar=true", "keep escalate_oscar=true", "Hand to Oscar",
                       "ONLY for:", "-> forward to Oscar", "escalate to Oscar. ", "real person: escalate_oscar=true"):
            self.assertNotIn(phrase, system + instr, phrase)
        self.assertIn("escalate_oscar", system)  # escalate stays an available decision
        self.assertIn(harness.SPICY_MAY_ESCALATE, system)

    def test_spicy_prompt_reaches_muse_request(self):
        import json
        from test_muse_backend import CTX, GOOD, _drive
        with mock.patch.dict(os.environ, {"HC_VARIANT": "spicy"}):
            os.environ.pop("RENDER", None)
            _, calls, _ = _drive(harness._infer_muse, json.dumps(GOOD))
        body = json.loads(calls[0][0].data.decode("utf-8"))
        self.assertEqual(body["messages"][0]["content"], self._spicy()[0])


if __name__ == "__main__":
    unittest.main()
