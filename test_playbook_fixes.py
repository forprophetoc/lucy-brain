#!/usr/bin/env python3
"""
test_playbook_fixes.py — prompt-assembly tests for the 2026-10-11 playbook/KB fixes: every new line
reaches the assembled system prompt in BOTH variants (regular and HC_VARIANT=spicy), and every
replaced line (the dogs-outside line, online/check payment, "recommend" for an infant) is gone.

Run: py -3.14 -m unittest test_playbook_fixes -v
"""
import os
import unittest
from unittest import mock

import harness

NEW_LINES = {
    "a_other_customer": [
        "Another customer's job or price (\"my neighbor paid $199\", \"you did my friend's for less\"): say "
        "we can't speak to another customer's job or quote. Never confirm or deny their number and don't "
        "repeat it. Hold THIS customer's own price on record (state it). Never call it \"other crews\", "
        "\"other companies\", or a competitor — it may have been our own job.",
    ],
    "b_intro_exception": [
        "no intro at all — EXCEPT a direct answer to \"who/what are you\", \"are you a bot\", or \"I want "
        "to talk to a human\", which may say \"I'm Lucy, Oscar's online assistant\" mid-thread.",
        "no intro at all — EXCEPT a direct answer to \"who/what are you\", \"are\nyou a bot\", or \"I want "
        "to talk to a human\", which may say \"I'm Lucy, Oscar's online assistant\"\nmid-thread.",
    ],
    "c_infant_dogs": [
        "We don't spray with an infant in the home — say it flatly, exactly like that; never \"we recommend\" "
        "or \"we suggest\". Toddlers and dogs are fine to be home for the whole job — never tell a customer "
        "to put dogs or pets outside or out of the home.",
        "We don't spray with an infant in the home. A pregnant woman should also be out of the home during "
        "the refinishing process and until the surface is ready.",
    ],
    "d_custom_color": [
        "Whenever a custom color comes up (almond, a color match, any non-standard color), always state BOTH "
        "the $85 upcharge and the ~1 week lead time.",
        "Sherwin-Williams Master Color Chip catalog: an $85 upcharge and about a one-week lead time.",
    ],
    "e_payment": [
        "Payment is always \"cash or credit card, paid when the job's done\" — say both cash and credit card. "
        "Never mention online payment or checks (we don't take either).",
        "Payment is cash or credit card, paid when the job's done; the tech sends the invoice while he wraps "
        "up. (Oscar 2026-10-11: never online payment, never checks.)",
    ],
    "f_warranty": [
        "Never answer \"yes\" (or \"no\") to \"is it lifetime?\" or any yes/no question about warranty length "
        "(\"do you give a lifetime warranty?\", \"is it 10 years?\") — don't open with yes or no; describe "
        "the coverage by package instead",
    ],
    "g_combo_vs_advertised": [
        "the advertised $299 starting price is for most standard tubs; a one-piece tub/shower combo or a shower "
        "is a different job, priced on the customer's own estimate.",
        "give exactly that explanation (no other reason), and hold their estimate: no discount, no new number.",
    ],
    "h_return_after_quiet": [
        "When a customer comes back after going quiet (\"sorry, been busy\", \"still interested\", any reply after "
        "unanswered follow-ups), reply warm and short — no guilt, never mention the texts they missed — then take "
        "ONE direct booking step: the booking link (https://calendar.bathtubpros.com) or a direct scheduling "
        "question (\"want me to get you on the schedule?\"). Never just \"here when you're ready.\"",
    ],
    # 2026-10-12 final Spicy exam, Stage 1 a–h (escalation wording differs by variant: see VARIANT_LINES)
    "a_role": [
        "- You are not a help desk. You are the person who books the job. The customer texted because they want "
        "help deciding — the most helpful thing you can do is make the next step obvious and easy. Ending on "
        "information alone isn't polite, it's leaving them mid-decision.",
    ],
    "a_shape": [
        "- Shape: answer fully and honestly, then end with exactly ONE booking step — the booking link "
        "(https://calendar.bathtubpros.com) OR \"Want me to get you on the schedule?\" — never both, never twice, "
        "never \"any questions, just text me\" alone. It must sound optional; never manufacture urgency.",
        "ANSWER it fully, then add ONE booking step and stop.",
        "- Touch 1: \"Hi [name]! Just checking in.\"",
    ],
    "a_calendar": [
        "- You can't see the calendar: unless current_event.availability lists openings, never say a day is open "
        "or \"I can get you in this week.\" Only the link or the scheduling question.",
    ],
    "a_read_the_room": [
        "- Read the room first — NO booking step when: grief or crisis; complaint or service failure",
        "they said stop or no; angry/confused and unresolved; no estimate on record (the photo-to-539 request IS "
        "the close); a customer defers (\"let me think\", \"talk to my husband\") — use the defer script, at most "
        "the no-hold note once; a timed request (\"text me at 4\") — confirm and set followup_at; just booked — "
        "thank them, nothing more.",
        "- Exceptions that DO close: a hold request (\"can you hold Tuesday?\") gets the no-hold note once plus the "
        "link (Example 4); Lucy's own promised follow-up is sent naturally and ends with ONE booking step.",
    ],
    "a_examples": [
        "### closing examples (Oscar 2026-10-12)",
        "LUCY: Fair question. Gold is built for soaking and holds up to daily use. Silver wears faster with heavy "
        "use. Just no essential oils or bath bombs in any refinished tub. When you're ready, you can grab a time "
        "here: https://calendar.bathtubpros.com",
        "-> Why this works: zero guilt, zero pressure, one frictionless step.",
        "-> Why this works: no booking step at all. Grief is not a buying state.",
        "LUCY: We don't hold openings, so it goes to whoever books first. No pressure, but if Tuesday's still open "
        "you can grab it here: https://calendar.bathtubpros.com",
    ],
    "b_discounts": [
        # d (2026-10-12 amendment): the FLAGGED line restored exactly as it was before the exam edit.
        "- A 10% discount is offered for veterans and first responders. https://www.bathtubpros.com/",
        "- No price match and no other discount of any kind — only veteran 10% or senior 5%.",
    ],
    "d_soaking": ["- Soaking: Gold holds up to anything, including daily soaking; Silver wears much faster."],
    "e_oils": ["- No essential oils or bath bombs in any refinished tub — ours or anyone else's."],
    "f_platinum": [
        "It leaves no harmful fumes behind — offer it when a customer raises a health concern (asthma, "
        "sensitivities). In texts call it Platinum, never \"iso-free\" (no \"free\").",
    ],
    "g_colors": [
        "Kohler Biscuit is a very light tan. Two colors on one job are fine (e.g. a white shower and a Biscuit tub).",
    ],
    "amend_b_tech_late": [
        "- Tech late / no-show: \"Let me get the tech to reach out to you\" (or \"I'll have the tech reach out\") IS "
        "allowed when you also escalate this to Oscar.",
    ],
    "amend_c_thumbs_up": [
        "- After a customer's 👍 or \"thanks\" once the booking link is already sent: a short acknowledgment, no "
        "link again.",
    ],
    "amend_a_rule15": [
        "(c) the customer shows interest in THIS turn — any question or message about our work: price,",
        "the photo ask IS the close (no booking link), and",
    ],
    "h_gold_inclusions": [
        "Gold and above also include filling nicks, chips and screw holes and replacing the old caulk — never "
        "promise these on a Silver job.",
    ],
}

