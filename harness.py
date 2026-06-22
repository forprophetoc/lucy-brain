
import csv
import json
import time
import pytz
import os
import io
import hashlib
import re
import shutil
import subprocess
import copy # Import copy module
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Optional, List, Dict, Any, Callable

# --- REAL HERMY DATACLASSES AND ENUMS (from hermy/hermy/state.py and hermy/hermy/schema.py) ---

class LeadStatus(str, Enum):
    NEW = "new"
    IN_INTAKE = "in_intake"
    ESTIMATE_READY = "estimate_ready"
    STALLED = "stalled"
    DORMANT = "dormant"
    WON = "won"
    LOST = "lost"

REQUIRED_INTAKE_FIELDS = [
    "contact_name",
    "tub_material",
    "tub_type",
    "damage_description",
    "scope",
]
REQUIRED_IMAGE_KINDS = ["full_tub"]

@dataclass
class Image:
    image_id: str
    kind: str
    quality: str = "unknown"
    observations: list[str] = field(default_factory=list)

@dataclass
class Message:
    ts: float
    sender: str
    text: str

@dataclass
class LeadState:
    lead_id: str
    contact_name: Optional[str] = None
    channel: str = "sms"
    status: LeadStatus = LeadStatus.NEW
    known: dict = field(default_factory=dict)
    images: list[Image] = field(default_factory=list)
    messages: list[Message] = field(default_factory=list)
    objections: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    last_contact_ts: Optional[float] = None
    created_ts: Optional[float] = None

    def image_kinds(self) -> set[str]:
        return {img.kind for img in self.images if img.quality != "unusable"}

    def missing_fields(self) -> list[str]:
        miss = [f for f in REQUIRED_INTAKE_FIELDS
                if not self.known.get(f) and not (f == "contact_name" and self.contact_name)]
        have = self.image_kinds()
        for kind in REQUIRED_IMAGE_KINDS:
            if kind not in have:
                miss.append(f"image:{kind}")
        return miss

    def days_since_contact(self, now: float) -> Optional[float]:
        if self.last_contact_ts is None:
            return None
        return (now - self.last_contact_ts) / 86400.0

    def transcript(self, limit: int = 12) -> str:
        rows = self.messages[-limit:]
        return "\n".join(f"[{m.sender}] {m.text}" for m in rows)

    def context_brief(self, now: float) -> dict:
        return {
            "lead_id": self.lead_id,
            "contact_name": self.contact_name,
            "status": self.status.value,
            "known": self.known,
            "missing": self.missing_fields(),
            "images": [
                {"kind": i.kind, "quality": i.quality, "observations": i.observations}
                for i in self.images
            ],
            "objections": self.objections,
            "tags": self.tags,
            "days_since_contact": self.days_since_contact(now),
            "transcript": self.transcript(),
        }

def lead_from_dict(d: dict) -> LeadState:
    images = [Image(**img) for img in d.get("images", [])]
    messages = [Message(**m) for m in d.get("messages", [])]
    return LeadState(
        lead_id=d["lead_id"],
        contact_name=d.get("contact_name"),
        channel=d.get("channel", "sms"),
        status=LeadStatus(d.get("status", "new")),
        known=d.get("known", {}),
        images=images,
        messages=messages,
        objections=d.get("objections", []),
        tags=d.get("tags", []),
        last_contact_ts=d.get("last_contact_ts"),
        created_ts=d.get("created_ts"),
    )


class Track(str, Enum):
    INTAKE = "intake"
    NURTURE = "nurture"

