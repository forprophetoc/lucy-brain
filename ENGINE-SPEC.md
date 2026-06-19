# Lucy Decision Engine — Spec v1.0

**Status:** Canonical design reference. Synthesized from the decision-engine consortium (Cowork/Claude + Codex + Manus), Oscar's rulings, and the Phase-1.5 verification of `harness.py`.
**Canonical home:** belongs alongside `harness.py` in `…\Hermes\bakeoff\` (currently authored in Midwife; copy to the canonical folder — the Hermes/Midwife spec duplication is a known open item to resolve).

---

## Principle

Two layers. **Hard rules decide whether Lucy may speak and when; the model decides what she says; hard rules then verify the draft.** A sandwich: deterministic gates → grounded model judgment → deterministic validator.

The split is the whole design: deterministic code owns consent, timing, memory-truth, dedupe, escalation, and language; the model owns the fuzzy language work inside those walls.

---

## Pipeline (runs in priority order, per event)

1. **Classify** the event: `inbound` / `proactive` / `internal`.
2. **Suppressor gates (deterministic):**
   - **Opt-out (GHL-owned, not app-level):** Opt-out is owned by GHL (platform DND + carrier suppression on STOP). Production Lucy respects the contact's GHL DND status (state read; GHL blocks the send regardless). No app-level keyword detection. Natural-language opt-outs that don't trip GHL's keyword DND → Lucy must not pitch, acknowledges and stands down, and flags Oscar to mark DND (model behavior + a control scenario, not a deterministic gate).
   - **Wrong-number:** mark the number invalid, stop outreach.
   - **Internal events** (job_complete note, CRM update): no customer message unless explicitly mapped → silent.
3. **Timing gate (deterministic):**
   - **Inbound → `send_now`. ALWAYS.** Code sets it; the model has NO say over inbound timing. (Opt-out suppression, when applicable, happens in GHL below the app — it is not an app-level timing exception.)
   - **Proactive →** quiet-hours gate: defer outside the allowed window; send inside it (subject to cadence). An `estimate_ready` fulfilling a *live/active* customer request counts as a reply → send.
4. **Memory grounding (deterministic):** prices, warranty terms, dates, package come ONLY from stored facts → FOUND / NOT_FOUND. The model never regenerates or invents them. Missing fact → say it will be confirmed, or escalate.
5. **Escalation (deterministic triggers):** legal / threats / refund / chargeback / safety → **mandatory hand-off to Oscar.** Anger / price dispute / warranty-risk → model may draft, Oscar approves.
6. **Model judgment (inside the gates):** intent, sentiment, multi-intent decomposition, vague-timing interpretation, language (reply in Spanish to Spanish), tone, the "are you AI?" answer, message drafting — constrained to retrieved facts only.
7. **Validator (deterministic, after the draft):** reject any message that invents a price/warranty, breaks a timing rule, ignores opt-out, double-asks for a review, or replies in the wrong language. A rejected draft is treated as an error (step 8) — the bad draft never sends.
8. **Error / failure handling — Oscar is the fallback, always.** Any inference error OR validator rejection on an **inbound** → never silent, never a guessed reply → **alert Oscar instantly** so he answers by hand. Test harness: a loud flagged error row. Production: a real-time alert to Oscar's phone.
9. **Emit:** `action` + `timing` (send_now / defer_until / silent) + `message` + **audit block** (which deterministic rules fired, which model judgments ran, which memory facts were used). The audit block is what the deterministic `CONTROL_` checks assert against.

---

## The split

**Deterministic code (hard, non-negotiable):** event classification · opt-out *(GHL platform, not app)* · wrong-number · **inbound→send_now** · quiet-hours (proactive only) · review dedupe · internal-silence · memory grounding/retrieval · escalation triggers · language routing · the output validator · **error→alert-Oscar**.

**Model judgment (fuzzy, linguistic):** intent classification · sentiment · multi-intent decomposition · vague-date interpretation · Spanish phrasing · tone · "are you AI?" · clarify-vs-confirm · message drafting.

---

## Hard invariants (must be enforced in code, not prompt)

- An inbound customer message **always** yields `send_now`. The model cannot defer or silence an inbound.
- An inbound is **never** silently dropped. Errors/validator-rejections alert Oscar.
- Opt-out, once set, can never be overridden by a model-generated message.
- No price/warranty/date/package is ever stated unless it came from stored memory.

---

## Output schema (per event)

```
Decision {
  action            # suggest_message | answer_question | escalate_human | mark_opt_out | internal_only | no_action | ...
  timing            # send_now | defer_until:<ISO> | silent
  message           # the SMS draft (may be empty)
  confidence        # high | medium | low
  escalation        # none | human_review | human_takeover
  memory_writes     # facts to persist
  audit { rules_fired[], judgments_used[], memory_ids[] }
  error             # "" or error/timeout/refusal/validator-reject
}
```

---

## Production note (separate track — NOT the test harness)

The live agent needs a **warm, persistent Claude process** (or streaming API on OAuth) to respond fast. The Phase-1.5 measurement showed ~13–16 s per response on the current cold `claude -p` subprocess spawn — that overhead is the cold start, not the thinking. The test harness is batch and doesn't care about this latency; the live receiver does. Oscar's "always-on" instinct was correct about latency — keep Claude's brain, make it warm. There is also currently **no live inbound receiver** — that is its own production build.

---

## Open / flagged items

- Hermes/Midwife spec duplication: pick one canonical source (Hermes\bakeoff has the full set + harness.py).
- Opt-out logic is intentionally NOT in `harness.py` — GHL owns it (platform DND + carrier suppression on STOP). App-level keyword detection was removed (it was the source of the "cancel my appointment" false positive).
- Python runtime mismatch noted (3.11 here vs a 3.14 pin elsewhere) — confirm before production.
- Scoring stub (`estimate_ok`/`action_ok`/`judge_score`) stays stubbed; replaced by the deterministic `CONTROL_` checker, not a subjective judge. Blind-audit machinery is dropped (single engine).
