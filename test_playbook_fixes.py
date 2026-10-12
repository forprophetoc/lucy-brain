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
        "the advertised $299 starting price is for a standard tub; a one-piece tub/shower combo is a "
        "different job, so its price is the customer's own estimate.",
        "give exactly that explanation (no other reason), and hold their estimate: no discount, no new number.",
    ],
}

REMOVED = [
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
