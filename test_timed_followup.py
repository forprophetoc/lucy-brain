"""
Unit tests (no network, no model): the brain sees the clock (now_et) and can return a timed
follow-up (followup_at). Inference is mocked at harness.infer / anthropic.Anthropic.

Run: python -m unittest -v test_timed_followup
"""
import contextlib
import io
import json
import os
import unittest
from unittest import mock

import harness
from hc_compose_service import compose

BASE_KEYS = {"reply", "send_decision", "facts", "language", "memory_facts_used", "reasoning", "error"}


def _req(**extra):
    r = {
        "trigger": "inbound_reply",
        "now": "2026-10-05T18:10:00.000Z",
        "contact_id": "C1",
        "identity": {"first_name": "Sam"},
        "inbound_text": "Can you reach out to me at 4pm today?",
        "history": [],
        "memory": {},
    }
    r.update(extra)
    return r


class _Fake:
    """Stands in for harness.infer: records the model context, returns a canned result."""

    def __init__(self, **result):
        self.context = None
        self.result = result

    def __call__(self, context, backend, *a, **k):
        self.context = context
        base = dict(action_type="suggest_message", confidence="high",
                    suggested_customer_message="You got it, Sam! I'll text you at 4.",
                    send_decision="send_now")
        base.update(self.result)
        return harness._infer_result(**base)


class TimedFollowupStage1(unittest.TestCase):
    def setUp(self):
        self._env = mock.patch.dict(os.environ, {"HC_BACKEND": "api"}, clear=False)
        self._env.start()
        os.environ.pop("ANTHROPIC_API_KEY", None)

    def tearDown(self):
        self._env.stop()

    def _compose(self, req, **result):
        fake = _Fake(**result)
        out_buf = io.StringIO()
        with mock.patch("harness.infer", fake), contextlib.redirect_stdout(out_buf):
            resp = compose(req)
        return resp, fake.context, out_buf.getvalue()

    # --- now_et in -> model context ---
    def test_now_et_reaches_model_context(self):
        resp, ctx, _ = self._compose(_req(now_et="2026-10-05T14:10:00-04:00"))
        self.assertEqual(ctx["local_time"]["now_et"], "2026-10-05T14:10:00-04:00")
        prompt = harness.build_user_prompt(harness._model_facing_context(ctx))
        self.assertIn('"now_et": "2026-10-05T14:10:00-04:00"', prompt)

    def test_without_now_et_current_et_is_computed_server_side(self):
        _, ctx, _ = self._compose(_req())  # only now (UTC)
        self.assertEqual(ctx["local_time"]["now_et"], "2026-10-05T14:10:00-04:00")

    def test_now_et_wins_over_now(self):
        _, ctx, _ = self._compose(_req(now="2026-01-01T00:00:00Z", now_et="2026-10-05T14:10:00-04:00"))
        self.assertEqual(ctx["local_time"]["now_et"], "2026-10-05T14:10:00-04:00")

    def test_malformed_now_et_falls_back_to_now(self):
        _, ctx, _ = self._compose(_req(now_et="4pm-ish"))
        self.assertEqual(ctx["local_time"]["now_et"], "2026-10-05T14:10:00-04:00")

    # --- followup_at out ---
    def test_valid_followup_at_parses_into_response(self):
        resp, _, _ = self._compose(_req(), followup_at="2026-10-05T16:00:00-04:00")
        self.assertEqual(resp["followup_at"], "2026-10-05T16:00:00-04:00")
        self.assertEqual(resp["send_decision"], "send_now")

    def test_followup_at_in_utc_is_normalized_to_et(self):
        resp, _, _ = self._compose(_req(), followup_at="2026-10-05T20:00:00Z")
        self.assertEqual(resp["followup_at"], "2026-10-05T16:00:00-04:00")

    def test_response_without_followup_at_is_unchanged(self):
        resp, _, _ = self._compose(_req())
        self.assertEqual(set(resp), BASE_KEYS)
        self.assertEqual(resp["reply"], "You got it, Sam! I'll text you at 4.")

    def test_malformed_followup_at_dropped_reply_kept_and_logged(self):
        for bad in ("4pm today", "2026-10-05T16:00:00", "2026-13-40T16:00:00-04:00"):
            resp, _, log = self._compose(_req(), followup_at=bad)
            self.assertNotIn("followup_at", resp, bad)
            self.assertEqual(resp["reply"], "You got it, Sam! I'll text you at 4.")
            self.assertEqual(resp["send_decision"], "send_now")
            self.assertIn("[HC] followup_at dropped (malformed)", log)

    # --- schema + parser ---
    def test_schema_lists_followup_at(self):
        self.assertIn("followup_at:", harness.SYSTEM_PROMPT)
        self.assertIn("disengaged, followup_at.", harness.OUTPUT_INSTRUCTION)

    def test_api_parser_carries_followup_at(self):
        def run(model_json):
            client = mock.MagicMock()
            block = mock.MagicMock(type="text", text=json.dumps(model_json))
            client.messages.create.return_value = mock.MagicMock(content=[block], usage=None)
            with mock.patch("anthropic.Anthropic", return_value=client), \
                    contextlib.redirect_stdout(io.StringIO()):
                return harness._infer_claude_api({"local_time": {}}, "sk-test")

        with_it = run({"action_type": "suggest_message", "confidence": "high",
                       "suggested_customer_message": "ok", "send_decision": "send_now",
                       "followup_at": "2026-10-05T16:00:00-04:00"})
        self.assertEqual(with_it["followup_at"], "2026-10-05T16:00:00-04:00")
        self.assertEqual(with_it["error"], "")
        without = run({"action_type": "suggest_message", "confidence": "high",
                       "suggested_customer_message": "ok", "send_decision": "send_now"})
        self.assertEqual(without["followup_at"], "")
        self.assertEqual(without["suggested_customer_message"], "ok")


