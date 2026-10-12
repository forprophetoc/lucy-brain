"""
Muse backend unit tests (no network): HC_BACKEND=muse with urllib.request.urlopen mocked.
Request shape, auth, parse, and every failure path (timeout/401/402/429/5xx/bad JSON) — each
failure takes the same result as the deepseek backend and logs one "[HC] infer FAILED backend=muse".

Run: python -m unittest -v test_muse_backend
"""
import contextlib
import io
import json
import os
import unittest
import urllib.error
from unittest import mock

import harness
from hc_compose_service import compose, _active_model

GOOD = {"action_type": "suggest_message", "confidence": "high", "message_to_oscar": "note",
        "rationale": "why", "evidence": ["e"], "suggested_customer_message": "You got it, Sam!",
        "estimate_readiness": None, "send_decision": "send_now", "language": "en",
        "memory_facts_used": [], "escalate_oscar": False, "escalation_reason": "",
        "followup_date": "", "first_name": "", "scope": "", "disengaged": "",
        "followup_at": "2026-10-13T14:00:00-04:00"}
CTX = {"local_time": {"now_et": "2026-10-12T14:10:00-04:00"},
       "current_event": {"event_type": "inbound_reply", "inbound_text": "text me tomorrow at 2"}}


class _HttpResp:
    def __init__(self, payload):
        self._b = json.dumps(payload).encode("utf-8")

    def read(self):
        return self._b

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def _payload(content):
    return {"id": "chatcmpl-1", "object": "chat.completion", "model": "muse-spark-1.3",
            "choices": [{"index": 0, "message": {"role": "assistant", "content": content},
                         "finish_reason": "stop"}],
            "usage": {"prompt_tokens": 12, "completion_tokens": 7, "total_tokens": 19}}


def _http_err(url, code, body):
    return urllib.error.HTTPError(url, code, "err", {}, io.BytesIO(body.encode("utf-8")))


def _drive(fn, *effects):
    """Run fn(CTX, key) with urlopen mocked to the given effects; returns (out, calls, log)."""
    calls = []

    def fake_urlopen(req, timeout=None):
        calls.append((req, timeout))
        eff = effects[min(len(calls), len(effects)) - 1]
        if isinstance(eff, BaseException):
            raise eff
        return _HttpResp(_payload(eff))

    buf = io.StringIO()
    with mock.patch("urllib.request.urlopen", fake_urlopen), contextlib.redirect_stdout(buf):
        out = fn(CTX, "sk-muse-test-key")
    return out, calls, buf.getvalue()


class MuseRequest(unittest.TestCase):
    def test_request_shape_and_auth(self):
        _, calls, _ = _drive(harness._infer_muse, json.dumps(GOOD))
        req, timeout = calls[0]
        self.assertEqual(req.full_url, "https://api.meta.ai/v1/chat/completions")
        self.assertEqual(req.get_method(), "POST")
        self.assertEqual(req.get_header("Authorization"), "Bearer sk-muse-test-key")
        self.assertEqual(req.get_header("Content-type"), "application/json")
        self.assertEqual(timeout, harness.BRAIN_TIMEOUT_SECONDS)
        body = json.loads(req.data.decode("utf-8"))
        self.assertEqual(body["model"], "muse-spark-1.3")
        self.assertNotIn("contributor", body["model"])
        self.assertEqual(body["temperature"], 0)
        self.assertEqual(body["reasoning_effort"], "minimal")
        self.assertFalse(body["stream"])
        rf = body["response_format"]
        self.assertEqual(rf["type"], "json_schema")
        self.assertTrue(rf["json_schema"]["strict"])
        schema = rf["json_schema"]["schema"]
        self.assertFalse(schema["additionalProperties"])
        self.assertEqual(set(schema["required"]), set(schema["properties"]))
        self.assertEqual(set(schema["properties"]), set(GOOD))

    def test_same_prompt_as_deepseek(self):
        _, mcalls, _ = _drive(harness._infer_muse, json.dumps(GOOD))
        _, dcalls, _ = _drive(harness._infer_deepseek, json.dumps(GOOD))
        mb = json.loads(mcalls[0][0].data.decode("utf-8"))
        db = json.loads(dcalls[0][0].data.decode("utf-8"))
        self.assertEqual(mb["messages"], db["messages"])

    def test_schema_accepts_every_output_instruction_key(self):
        for key in harness.OUTPUT_INSTRUCTION.split("EXACTLY these keys: ")[1].split(". ")[0].split(", "):
            self.assertIn(key, harness.MUSE_OUTPUT_SCHEMA["properties"])


class MuseParse(unittest.TestCase):
    def test_valid_json_parses_same_as_deepseek(self):
        mu, _, log = _drive(harness._infer_muse, json.dumps(GOOD))
        ds, _, _ = _drive(harness._infer_deepseek, json.dumps(GOOD))
        self.assertEqual(mu, ds)
        self.assertEqual(mu["error"], "")
        self.assertEqual(mu["followup_at"], "2026-10-13T14:00:00-04:00")
        self.assertEqual(mu["usage"], {"input_tokens": 12, "output_tokens": 7})
        self.assertNotIn("FAILED", log)

    def test_fenced_json_parses(self):
        mu, _, _ = _drive(harness._infer_muse, "```json\n" + json.dumps(GOOD) + "\n```")
        self.assertEqual(mu["suggested_customer_message"], "You got it, Sam!")