class Confidence(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class Behavior(str, Enum):
    AUTONOMOUS = "autonomous"
    RECOMMEND = "recommend"
    SUPPRESS = "suppress"

    @property
    def rank(self) -> int:
        return {"suppress": 0, "recommend": 1, "autonomous": 2}[self.value]

class ActionType(str, Enum):
    REQUEST_PHOTO = "request_photo"
    REQUEST_INFO = "request_info"
    ASK_QUESTION = "ask_question"
    VISUAL_OBSERVATION = "visual_observation"
    FLAG_UPSELL = "flag_upsell"
    MARK_ESTIMATE_READY = "mark_estimate_ready"
    SUGGEST_FOLLOWUP = "suggest_followup"
    SUMMARIZE = "summarize"
    SUGGEST_MESSAGE = "suggest_message"
    NO_ACTION = "no_action"

HIGH_RISK_ACTIONS = {
    ActionType.FLAG_UPSELL,
    ActionType.SUGGEST_MESSAGE,
    ActionType.MARK_ESTIMATE_READY,
}

# --- DETERMINISTIC GATE LAYER (classification + inbound timing override) ---
# Customer-initiated event types. Their send-timing is owned by code, not the model.
INBOUND_EVENT_TYPES = {"inbound_reply"}

# An inbound that cannot be answered is escalated to a human — never silently dropped.
# (Opt-out is owned by GHL at the platform level: DND + carrier suppression on STOP.)
ESCALATE_HUMAN = "escalate_human"

@dataclass
class Recommendation:
    lead_id: str
    track: Track
    action_type: ActionType
    confidence: Confidence
    score: float
    behavior: Behavior
    would_be: Behavior
    message_to_oscar: str
    rationale: str = ""
    evidence: list[str] = field(default_factory=list)
    suggested_customer_message: Optional[str] = None
    estimate_readiness: Optional[int] = None
    suppressed: bool = False
    suppressed_reason: Optional[str] = None
    send_decision: str = "silent"
    language: str = ""                                      # ISO code Lucy replied in ("en"/"es"); "" if no message
    memory_facts_used: list = field(default_factory=list)   # prior-arc facts used this turn; [] if none
    escalate_oscar: bool = False                            # True -> flag Oscar (hand-off / set DND)
    escalation_reason: str = ""                             # why escalated; "" if not
    followup_date: str = ""                                 # canonical YYYY-MM-DD from a stated timeline; "" if none
    phase: int = 1
    created_ts: float = field(default_factory=lambda: time.time())

    def to_dict(self) -> dict:
        d = asdict(self)
        d["track"] = self.track.value
        d["action_type"] = self.action_type.value
        d["confidence"] = self.confidence.value
        d["behavior"] = self.behavior.value
        d["would_be"] = self.would_be.value
        return d

# --- REAL HERMY PROMPTS (from hermy/hermy/prompts.py) ---

SYSTEM_PROMPT = """\
You are Hermy, an operational intelligence layer for a bathtub-refinishing shop.
You do NOT talk to customers. You observe a lead's state and produce ONE
structured recommendation for the shop owner (Oscar).

CUSTOMER-FACING IDENTITY (applies to every suggested_customer_message you draft):
You are Lucy, Bathtub Pros' assistant. NEVER claim or imply you are a human/real
person, and never imply you are Oscar. If asked whether you're a real person, a
bot, or AI, answer plainly and warmly, then help — e.g.: "I'm Lucy, Bathtub Pros'
assistant. I can help you right now, or I can relay a message to Oscar first thing
in the morning." One honest line, then keep moving. Never say things like "you've
got a real person here."

OPT-OUT / DO-NOT-CONTACT:
If a customer asks to stop being contacted in ANY wording (not just the word
"STOP" — e.g. "please stop texting me", "leave me alone", "take me off your
list"), briefly acknowledge that you'll stop, do NOT pitch or upsell, and set
escalate_oscar=true so Oscar can mark them Do-Not-Contact.

NEVER SILENT ON INBOUND:
Every inbound customer message gets a non-empty customer-facing reply. Never
return an empty suggested_customer_message for an inbound. If you truly can't
answer, say you'll confirm and follow up — but never send nothing.

CONTINUE THE RELATIONSHIP — NEVER COLD-RESTART (rule #14):
When the lead already has prior history, a quote/price on record, or a stated
timeline (anything in the conversation or memory shows you've engaged before),
CONTINUE from where you left off: reference the prior quote/price, their stated
timeline, or the last thing discussed. Do NOT cold-intake a known lead — never ask
them to "send a photo to get started" and never treat a contact with prior context
as a brand-new lead. A photo/intake request is appropriate ONLY for a genuinely NEW
lead with no quote and no usable prior context. Proactive re-engagement (a due
follow-up) is ALWAYS a continuation: pick up the thread, do not reopen intake.
On a PROACTIVE re-engagement specifically (a due follow-up with no new inbound),
your message is a warm check-in that references their stated timeline and invites
them to continue ("are you ready to move forward?", "want me to get you on the
schedule?"). Do NOT lead with a photo or intake request — EVEN IF no quote exists
yet. The proactive touch reopens the door; it does not reopen intake. If a photo is
genuinely still needed, ask only AFTER they reply, never as the opening call-to-action.

Deterministic systems already handle estimates, pricing, CRM and delivery. Your
only job is judgment under ambiguity: what is missing, what the photos show, what
to ask next, when an estimate is ready, whether an upsell is warranted, and how
to time nurture.

Refinishing domain knowledge:
- A confident estimate needs a clear, full view of the tub. Close-ups alone are
  not enough.
- Bubbling, peeling, or flaking — especially around the drain or on the floor —
  signals a PRIOR COATING that will likely need a strip job. Flag it.
- Surrounds/tile in poor or dated condition near a tub are a legitimate upsell —
  but ONLY when you can actually see their condition clearly. If the tile/surround
  is not clearly visible, DO NOT propose an upsell.
- Snowbirds and "circle back later" leads are timing problems, not dead leads.
  Recommend follow-up when their window arrives.

Confidence rules:
- Output a raw confidence from 0.0 to 1.0 reflecting how sure you are.
- Be honest and conservative. Uncertainty should produce LOW scores.
- Never inflate confidence to justify an upsell. A missed upsell is cheap; a
  wrong one costs trust.

Respond with ONLY a JSON object, no prose, with these keys:
  action_type: one of [request_photo, request_info, ask_question,
     visual_observation, flag_upsell, mark_estimate_ready, suggest_followup,
     summarize, suggest_message, no_action]
  confidence: one of [high, medium, low]
  message_to_oscar: short internal note to the owner
  rationale: one sentence of reasoning
  evidence: array of short strings (the signals you used)
  suggested_customer_message: string or null (a draft only if relevant)
  estimate_readiness: integer 0..100 or null (intake only)
  send_decision: one of [send_now, defer_until:<ISO>, silent]. proactive/outbound should not send during quiet hours; a customer-initiated inbound may be answered any time.
  language: ISO code of the language the customer message is written in ("en", "es", ...); "" if there is no customer message
  memory_facts_used: array of the specific prior facts you used this turn (e.g. ["package=gold", "price=451"]); [] if none
  escalate_oscar: boolean — true when this needs Oscar's attention/hand-off (do-not-contact request, legal/refund/safety, or anything you should not handle autonomously); else false
  escalation_reason: short string naming why (e.g. "do-not-contact request"); "" when escalate_oscar is false
  followup_date: canonical YYYY-MM-DD when the customer states a timeline ("ready in January", "after we're back from Ohio next month", "call me in 3 weeks"), resolved relative to the provided local_time/now; "" when no timeline is stated. Do NOT invent a date when none is implied.
"""

def build_user_prompt(context_brief: dict) -> str:
    return (
        "Lead state:\n"
        + json.dumps(context_brief, indent=2, default=str)
        + "\n\nProduce the single most operationally appropriate recommendation "
          "as JSON."
    )

# --- HARNESS UTILITIES ---

NY_TZ = pytz.timezone('America/New_York')

def parse_csv(csv_string: str) -> List[Dict[str, str]]:
    # Strip potential leading/trailing whitespace from each line before parsing
    # This helps with issues where `csv.DictReader` might misinterpret headers due to whitespace
    lines = csv_string.strip().splitlines()
    # Ensure each line is stripped of whitespace before creating StringIO object
    f = io.StringIO('\n'.join(line.strip() for line in lines))
    reader = csv.DictReader(f)
    # print(f"DEBUG: CSV fieldnames detected: {reader.fieldnames}") # Debug print - re-enable if needed
    return list(reader)

def to_timestamp(iso_datetime_str: str) -> float:
    dt_obj = datetime.fromisoformat(iso_datetime_str)
    if dt_obj.tzinfo is None:
        # If naive, localize it to NY_TZ
        dt_obj = NY_TZ.localize(dt_obj)
    else:
        # If timezone-aware, convert it to NY_TZ
        dt_obj = dt_obj.astimezone(NY_TZ)
    return dt_obj.timestamp()

def is_quiet_hours(dt: datetime) -> bool:
    # Quiet hours: 21:00 (9 PM) to 08:00 (8 AM) local time
    return not (8 <= dt.hour < 21)

# --- CONTEXT BUILDING ---

def build_context(
    contact: Dict[str, str],
    lead_state: LeadState,
    event: Dict[str, str],
    now: datetime
) -> Dict[str, Any]:
    # Convert now to timestamp for LeadState methods
    now_timestamp = now.timestamp()

    # Get the model-ready brief of the lead state
    lead_state_brief = lead_state.context_brief(now_timestamp)

    # Add contact details to the brief (flattened)
    context = {
        **lead_state_brief,
        "current_event": {
            "event_id": event["event_id"],
            "event_type": event["event_type"],
            "inbound_text": event["inbound_text"] if event["inbound_text"] else None,
            "expected_behavior": event["expected_behavior"] if event["expected_behavior"] else None,
            "scheduled_at": event["scheduled_at"], # Keep original for reference
        },
        "contact_details": {
            "contact_id": contact["contact_id"],
            "first_name": contact["first_name"],
            "last_name": contact["last_name"],
            "phone": contact["phone"],
            "city": contact["city"],
            "service": contact["service"],
            "package": contact["package"],
            "estimate_amount": float(contact["estimate_amount"]) if contact["estimate_amount"] else None,
            "tags": [tag.strip() for tag in contact["tags"].split(',')] if contact["tags"] else [],
            "persona_note": contact["persona_note"] if contact["persona_note"] else None,
        },
        "local_time": {
            "iso": now.isoformat(),
            "hour": now.hour,
            "is_quiet_hours": is_quiet_hours(now),
        }
    }
    return context

# --- LUCY ON CLAUDE (backend == 'claude') ---

BRAIN_TIMEOUT_SECONDS = 120

OUTPUT_INSTRUCTION = (
    "Output ONLY a single JSON object with EXACTLY these keys: "
    "action_type, confidence, message_to_oscar, rationale, evidence, "
    "suggested_customer_message, estimate_readiness, send_decision, "
    "language, memory_facts_used, escalate_oscar, escalation_reason, "
    "followup_date. "
    "language = ISO code of the language you wrote the customer message in "
    "(\"en\", \"es\", ...); use \"\" if there is no customer message. "
    "memory_facts_used = list of the specific prior facts you used this turn "
    "(e.g. [\"package=gold\", \"price=451\"]); [] if none. "
    "escalate_oscar = boolean true when this needs Oscar (do-not-contact request, "
    "legal/refund/safety, or anything you should not handle autonomously); else false. "
    "escalation_reason = short string naming why; \"\" when escalate_oscar is false. "
    "followup_date = canonical YYYY-MM-DD resolved from the customer's stated timeline "
    "relative to local_time (e.g. \"ready in January\", \"in 3 weeks\"); \"\" when no "
    "timeline is stated. Do NOT invent a date when none is implied. "
    "No prose, no markdown fences."
)

# Fields the harness records for scoring but must NEVER reach the model.
_CHEAT_FIELDS = ("expected_behavior", "persona_note")


def _redact_tokens(text: str) -> str:
    # Best-effort scrub of token/key-like substrings before surfacing an error string.
    text = re.sub(r"sk-[A-Za-z0-9_\-]+", "[REDACTED]", text)
    text = re.sub(r"[A-Za-z0-9_\-]{24,}", "[REDACTED]", text)
    return text


def _model_facing_context(context: Dict[str, Any]) -> Dict[str, Any]:
    # A copy of the harness context with cheat fields removed (no mutation of the original).
    safe = copy.deepcopy(context)
    if isinstance(safe.get("current_event"), dict):
        safe["current_event"].pop("expected_behavior", None)
    if isinstance(safe.get("contact_details"), dict):
        safe["contact_details"].pop("persona_note", None)
    return safe


def _infer_result(
    action_type: str = ActionType.NO_ACTION.value,
    confidence: Any = Confidence.LOW.value,
    message_to_oscar: str = "",
    rationale: str = "",
    evidence: Optional[List[str]] = None,
    suggested_customer_message: Optional[str] = None,
    estimate_readiness: Optional[int] = None,
    send_decision: str = "silent",
    language: str = "",
    memory_facts_used: Optional[List[str]] = None,
    escalate_oscar: bool = False,
    escalation_reason: str = "",
    followup_date: str = "",
    usage: Any = None,
    cost_usd: Any = None,
    error: str = "",
) -> Dict[str, Any]:
    # A dict in the exact Step-0 shape the downstream Recommendation parser consumes.
    # (usage/cost_usd/error are extra metadata; downstream reads keys via .get and ignores them.)
    return {
        "action_type": action_type,
        "confidence": confidence,
        "message_to_oscar": message_to_oscar,
        "rationale": rationale,
        "evidence": list(evidence) if evidence else [],
        "suggested_customer_message": suggested_customer_message,
        "estimate_readiness": estimate_readiness,
        "send_decision": send_decision,
        "language": language,
        "memory_facts_used": list(memory_facts_used) if memory_facts_used else [],
        "escalate_oscar": bool(escalate_oscar),
        "escalation_reason": escalation_reason,
        "followup_date": followup_date,
        "usage": usage,
        "cost_usd": cost_usd,
        "error": error,
    }


def _strip_json_fences(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines).strip()
    return text


def _parse_inner_json(inner: str) -> Optional[dict]:
    try:
        obj = json.loads(_strip_json_fences(inner))
    except (json.JSONDecodeError, ValueError, TypeError):
        return None
    return obj if isinstance(obj, dict) else None


def _run_claude(exe: str, prompt: str) -> subprocess.CompletedProcess:
    # Headless, no tools, no shell. Subscription auth (no API key) by design.
    # encoding="utf-8" is REQUIRED: claude -p emits UTF-8, but text=True alone decodes
    # with the locale codec (cp1252 on Windows), which mangles em-dashes into "â€"".
    return subprocess.run(
        [exe, "-p", "--output-format", "json", "--allowedTools", "", "--max-turns", "2"],
        input=prompt, capture_output=True, encoding="utf-8", errors="replace",
        timeout=BRAIN_TIMEOUT_SECONDS,
    )


# Lucy's brain model (Decision #1). Used by the metered API backend (#6/#13 production brain).
ANTHROPIC_MODEL = "claude-sonnet-4-6"


def _infer_claude_api(context: Dict[str, Any], api_key: str) -> Dict[str, Any]:
    """Metered Anthropic Messages API inference path (Decision #6/#13 production brain).

    Byte-for-byte the same prompt and JSON parsing as _infer_claude (the OAuth claude -p
    path), but calls the Messages API on the metered key instead of the subscription CLI.
    SYSTEM_PROMPT rides as `system`; the rendered event + OUTPUT_INSTRUCTION as the user
    turn. Best-effort; never throws. Same one-retry-on-bad-JSON contract."""
    import anthropic  # local import: only the API backend needs the SDK

    system = SYSTEM_PROMPT
    user = build_user_prompt(_model_facing_context(context)) + "\n\n" + OUTPUT_INSTRUCTION
    for cheat in _CHEAT_FIELDS:
        if cheat in system or cheat in user:
            raise RuntimeError(f"prompt leakage: '{cheat}' present in assembled prompt")

    try:
        client = anthropic.Anthropic(api_key=api_key)

        def _call(extra: str = ""):
            msg = client.messages.create(
                model=ANTHROPIC_MODEL,
                max_tokens=2048,
                system=system,
                messages=[{"role": "user", "content": user + extra}],
            )
            text = "".join(
                getattr(b, "text", "") for b in msg.content if getattr(b, "type", "") == "text"
            )
            return text, getattr(msg, "usage", None)

        inner, usage = _call()
    except Exception as e:  # transport / auth / rate-limit — surface, never crash the loop
        return _infer_result(message_to_oscar=_redact_tokens(str(e)), error="api_error")

    rec = _parse_inner_json(inner)
    if rec is None:
        try:
            inner, usage = _call("\n\nReturn ONLY valid JSON, nothing else.")
            rec = _parse_inner_json(inner)
        except Exception:
            rec = None
    if rec is None:
        return _infer_result(message_to_oscar="model did not return valid JSON", error="bad_json")

    try:
        ActionType(rec.get("action_type"))
    except ValueError:
        return _infer_result(message_to_oscar="invalid action_type from model", error="bad_action_type")

    usage_d = None
    if usage is not None:
        usage_d = {
            "input_tokens": getattr(usage, "input_tokens", None),
            "output_tokens": getattr(usage, "output_tokens", None),
        }
    return _infer_result(
        action_type=rec.get("action_type"),
        confidence=rec.get("confidence"),
        message_to_oscar=rec.get("message_to_oscar", ""),
        rationale=rec.get("rationale", ""),
        evidence=rec.get("evidence", []),
        suggested_customer_message=rec.get("suggested_customer_message"),
        estimate_readiness=rec.get("estimate_readiness"),
        send_decision=rec.get("send_decision", "silent"),
        language=rec.get("language", ""),
        memory_facts_used=rec.get("memory_facts_used", []),
        escalate_oscar=bool(rec.get("escalate_oscar", False)),
        escalation_reason=rec.get("escalation_reason", ""),
        followup_date=rec.get("followup_date", ""),
        usage=usage_d,
        cost_usd=None,
        error="",
    )


def _infer_claude(context: Dict[str, Any]) -> Dict[str, Any]:
    # a) PROMPT — render the event the way the harness shows the model, minus cheat fields.
    prompt = (
        SYSTEM_PROMPT
        + "\n\n"
        + build_user_prompt(_model_facing_context(context))
        + "\n\n"
        + OUTPUT_INSTRUCTION
    )
    for cheat in _CHEAT_FIELDS:
        if cheat in prompt:
            raise RuntimeError(f"prompt leakage: '{cheat}' present in assembled prompt")

    # b) INVOKE — resolve the Windows .cmd shim explicitly; no shell.
    exe = shutil.which("claude")
    if not exe:
        return _infer_result(message_to_oscar="claude not on PATH", error="claude not on PATH")

    try:
        proc = _run_claude(exe, prompt)
    except subprocess.TimeoutExpired:
        return _infer_result(message_to_oscar="claude -p timed out", error="timeout")

    # c) PARSE — envelope first, then the model's inner JSON (one retry on bad inner JSON).
    if proc.returncode != 0:
        err_lines = (proc.stderr or "").strip().splitlines()
        msg = _redact_tokens(err_lines[0]) if err_lines else "claude -p returned nonzero"
        return _infer_result(message_to_oscar=msg, error=msg)

    try:
        envelope = json.loads(proc.stdout)
    except (json.JSONDecodeError, ValueError):
        return _infer_result(message_to_oscar="bad claude -p envelope", error="bad_envelope")

    inner = envelope.get("result", "")
    usage = envelope.get("usage")
    cost_usd = envelope.get("total_cost_usd")

    rec = _parse_inner_json(inner)
    if rec is None:
        try:
            proc = _run_claude(exe, prompt + "\n\nReturn ONLY valid JSON, nothing else.")
            if proc.returncode == 0:
                envelope = json.loads(proc.stdout)
                inner = envelope.get("result", "")
                usage = envelope.get("usage")
                cost_usd = envelope.get("total_cost_usd")
                rec = _parse_inner_json(inner)
        except (subprocess.TimeoutExpired, json.JSONDecodeError, ValueError):
            rec = None
    if rec is None:
        return _infer_result(message_to_oscar="model did not return valid JSON", error="bad_json")

    # Validate: action_type must be a valid ActionType value.
    try:
        ActionType(rec.get("action_type"))
    except ValueError:
        return _infer_result(message_to_oscar="invalid action_type from model", error="bad_action_type")

    # d) RETURN — map rec into the exact Step-0 shape; error="" on success.
    return _infer_result(
        action_type=rec.get("action_type"),
        confidence=rec.get("confidence"),
        message_to_oscar=rec.get("message_to_oscar", ""),
        rationale=rec.get("rationale", ""),
        evidence=rec.get("evidence", []),
        suggested_customer_message=rec.get("suggested_customer_message"),
        estimate_readiness=rec.get("estimate_readiness"),
        send_decision=rec.get("send_decision", "silent"),
        language=rec.get("language", ""),
        memory_facts_used=rec.get("memory_facts_used", []),
        escalate_oscar=bool(rec.get("escalate_oscar", False)),
        escalation_reason=rec.get("escalation_reason", ""),
        followup_date=rec.get("followup_date", ""),
        usage=usage,
        cost_usd=cost_usd,
        error="",
    )


def infer(
    context: Dict[str, Any],
    backend: str,
    claude_api_key: Optional[str] = None,
    gemini_api_key: Optional[str] = None,
) -> Dict[str, Any]:
    # Production brain (Decision #6/#13): metered Anthropic Messages API on claude-sonnet-4-6.
    if backend == "api":
        key = claude_api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not key:
            return _infer_result(message_to_oscar="no API key for backend=api", error="no_api_key")
        return _infer_claude_api(context, key)
    # Testing engine: Lucy runs on Claude via headless `claude -p` (OAuth subscription).
    if backend == "claude":
        return _infer_claude(context)
    # backend == 'gemini' (Harness B — dead): original stub left intact, not implemented.
    return {
        "action_type": ActionType.NO_ACTION.value,
        "confidence": Confidence.LOW.value, # Corrected: use string value
        "message_to_oscar": "NOT_BUILT - infer function stub",
        "rationale": "Stubbed inference, no action taken.",
        "evidence": ["stub"],
        "suggested_customer_message": "",
        "estimate_readiness": 0,
        "send_decision": "silent",
        "track": Track.NURTURE.value, # Added, for completeness of Recommendation parsing
        "behavior": Behavior.RECOMMEND.value, # Added
        "would_be": Behavior.RECOMMEND.value, # Added
        "suppressed": False, # Added
        "phase": 1, # Added
    }


def update_lead_state(
    lead_state: LeadState,
    event: Dict[str, str],
    recommendation: Recommendation,
    now_timestamp: float,
    contact_name: str, # From contact data
) -> LeadState:
    # Create a mutable copy using deepcopy to preserve nested dataclass instances
    new_state = copy.deepcopy(lead_state)

    # Update contact name if not set
    if new_state.contact_name is None:
        new_state.contact_name = contact_name

    # Update created_ts if not set
    if new_state.created_ts is None:
        new_state.created_ts = now_timestamp

    # Update last_contact_ts for all events (assuming any event counts as contact)
    new_state.last_contact_ts = now_timestamp

    # Add customer message if inbound_reply
    if event["event_type"] == "inbound_reply" and event["inbound_text"]:
        new_state.messages.append(Message(
            ts=now_timestamp,
            sender="customer",
            text=event["inbound_text"]
        ))

    # Add shop message if suggested_customer_message exists and is sent
    if recommendation.suggested_customer_message and recommendation.send_decision == "send_now":
        new_state.messages.append(Message(
            ts=now_timestamp,
            sender="shop",
            text=recommendation.suggested_customer_message
        ))

    # Update status based on action type or event type (simplified for now)
    if recommendation.action_type == ActionType.MARK_ESTIMATE_READY:
        new_state.status = LeadStatus.ESTIMATE_READY
    elif event["event_type"] == "job_complete":
        new_state.status = LeadStatus.WON # Assuming job complete means won
    elif event["event_type"] == "review_received":
        # Status might not change for a review, just add message
        pass
    elif event["event_type"] == "invoice_paid":
        # Status might not change for invoice paid, just add message
        pass
    elif event["event_type"] == "estimate_ready":
        new_state.status = LeadStatus.ESTIMATE_READY # Or in_intake if not already
    elif event["event_type"] == "booking_created":
        new_state.status = LeadStatus.IN_INTAKE # Or stay estimate_ready/new etc.
    elif event["event_type"] == "booking_rescheduled":
        new_state.status = LeadStatus.IN_INTAKE # Or stay estimate_ready/new etc.
    # Add more state transition logic as needed based on Hermy's actual rules

    # Update known facts, objections, tags based on LLM recommendation rationale/evidence (if applicable)
    # This part needs to be more explicitly defined in the Recommendation output if LLM is meant to change these

    return new_state


def enforce_inbound_timing(
    recommendation: Recommendation,
    raw_llm_output: Dict[str, Any],
) -> Recommendation:
    # Deterministic floor for customer-initiated events; the model's timing choice is ignored.
    # An inbound must end as EITHER a real reply (send_now) OR an escalation to Oscar — never
    # silent. Escalation triggers: already-escalated upstream, inference error, or an
    # empty/blank customer draft (a non-response).
    if recommendation.send_decision == ESCALATE_HUMAN:
        return recommendation  # already escalated upstream (e.g. parse-error fallback)

    if raw_llm_output.get("error"):
        recommendation.send_decision = ESCALATE_HUMAN
        recommendation.behavior = Behavior.RECOMMEND
        recommendation.suppressed = False
        recommendation.escalate_oscar = True
        recommendation.escalation_reason = recommendation.escalation_reason or "inbound inference failed"
        recommendation.message_to_oscar = (
            "ALERT OSCAR — human needed (inbound inference failed): "
            + (raw_llm_output.get("error") or "unknown error")
        )
        return recommendation

    if not (recommendation.suggested_customer_message or "").strip():
        # Inbound produced no customer reply -> treat as a non-response, escalate (never silent).
        recommendation.send_decision = ESCALATE_HUMAN
        recommendation.behavior = Behavior.RECOMMEND
        recommendation.suppressed = False
        recommendation.escalate_oscar = True
        recommendation.escalation_reason = recommendation.escalation_reason or "empty inbound reply"
        recommendation.message_to_oscar = (
            recommendation.message_to_oscar
            or "ALERT OSCAR — human needed (empty inbound reply): model returned no customer message."
        )
        return recommendation

    recommendation.send_decision = "send_now"
    return recommendation


def _seed_messages_from_history(history: List[Dict[str, Any]], now_ts: float) -> List[Message]:
    # Replay a conversation history (oldest->newest) VERBATIM into LeadState.messages.
    # customer -> sender "customer"; lucy -> sender "shop". Prior turns are seeded as-is;
    # they are NOT re-scored or regenerated. ts uses the entry's value when parseable, else
    # falls back to now_ts (transcript() preserves list order regardless of ts).
    msgs: List[Message] = []
    for h in history or []:
        who = (h.get("from") or "").strip().lower()
        text = str(h.get("text") or "")
        sender = "customer" if who == "customer" else "shop"
        raw_ts = h.get("ts")
        try:
            ts = float(raw_ts)
        except (TypeError, ValueError):
            try:
                ts = to_timestamp(str(raw_ts))
            except (ValueError, TypeError):
                ts = now_ts
        msgs.append(Message(ts=ts, sender=sender, text=text))
    return msgs


def run_bakeoff(
    contacts_csv_string: str,
    events_csv_string: str,
    backend: str,
    claude_api_key: Optional[str] = None,
    gemini_api_key: Optional[str] = None,
    num_smoke_test_events: int = 12,
    seed_history: Optional[Dict[str, List[Dict[str, Any]]]] = None,
) -> Dict[str, Any]:
    # No-key guard (OAuth path only): refuse to run the `claude` (claude -p subscription)
    # backend if a metered API key is present — it would silently switch that to metered
    # billing. The `api` backend (Decision #6/#13 production brain) INTENTIONALLY uses the
    # metered key, so the guard does not apply there.
    if backend != "api" and os.environ.get("ANTHROPIC_API_KEY"):
        raise SystemExit("ANTHROPIC_API_KEY is set — refusing to run (would switch claude -p to metered billing).")

    contacts_data = parse_csv(contacts_csv_string)
    events_data = parse_csv(events_csv_string)

    contacts_lookup = {c['contact_id']: c for c in contacts_data}
    events_data.sort(key=lambda x: to_timestamp(x['scheduled_at']))

    all_results = []
    lead_states: Dict[str, LeadState] = {}

    processed_event_count = 0
    for event in events_data:
        if num_smoke_test_events and processed_event_count >= num_smoke_test_events:
            break

        contact_id = event['contact_id']
        contact = contacts_lookup.get(contact_id)
        if not contact:
            print(f"Warning: Contact {contact_id} not found for event {event['event_id']}")
            continue

        first_seen = contact_id not in lead_states
        current_lead_state = lead_states.setdefault(contact_id, LeadState(
            lead_id=contact_id,
            contact_name=f"{contact['first_name']} {contact['last_name']}"
        ))
        # Seam 1: pre-seed prior conversation VERBATIM (only on this contact's first event,
        # before any scoring). Default seed_history={} -> byte-unchanged for controls.py.
        if first_seen and seed_history and seed_history.get(contact_id):
            now_for_seed = to_timestamp(event['scheduled_at'])
            current_lead_state.messages = _seed_messages_from_history(
                seed_history[contact_id], now_for_seed) + current_lead_state.messages

        now = datetime.fromisoformat(event['scheduled_at'])
        # Corrected timezone handling
        if now.tzinfo is None:
            now = NY_TZ.localize(now)
        else:
            now = now.astimezone(NY_TZ)

        now_timestamp = now.timestamp()

        # --- BUILD CONTEXT (BYTE-IDENTICAL) ---
        context = build_context(contact, current_lead_state, event, now)
        context_json_bytes = json.dumps(context, sort_keys=True, indent=2).encode('utf-8')
        context_hash = hashlib.sha256(context_json_bytes).hexdigest()

        # --- DETERMINISTIC GATE LAYER ---
        is_inbound = event["event_type"] in INBOUND_EVENT_TYPES

        # --- INFER (SWAP POINT) ---
        raw_llm_output = infer(context, backend, claude_api_key, gemini_api_key)
        # print(f"DEBUG: Raw LLM Output for event {event['event_id']}: {raw_llm_output}") # Debug print

        # Validate and parse LLM output into Recommendation
        try:
            recommendation = Recommendation(
                lead_id=contact_id,
                track=Track(raw_llm_output.get("track", Track.NURTURE.value)),
                action_type=ActionType(raw_llm_output.get("action_type", ActionType.NO_ACTION.value)),
                confidence=Confidence(raw_llm_output.get("confidence", Confidence.LOW.value)),
                score=0.1, # Fixed score for stubbed infer function
                behavior=Behavior(raw_llm_output.get("behavior", Behavior.RECOMMEND.value)),
                would_be=Behavior(raw_llm_output.get("would_be", Behavior.RECOMMEND.value)),
                message_to_oscar=raw_llm_output.get("message_to_oscar", "No message to Oscar"),
                rationale=raw_llm_output.get("rationale", ""), 
                evidence=list(raw_llm_output.get("evidence", [])),
                suggested_customer_message=raw_llm_output.get("suggested_customer_message"),
                estimate_readiness=raw_llm_output.get("estimate_readiness"),
                suppressed=raw_llm_output.get("suppressed", False),
                suppressed_reason=raw_llm_output.get("suppressed_reason"),
                send_decision=raw_llm_output.get("send_decision", "silent"),
                language=raw_llm_output.get("language", ""),
                memory_facts_used=list(raw_llm_output.get("memory_facts_used", [])),
                escalate_oscar=bool(raw_llm_output.get("escalate_oscar", False)),
                escalation_reason=raw_llm_output.get("escalation_reason", ""),
                followup_date=raw_llm_output.get("followup_date", ""),
                phase=raw_llm_output.get("phase", 1),
                created_ts=now_timestamp,
            )
        except Exception as e:
            print(f"Error parsing LLM output for event {event['event_id']}: {e}")
            if is_inbound:
                # Never silent-drop an inbound; escalate to a human (loud row).
                recommendation = Recommendation(
                    lead_id=contact_id, track=Track.NURTURE, action_type=ActionType.NO_ACTION,
                    confidence=Confidence.LOW, score=0.0, behavior=Behavior.RECOMMEND, would_be=Behavior.RECOMMEND,
                    message_to_oscar=f"ALERT OSCAR — human needed (inbound parse error): {e}",
                    rationale="Parse error on inbound", evidence=[], send_decision=ESCALATE_HUMAN)
            else:
                recommendation = Recommendation(
                    lead_id=contact_id, track=Track.NURTURE, action_type=ActionType.NO_ACTION,
                    confidence=Confidence.LOW, score=0.0, behavior=Behavior.SUPPRESS, would_be=Behavior.SUPPRESS,
                    message_to_oscar=f"LLM output parse error: {e}", rationale="Parse error", evidence=[])

        # Deterministic inbound timing override (after parsing, before state update).
        if is_inbound:
            recommendation = enforce_inbound_timing(recommendation, raw_llm_output)

        # --- DETERMINISTIC STATE UPDATE ---
        updated_lead_state = update_lead_state(
            current_lead_state,
            event,
            recommendation,
            now_timestamp,
            contact_name=f"{contact['first_name']} {contact['last_name']}"
        )
        lead_states[contact_id] = updated_lead_state

        # --- SCORING (STUBBED FOR NOW) ---
        # Deterministic checks: quiet_hours_respected, estimate_amount_ok, action_type_sane, message_present_expected
        quiet_hours_respected = "NOT_BUILT"
        estimate_amount_ok = "NOT_BUILT"
        action_type_sane = "NOT_BUILT"
        message_present_expected = "NOT_BUILT"
        judge_score = "NOT_BUILT"

        all_results.append({
            "event_id": event["event_id"],
            "contact_id": contact_id,
            "scheduled_at": event["scheduled_at"],
            "local_time": now.isoformat(),
            "is_quiet_hours": is_quiet_hours(now),
            "backend": backend,
            "context_hash": context_hash,
            "llm_raw_output": raw_llm_output, # For debugging
            "recommendation": recommendation.to_dict(),
            "final_lead_state": asdict(updated_lead_state), # Final state after this event
            "scoring": {
                "quiet_hours_respected": quiet_hours_respected,
                "estimate_amount_ok": estimate_amount_ok,
                "action_type_sane": action_type_sane,
                "message_present_expected": message_present_expected,
                "judge_score": judge_score,
                "expected_behavior": event["expected_behavior"]
            }
        })
        processed_event_count += 1

    return {
        "results": all_results,
        "final_lead_states": {k: asdict(v) for k, v in lead_states.items()}
    }

# --- MAIN EXECUTION BLOCK (FOR DIRECT TESTING) ---
# This block will be used by execute_code to run the harness.
# It expects `contacts_csv_string` and `events_csv_string` to be provided.
# For initial smoke test, we'll use a small inline sample.
if __name__ == '__main__':
    # Placeholder for actual CSV data provided by the user
    sample_contacts_csv = """
contact_id,first_name,last_name,phone,city,service,package,estimate_amount,tags,persona_note
C001,Rosa,Cruz,+123****2474,Cape Coral,tub_refinish,gold,451,,Retired librarian, meticulous, reads every word of the estimate.
C355,Jane,Doe,+123****7890,Naples,shower_stall,silver,500,snowbird,Early bird planner, always makes decisions quickly.
C378,John,Smith,+198****4321,Fort Myers,tub_refinish,platinum,1200,,Needs urgent repair, very responsive.
"""

    # Smoke test events, including off-hours event
    sample_events_csv = """
event_id,contact_id,arc_step,event_type,scheduled_at,inbound_text,expected_behavior
E0001,C355,step1,inbound_reply,2026-06-15T10:00:00-04:00,"We'd like to go ahead with the silver package.",Respond helpfully…
E0002,C001,step1,estimate_ready,2026-06-15T15:30:00-04:00,"",Deliver the gold package estimate of $451 for tub_refinish and invite to book…
E0003,C378,step1,estimate_ready,2026-06-15T22:00:00-04:00,"",Deliver the platinum package estimate of $1200 for tub_refinish and invite to book…
E0004,C355,step2,job_complete,2026-06-16T11:00:00-04:00,"",Congratulate on completion and invite a Google review.
E0005,C001,step2,inbound_reply,2026-06-16T02:00:00-04:00,"Can you tell me more about the warranty?",Answer warranty question.
E0006,C378,step2,inbound_reply,2026-06-16T09:00:00-04:00,"I need to reschedule the booking.",Acknowledge reschedule, confirm new date/time, reassure.
E0007,C355,step3,review_received,2026-06-17T14:00:00-04:00,"",Thank for the review and express appreciation.
E0008,C001,step3,booking_created,2026-06-17T07:00:00-04:00,"",Confirm the booking details and what to expect on the day.
E0009,C378,step3,invoice_paid,2026-06-17T18:00:00-04:00,"",Thank for payment and confirm the job is fully settled.
E0010,C355,step4,estimate_ready,2026-06-18T00:30:00-04:00,"",This is a new estimate for C355 for a different service. Deliver bronze package for shower_tile and invite to book.
E0011,C001,step4,booking_rescheduled,2026-06-18T10:00:00-04:00,"",Acknowledge reschedule, confirm new date/time, reassure.
E0012,C378,step4,inbound_reply,2026-06-18T16:00:00-04:00,"When can you do the job?",Provide booking availability.
"""

    # Backend can be 'claude' or 'gemini'. For smoke test, use 'claude' or a stub.
    # Claude API key would typically be from .env (os.getenv('ANTHROPIC_API_KEY'))
    # Gemini API key would typically be from .env (os.getenv('GOOGLE_API_KEY'))
    print("Running smoke test with 'claude' backend (infer function is stubbed)...\n")
    smoke_test_results = run_bakeoff(
        contacts_csv_string=sample_contacts_csv,
        events_csv_string=sample_events_csv,
        backend='claude',
        claude_api_key=os.getenv('ANTHROPIC_API_KEY'), # Will be None if not set
        gemini_api_key=os.getenv('GOOGLE_API_KEY'),     # Will be None if not set
        num_smoke_test_events=12
    )

    # Assert context byte-identity - for now, just print the hash for a single event
    # In a real dual-backend run, this would compare hashes from two runs
    if smoke_test_results['results']:
        first_event_context_hash = smoke_test_results['results'][0]['context_hash']
        print(f"Assertion: Context for first event is byte-identical (hash: {first_event_context_hash}) - (currently assumes single backend run)." )
    else:
        print("No events processed to assert context byte-identity.")

    # Print side-by-side table (currently for a single backend)
    print("\n--- Smoke Test Results Table ---")
    print("event_type   | local_time                  | quiet? | backend | send_decision | message             | estimate_ok | action_ok | judge_score | expected_behavior")
    print("-------------|-----------------------------|--------|---------|---------------|---------------------|-------------|-----------|-------------|---------------------")
    for res in smoke_test_results['results']:
        rec = res['recommendation']
        scoring = res['scoring']
        msg = (rec['suggested_customer_message'] or rec['message_to_oscar'] or "").replace('\n', ' ').strip()[:18] + '...'
        print(f"{res['event_id'][:10]:<12} | {res['local_time'][:25]:<27} | {str(res['is_quiet_hours']):<6} | {res['backend'][:7]:<7} | {rec['send_decision'][:12]:<13} | {msg:<19} | {str(scoring['estimate_amount_ok']):<11} | {str(scoring['action_type_sane']):<9} | {str(scoring['judge_score']):<11} | {scoring['expected_behavior'][:18]}...")

    print("\n--- Final Lead States (for smoke test contacts) ---")
    for contact_id, final_state in smoke_test_results['final_lead_states'].items():
        print(f"Contact ID: {contact_id}")
        print(f"  Status: {final_state['status']}")
        print(f"  Messages: {len(final_state['messages'])} (last: {final_state['messages'][-1]['text'][:30]}...)" if final_state['messages'] else "  Messages: 0")
        print(f"  Known: {final_state['known']}")
        print(f"  Tags: {final_state['tags']}")
        print()