class PlaybookRules(unittest.TestCase):
    """Stage 2/3 — the rules are present in the ASSEMBLED prompt (system + user + output
    instruction) exactly as both backends send it. Behavior is proven by the real-model smoke."""

    def _assembled(self):
        ctx = {"local_time": {"now_et": "2026-10-05T14:10:00-04:00"}, "current_event": {}}
        return (harness.SYSTEM_PROMPT + "\n\n"
                + harness.build_user_prompt(harness._model_facing_context(ctx)) + "\n\n"
                + harness.OUTPUT_INSTRUCTION)

    def test_text_vs_call_rule_present(self):
        p = self._assembled()
        self.assertIn("TIMED TEXT FOLLOW-UPS — TEXT vs CALL:", p)
        for phrase in ('"morning" = 10:00', '"afternoon" = 14:00', '"evening" = 18:00',
                       'a day with no time ("tomorrow", a', "weekday) = 10:00",
                       "computed from local_time.now_et",
                       'asks for Oscar or a real person: escalate_oscar=true',
                       "Never refuse an early or late time",
                       "don't re-ask why they wanted it"):
            self.assertIn(phrase, p, phrase)
        # The rule sits once, before the generic fallback line, and after AVAILABILITY.
        self.assertEqual(p.count("TIMED TEXT FOLLOW-UPS"), 1)
        self.assertLess(p.index("AVAILABILITY (quote ONLY"), p.index("TIMED TEXT FOLLOW-UPS"))

    def test_never_write_free_line_present(self):
        p = self._assembled()
        self.assertEqual(p.count('NEVER WRITE "FREE":'), 1)
        for phrase in ('"free estimate", "free of', '"feel free", "carefree"',
                       '"feel free to text me" becomes "just text me"',
                       '"no charge" / "no cost" only where the KB already allows it',
                       'Ready answer — asked whether the estimate is free', '"No cost to you."'):
            self.assertIn(phrase, p, phrase)

    def test_d2_rule15_scoped_and_kb_agrees(self):
        p = self._assembled()
        # Playbook: rule #15 scoped by estimate-on-record; old absolute wording gone.
        self.assertIn("PHOTOS & ESTIMATES (rule #15 — scoped by whether THIS contact has an estimate on record):", p)
        self.assertIn("Ask the customer to text a photo of the tub to (239) 539-4777 ONLY when ALL of these hold:", p)
        self.assertIn("NEVER on a proactive / follow-up compose", p)
        self.assertIn("the customer's message in THIS turn asks about price, a quote, or getting started", p)
        self.assertIn("contact_details has no package and no\n    estimate_amount", p)
        self.assertIn('quote NO price and NO price range (no "$299", no "$299–$449", no "$300–$600")', p)
        self.assertIn("Estimate ON record: Lucy NEVER asks for a photo", p)
        for gone in ("ABSOLUTE — NO PHOTOS, NO ESTIMATES (rule #15, NO EXCEPTIONS)",
                     "ask for a photo for ANYONE — new or known",
                     'NO situation in which "send a photo to get a quote"'):
            self.assertNotIn(gone, p, gone)
        # KB (injected into the same prompt): edited lines present.
        self.assertIn("To get a quote (contacts with NO estimate on record — Oscar 2026-10-04): ask them to "
                      "text a photo of the tub to (239) 539-4777", p)
        self.assertIn("A contact who already has an estimate is never asked for a photo.", p)
        self.assertIn("$299–$449 depending on condition and repairs needed. NEVER quote this range to a "
                      "contact with no estimate on record.", p)
        self.assertIn("NEVER quote these figures to a contact with no estimate on record.", p)