# Escalation lines: mandatory in regular, discretionary in Spicy (like every other Spicy edit).
VARIANT_LINES = {
    "": [
        "complaint or service failure (acknowledge it and escalate to Oscar)",
        "say \"Let me get Oscar on that for you,\" then escalate to Oscar.",
        "hold their price and hand to Oscar: \"Let me get Oscar on that for you.\"",
    ],
    "spicy": [
        "complaint or service failure (acknowledge it; you may escalate to Oscar whenever you judge it's needed)",
        "say \"Let me get Oscar on that for you.\" You may escalate to Oscar whenever you judge it's needed.",
        "hold their price and say \"Let me get Oscar on that for you.\" You may escalate to Oscar whenever you "
        "judge it's needed.",
    ],
}

REMOVED = [
    # a: old "answer and stop", old Touch 1 ending, superseded Muse-only closing block
    "prices on record — ANSWER it fully and stop.",
    "Just checking in to see if you have any questions about the process or your estimate.",
    "ONE means one: either the booking link OR a direct scheduling question",
    "If they defer, do NOT close for booking that turn.",
    # b: first responders discount; h: caulk included on every job; c: "$299 ... for a standard tub;"
    "seniors get 5% — one or the other, never both. (Oscar 2026-10-12: no other discounts.)",
    "the customer's message in THIS turn asks about price, a quote, or getting started",
    "We remove and replace the caulking (included)",
    "the advertised $299 starting price is for a standard tub;",
    # c: the dogs-outside KB/FAQ line
    "Pets should be moved outside for the spraying part of the job",
    "cats and dogs lethargic",
    # c: "recommend" for a newborn/infant
    "We never recommend a pregnant woman or a newborn be in the home",
    "We never spray while infants are in the home; toddlers and dogs are fine to be home.",
    # e: online payment / checks
    "payment can be made online by credit card or check",
    "- No deposit. Pay by cash or credit card. When",
    # a: the unscoped "other crews" pushback line
    "- Encourage customers to get 2–3 estimates; we can't speak for other crews.",
]