class MuseFailures(unittest.TestCase):
    """Every failure: same result dict as deepseek's for the same failure, one FAILED log line."""

    def _both(self, mk_effects):
        mu = _drive(harness._infer_muse, *mk_effects(harness.MUSE_URL))
        ds = _drive(harness._infer_deepseek, *mk_effects(harness.DEEPSEEK_URL))
        return mu, ds

    def _assert_fail(self, mk_effects, error, etype):
        (mu, mcalls, mlog), (ds, _, _) = self._both(mk_effects)
        self.assertEqual(mu, ds)
        self.assertEqual(mu["error"], error)
        self.assertIsNone(mu["suggested_customer_message"])
        failed = [ln for ln in mlog.splitlines() if "infer FAILED" in ln]
        self.assertEqual(len(failed), 1, mlog)
        self.assertTrue(failed[0].startswith(f"[HC] infer FAILED backend=muse model=muse-spark-1.3 type={etype} "),
                        failed[0])
        self.assertNotIn("sk-muse-test-key", mlog)
        return mcalls

    def test_timeout(self):
        self._assert_fail(lambda u: [TimeoutError("timed out")], "api_error", "TimeoutError")

    def test_401(self):
        self._assert_fail(lambda u: [_http_err(u, 401, '{"error":{"code":"invalid_api_key"}}')], "api_error", 401)

    def test_402(self):
        self._assert_fail(lambda u: [_http_err(u, 402, '{"error":{"message":"Billing account issue."}}')],
                          "api_error", 402)

    def test_429(self):
        self._assert_fail(lambda u: [_http_err(u, 429, '{"error":{"type":"rate_limit_error"}}')], "api_error", 429)

    def test_5xx(self):
        for code in (500, 503, 504):
            with self.subTest(code=code):
                self._assert_fail(lambda u: [_http_err(u, code, '{"error":{"type":"server_error"}}')],
                                  "api_error", code)

    def test_bad_json_after_one_retry(self):
        calls = self._assert_fail(lambda u: ["not json", "still not json"], "bad_json", "bad_json")
        self.assertEqual(len(calls), 2)

    def test_bad_action_type(self):
        self._assert_fail(lambda u: [json.dumps(dict(GOOD, action_type="dance"))], "bad_action_type",
                          "bad_action_type")

    def test_missing_key(self):
        buf = io.StringIO()
        with mock.patch.dict(os.environ, {}, clear=False), contextlib.redirect_stdout(buf):
            os.environ.pop("MUSE_API_KEY", None)
            out = harness.infer(CTX, "muse")
        self.assertEqual(out["error"], "no_api_key")
        self.assertIn("[HC] infer FAILED backend=muse", buf.getvalue())


class MuseRouting(unittest.TestCase):
    def test_infer_routes_muse(self):
        with mock.patch("harness._infer_muse", return_value={"via": "muse"}) as fn, \
                mock.patch.dict(os.environ, {"MUSE_API_KEY": "m"}):
            self.assertEqual(harness.infer(CTX, "muse"), {"via": "muse"})
            fn.assert_called_once_with(CTX, "m")

    def test_compose_strips_backend_and_takes_failure_path(self):
        """HC_BACKEND=' muse ' (whitespace) reaches the muse backend; a failure escalates through
        compose exactly like deepseek's (error passed through, one FAILED line, no double log)."""
        def run(backend, url):
            calls = []

            def fake(req, timeout=None):
                calls.append(req.full_url)
                raise _http_err(url, 503, "{}")
            buf = io.StringIO()
            env = {"HC_BACKEND": backend, "MUSE_API_KEY": "m", "DEEPSEEK_API_KEY": "d"}
            with mock.patch.dict(os.environ, env), mock.patch("urllib.request.urlopen", fake), \
                    contextlib.redirect_stdout(buf):
                os.environ.pop("ANTHROPIC_API_KEY", None)
                resp = compose({"trigger": "inbound_reply", "now_et": "2026-10-12T14:10:00-04:00",
                                "contact_id": "C1", "identity": {"first_name": "Sam"},
                                "inbound_text": "hi", "history": []})
            return resp, calls, buf.getvalue()

        mresp, mcalls, mlog = run("  muse \n", harness.MUSE_URL)
        dresp, _, _ = run("deepseek", harness.DEEPSEEK_URL)
        self.assertEqual(mcalls, [harness.MUSE_URL])
        self.assertEqual(mresp, dresp)
        self.assertEqual(mresp["send_decision"], "escalate_human")
        self.assertTrue(mresp["error"].startswith("api_error"))
        self.assertEqual(mlog.count("infer FAILED"), 1)

    def test_active_model(self):
        with mock.patch.dict(os.environ, {"HC_BACKEND": " muse "}):
            self.assertEqual(_active_model(), "muse-spark-1.3")


if __name__ == "__main__":
    unittest.main()