class TextLengthCap(unittest.TestCase):
    """Stage 9 — <=320 chars per text is enforced in code by harness.run_bakeoff (shared by
    compose() and the gauntlet): one shorten retry, else escalate. Driven through compose()."""

    def setUp(self):
        self._env = mock.patch.dict(os.environ, {"HC_BACKEND": "api"}, clear=False)
        self._env.start()
        os.environ.pop("ANTHROPIC_API_KEY", None)

    def tearDown(self):
        self._env.stop()

    def _run(self, *replies):
        calls = []

        def fake_infer(context, backend, *a, **k):
            calls.append(context)
            return harness._infer_result(action_type="suggest_message", confidence="high",
                                         suggested_customer_message=replies[len(calls) - 1],
                                         send_decision="send_now")

        with mock.patch("harness.infer", fake_infer), contextlib.redirect_stdout(io.StringIO()) as log:
            resp = compose(_req())
        return resp, calls, log.getvalue()

    def test_373_retry_300_passes(self):
        long, short = "A" * 373, "B" * 300
        resp, calls, log = self._run(long, short)
        self.assertEqual(len(calls), 2)
        self.assertIn("revision_request", calls[1])
        self.assertIn(long, calls[1]["revision_request"])
        self.assertEqual(resp["reply"], short)
        self.assertEqual(resp["send_decision"], "send_now")
        self.assertIn("shortened on retry (373 -> 300)", log)
        # One location: the cap lives in harness (shared path), not duplicated in the service.
        self.assertTrue(callable(harness.enforce_text_cap))
        with open("hc_compose_service.py", encoding="utf-8") as fh:
            self.assertNotIn("revision_request", fh.read())

    def test_373_retry_360_takes_failure_path(self):
        resp, calls, log = self._run("A" * 373, "B" * 360)
        self.assertEqual(len(calls), 2)
        self.assertEqual(resp["send_decision"], "escalate_human")
        self.assertIn("after one retry -> escalate", log)

    def test_at_or_under_320_makes_no_retry(self):
        for n in (1, 320):
            resp, calls, _ = self._run("C" * n)
            self.assertEqual(len(calls), 1, n)
            self.assertEqual(resp["send_decision"], "send_now")
            self.assertEqual(resp["reply"], "C" * n)

    def test_two_texts_each_under_320_is_fine(self):
        two = "D" * 300 + "\n\n" + "E" * 300
        resp, calls, _ = self._run(two)
        self.assertEqual(len(calls), 1)
        self.assertEqual(resp["reply"], two)

    def test_retry_error_takes_failure_path(self):
        calls = []

        def fake_infer(context, backend, *a, **k):
            calls.append(1)
            if len(calls) == 1:
                return harness._infer_result(action_type="suggest_message", confidence="high",
                                             suggested_customer_message="A" * 373, send_decision="send_now")
            return harness._infer_result(error="api_error", message_to_oscar="boom")

        with mock.patch("harness.infer", fake_infer), contextlib.redirect_stdout(io.StringIO()):
            resp = compose(_req())
        self.assertEqual(resp["send_decision"], "escalate_human")