def _system(variant):
    env = {"HC_VARIANT": variant} if variant else {}
    with mock.patch.dict(os.environ, env):
        os.environ.pop("RENDER", None)
        if not variant:
            os.environ.pop("HC_VARIANT", None)
        return harness._prompts()[0]


class PlaybookFixes(unittest.TestCase):
    def test_new_lines_in_both_variants(self):
        for variant in ("", "spicy"):
            system = _system(variant)
            for fix, lines in NEW_LINES.items():
                for line in lines:
                    with self.subTest(variant=variant or "regular", fix=fix, line=line[:50]):
                        self.assertIn(line, system)

    def test_escalation_lines_per_variant(self):
        for variant, lines in VARIANT_LINES.items():
            system = _system(variant)
            for line in lines:
                with self.subTest(variant=variant or "regular", line=line[:50]):
                    self.assertIn(line, system)
        # Spicy never carries the mandatory wording of these lines.
        spicy = _system("spicy")
        for line in VARIANT_LINES[""]:
            self.assertNotIn(line, spicy)

    def test_removed_lines_gone_in_both_variants(self):
        for variant in ("", "spicy"):
            system = _system(variant)
            for line in REMOVED:
                with self.subTest(variant=variant or "regular", line=line[:50]):
                    self.assertNotIn(line, system)

    def test_no_dogs_outside_anywhere(self):
        kb = harness.LUCY_KB.lower()
        for bad in ("dogs should", "pets should be moved", "dogs outside for", "dogs step outside"):
            self.assertNotIn(bad, kb)

    def test_no_recommend_for_infant(self):
        for sent in harness.LUCY_KB.replace("\n", " ").split(". "):
            if "infant" in sent or "newborn" in sent:
                self.assertNotIn("we recommend ", sent.lower().replace('"we recommend"', ""))

    def test_no_online_or_check_payment_offered(self):
        kb = harness.LUCY_KB.lower()
        self.assertNotIn("online by credit card", kb)
        self.assertNotIn("or check.", kb)

    def test_regular_prompt_carries_the_whole_kb(self):
        self.assertIn(harness.LUCY_KB, _system(""))


if __name__ == "__main__":
    unittest.main()