class ProactivePhotoGuard(unittest.TestCase):
    """D2 in code — harness.run_bakeoff: a proactive compose that asks for a photo gets one retry,
    else escalates; inbound turns are untouched. Driven through compose(), model mocked."""

    PHOTO = "Ready to get started? Send a photo of your tub to (239) 539-4777 and I'll get you a quote."
    CLEAN = "Hi Eleanor! You asked us to check back in January. Ready to move forward?"

    def setUp(self):
        self._env = mock.patch.dict(os.environ, {"HC_BACKEND": "api"}, clear=False)
        self._env.start()
        os.environ.pop("ANTHROPIC_API_KEY", None)

    def tearDown(self):
        self._env.stop()

    def _run(self, trigger, *replies):
        calls = []

        def fake_infer(context, backend, *a, **k):
            calls.append(context)
            return harness._infer_result(action_type="suggest_message", confidence="high",
                                         suggested_customer_message=replies[len(calls) - 1],
                                         send_decision="send_now")

        req = _req(trigger=trigger, inbound_text="" if trigger != "inbound_reply" else "how much?")
        with mock.patch("harness.infer", fake_infer), contextlib.redirect_stdout(io.StringIO()) as log:
            resp = compose(req)
        return resp, calls, log.getvalue()

    def test_proactive_photo_ask_retry_clean_passes(self):
        resp, calls, log = self._run("due_date_sweep", self.PHOTO, self.CLEAN)
        self.assertEqual(len(calls), 2)
        self.assertIn("NO request for a photo", calls[1]["revision_request"])
        self.assertEqual(resp["reply"], self.CLEAN)
        self.assertEqual(resp["send_decision"], "send_now")
        self.assertIn("proactive photo request -> removed on retry", log)

    def test_proactive_photo_ask_retry_still_asks_escalates(self):
        resp, calls, log = self._run("due_date_sweep", self.PHOTO, "Just text a pic of the tub so we can quote it.")
        self.assertEqual(len(calls), 2)
        self.assertEqual(resp["send_decision"], "escalate_human")
        self.assertIn("proactive photo request after one retry -> escalate", log)

    def test_inbound_photo_ask_untouched(self):
        resp, calls, _ = self._run("inbound_reply", self.PHOTO)
        self.assertEqual(len(calls), 1)
        self.assertEqual(resp["reply"], self.PHOTO)
        self.assertEqual(resp["send_decision"], "send_now")

    def test_proactive_without_photo_ask_no_retry(self):
        resp, calls, _ = self._run("due_date_sweep", self.CLEAN)
        self.assertEqual(len(calls), 1)
        self.assertEqual(resp["reply"], self.CLEAN)

    def test_guard_pattern_matches_the_checks(self):
        import controls
        import scenario_suite
        samples = [self.PHOTO, "text me a pic of the tub", "share a picture so we can quote",
                   "Mándame una foto de tu bañera", "photo of your tub please", self.CLEAN,
                   "Great photo quality!", "no pictures needed"]
        for s in samples:
            checks = bool(controls.PHOTO_REQ_RE.search(s)) or bool(scenario_suite.PHOTO_REQ_RE.search(s))
            self.assertEqual(bool(harness.PHOTO_REQ_RE.search(s)), checks, s)


class InboundPhotoScopeGuard(unittest.TestCase):
    """D2 in code, inbound side — harness.run_bakeoff: a photo ask on an inbound turn is allowed
    only for a no-estimate contact asking about price/quote/getting started; otherwise one retry,
    else escalate. Driven through compose(), model mocked."""

    PHOTO = "Yes! Just text a photo of your tub to (239) 539-4777 and we'll send your exact price."
    CLEAN = "Yes, Pat! Naples is in our service area. Happy to help."
    EST_THREAD = [{"from": "lucy", "text": "Your estimate is ready: https://app.esticlose.com/estimate/bathtub-pros/p1",
                   "ts": "2026-10-05T10:00:00-04:00"}]
    PRICE_THREAD = [{"from": "lucy", "text": "Your Gold package comes to $449.", "ts": "2026-10-05T10:00:00-04:00"}]

    def setUp(self):
        self._env = mock.patch.dict(os.environ, {"HC_BACKEND": "api"}, clear=False)
        self._env.start()
        os.environ.pop("ANTHROPIC_API_KEY", None)

    def tearDown(self):
        self._env.stop()

    def _run(self, inbound, history, *replies):
        calls = []

        def fake_infer(context, backend, *a, **k):
            calls.append(context)
            return harness._infer_result(action_type="suggest_message", confidence="high",
                                         suggested_customer_message=replies[len(calls) - 1],
                                         send_decision="send_now")

        with mock.patch("harness.infer", fake_infer), contextlib.redirect_stdout(io.StringIO()) as log:
            resp = compose(_req(inbound_text=inbound, history=history))
        return resp, calls, log.getvalue()

    def test_estimate_on_record_photo_ask_retry_clean_passes(self):
        resp, calls, log = self._run("Do you cover Naples?", self.EST_THREAD, self.PHOTO, self.CLEAN)
        self.assertEqual(len(calls), 2)
        self.assertIn("NO request", calls[1]["revision_request"])
        self.assertEqual(resp["reply"], self.CLEAN)
        self.assertEqual(resp["send_decision"], "send_now")
        self.assertIn("inbound photo request outside D2 -> removed on retry", log)

    def test_estimate_on_record_photo_ask_retry_still_asks_escalates(self):
        resp, calls, log = self._run("How much again?", self.PRICE_THREAD, self.PHOTO,
                                     "Send a pic of the tub so we can confirm.")
        self.assertEqual(len(calls), 2)
        self.assertEqual(resp["send_decision"], "escalate_human")
        self.assertIn("after one retry -> escalate", log)

    def test_no_estimate_non_price_question_photo_ask_is_retried(self):
        resp, calls, _ = self._run("Do you cover Naples?", [], self.PHOTO, self.CLEAN)
        self.assertEqual(len(calls), 2)
        self.assertEqual(resp["reply"], self.CLEAN)

    def test_no_estimate_price_question_photo_ask_untouched(self):
        for q in ("how much to refinish a tub?", "what's the total price for my tub?", "how do I get started?"):
            resp, calls, _ = self._run(q, [], self.PHOTO)
            self.assertEqual(len(calls), 1, q)
            self.assertEqual(resp["reply"], self.PHOTO, q)
            self.assertEqual(resp["send_decision"], "send_now", q)

    def test_no_photo_ask_no_retry(self):
        resp, calls, _ = self._run("Do you cover Naples?", self.EST_THREAD, self.CLEAN)
        self.assertEqual(len(calls), 1)
        self.assertEqual(resp["reply"], self.CLEAN)

    def test_estimate_on_record_detection(self):
        on = harness._estimate_on_record
        self.assertTrue(on({"contact_details": {"package": "gold", "estimate_amount": 451.0}}))
        self.assertTrue(on({"contact_details": {}, "transcript": "[shop] https://app.esticlose.com/estimate/x"}))
        self.assertTrue(on({"contact_details": {}, "transcript": "[shop] Gold is $449"}))
        self.assertTrue(on({"contact_details": {}, "current_event": {"followup": {"estimate_url": "u"}}}))
        self.assertFalse(on({"contact_details": {"package": "", "estimate_amount": None}, "transcript": "[customer] hi"}))


GOOD = {"action_type": "suggest_message", "confidence": "high", "message_to_oscar": "n",
        "rationale": "r", "evidence": ["e"], "suggested_customer_message": "You got it!",
        "estimate_readiness": None, "send_decision": "send_now", "language": "en",
        "memory_facts_used": [], "escalate_oscar": False, "escalation_reason": "",
        "followup_date": "", "first_name": "", "scope": "", "disengaged": "",
        "followup_at": "2026-10-05T16:00:00-04:00"}
CTX = {"local_time": {"now_et": "2026-10-05T14:10:00-04:00"},
       "current_event": {"event_type": "inbound_reply", "inbound_text": "text me at 4"}}


class _HttpResp:
    def __init__(self, payload):
        self._b = json.dumps(payload).encode("utf-8")

    def read(self):
        return self._b

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def _ds_payload(content):
    return {"choices": [{"message": {"role": "assistant", "content": content}}],
            "usage": {"prompt_tokens": 10, "completion_tokens": 5}}


class DeepSeekBackend(unittest.TestCase):
    """Stage 3B — HC_BACKEND=deepseek, HTTP mocked (urllib.request.urlopen). Each failure case is
    run through the api backend too and the two results must be identical."""

    def _deepseek(self, *effects):
        calls = []

        def fake_urlopen(req, timeout=None):
            calls.append((req, timeout))
            eff = effects[min(len(calls), len(effects)) - 1]
            if isinstance(eff, BaseException):
                raise eff
            return _HttpResp(_ds_payload(eff))

        with mock.patch("urllib.request.urlopen", fake_urlopen), contextlib.redirect_stdout(io.StringIO()):
            out = harness._infer_deepseek(CTX, "sk-ds-test")
        return out, calls

    def _api(self, *effects):
        client = mock.MagicMock()
        seq = []
        for eff in effects:
            seq.append(eff if isinstance(eff, BaseException) else
                       mock.MagicMock(content=[mock.MagicMock(type="text", text=eff)], usage=None))
        client.messages.create.side_effect = seq
        with mock.patch("anthropic.Anthropic", return_value=client), contextlib.redirect_stdout(io.StringIO()):
            out = harness._infer_claude_api(CTX, "sk-test")
        return out, client

    def test_request_shape_and_auth(self):
        _, calls = self._deepseek(json.dumps(GOOD))
        req, timeout = calls[0]
        self.assertEqual(req.full_url, "https://api.deepseek.com/chat/completions")
        self.assertEqual(req.get_method(), "POST")
        self.assertEqual(req.get_header("Authorization"), "Bearer sk-ds-test")
        self.assertEqual(req.get_header("Content-type"), "application/json")
        self.assertEqual(timeout, harness.BRAIN_TIMEOUT_SECONDS)
        body = json.loads(req.data.decode("utf-8"))
        self.assertEqual(body["model"], "deepseek-v4-pro")
        self.assertEqual(body["response_format"], {"type": "json_object"})
        self.assertEqual(body["thinking"], {"type": "disabled"})
        self.assertEqual(body["temperature"], 0)
        self.assertFalse(body["stream"])
        # SAME system prompt and user turn as the api backend.
        _, client = self._api(json.dumps(GOOD))
        api_kwargs = client.messages.create.call_args.kwargs
        self.assertEqual(body["messages"][0], {"role": "system", "content": api_kwargs["system"]})
        self.assertEqual(body["messages"][1], {"role": "user", "content": api_kwargs["messages"][0]["content"]})
        self.assertIn("JSON", body["messages"][1]["content"])  # JSON mode requires the word

    def test_valid_json_parses_to_same_fields_as_api(self):
        ds, _ = self._deepseek(json.dumps(GOOD))
        api, _ = self._api(json.dumps(GOOD))
        strip = lambda d: {k: v for k, v in d.items() if k not in ("usage", "cost_usd")}
        self.assertEqual(strip(ds), strip(api))
        self.assertEqual(ds["followup_at"], "2026-10-05T16:00:00-04:00")
        self.assertEqual(ds["usage"], {"input_tokens": 10, "output_tokens": 5})

    def test_timeout_identical_failure(self):
        ds, _ = self._deepseek(TimeoutError("timed out"))
        api, _ = self._api(TimeoutError("timed out"))
        self.assertEqual(ds, api)
        self.assertEqual(ds["error"], "api_error")

    def test_5xx_takes_api_error_path(self):
        import urllib.error
        err = urllib.error.HTTPError("https://api.deepseek.com/chat/completions", 503, "Service Unavailable", {}, None)
        ds, _ = self._deepseek(err)
        api, _ = self._api(RuntimeError(str(err)))
        self.assertEqual(ds, api)
        self.assertEqual(ds["error"], "api_error")
        self.assertIsNone(ds["suggested_customer_message"])

    def test_malformed_json_identical_failure_after_one_retry(self):
        ds, calls = self._deepseek("not json", "still not json")
        api, client = self._api("not json", "still not json")
        self.assertEqual(ds, api)
        self.assertEqual(ds["error"], "bad_json")
        self.assertEqual(len(calls), 2)
        self.assertEqual(client.messages.create.call_count, 2)

    def test_empty_content_is_malformed(self):
        ds, _ = self._deepseek("", "")
        self.assertEqual(ds["error"], "bad_json")

    def test_bad_action_type_identical(self):
        bad = json.dumps(dict(GOOD, action_type="dance"))
        ds, _ = self._deepseek(bad)
        api, _ = self._api(bad)
        self.assertEqual(ds, api)
        self.assertEqual(ds["error"], "bad_action_type")

    def test_infer_routing_and_default_unchanged(self):
        with mock.patch("harness._infer_claude_api", return_value={"via": "api"}) as api_fn, \
                mock.patch("harness._infer_deepseek", return_value={"via": "ds"}) as ds_fn, \
                mock.patch.dict(os.environ, {"ANTHROPIC_API_KEY": "k", "DEEPSEEK_API_KEY": "d"}):
            self.assertEqual(harness.infer(CTX, "api"), {"via": "api"})
            api_fn.assert_called_once_with(CTX, "k")
            ds_fn.assert_not_called()
            self.assertEqual(harness.infer(CTX, "deepseek"), {"via": "ds"})
            ds_fn.assert_called_once_with(CTX, "d")
        # compose's default backend is still the env default "claude" when HC_BACKEND is unset.
        src = open("hc_compose_service.py", encoding="utf-8").read()
        self.assertIn('backend=os.environ.get("HC_BACKEND", "claude")', src)

    def test_missing_deepseek_key(self):
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("DEEPSEEK_API_KEY", None)
            out = harness.infer(CTX, "deepseek")
        self.assertEqual(out["error"], "no_api_key")


if __name__ == "__main__":
    unittest.main()
