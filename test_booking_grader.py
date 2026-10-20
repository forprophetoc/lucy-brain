#!/usr/bin/env python3
"""
test_booking_grader.py — grader tests for booking_scenarios (no network, no model):
every booking check is pinned with a hand-written GOOD reply (passes) and a BAD reply
(fails), and the full hard rule set is inherited (an invented price hard-fails).

Run: py -3.14 -m unittest test_booking_grader -v
"""
import unittest

import booking_scenarios as K

S = K.BY_ID

GOOD = ("Mia, thank you for the business — we sincerely appreciate it! Here's the booking link with the "
        "dates available: https://calendar.bathtubpros.com — once you fill in your info, the appointment "
        "is set. I'll text you a reminder the day before and again when we're on our way. Thanks again, Mia!")


def resp(reply, decision="send_now"):
    return {"reply": reply, "send_decision": decision, "facts": {}, "error": ""}


class BookingGrader(unittest.TestCase):
    def test_good_passes_everything(self):
        g = K.grade(S["BOK1"], resp(GOOD))
        for k, v in g["rules"].items():
            self.assertTrue(v["pass"], f"{k}: {v}")
        self.assertTrue(g["all_pass"])

    def test_thank_you_must_be_first(self):
        bad = ("Excellent! Here's the booking link with the dates available: https://calendar.bathtubpros.com "
               "— once you fill in your info, the appointment is set. And Mia, thank you for the business! "
               "I'll text a reminder the day before and again when we're on our way.")
        g = K.grade(S["BOK1"], resp(bad))
        self.assertFalse(g["rules"]["thank_you_first"]["pass"])

    def test_one_word_opener_is_not_the_first_sentence(self):
        """"Excellent! First and foremost, thank you for the business…" passes — the opener is
        an interjection; every live reply opens this way."""
        good = ("Excellent! First and foremost, thank you for the business, Mia — we sincerely appreciate it. "
                "Here's the booking link: https://calendar.bathtubpros.com\n\nOnce you fill in your info your "
                "appointment is set. We'll text a reminder the day before and again when we're on our way. "
                "Thanks again, Mia!")
        g = K.grade(S["BOK1"], resp(good))
        self.assertTrue(g["rules"]["thank_you_first"]["pass"], g["rules"]["thank_you_first"])

    def test_no_thank_you_at_all_fails(self):
        bad = ("Here's the booking link: https://calendar.bathtubpros.com — grab any open date. I'll text a "
               "reminder the day before and again when we're on our way, Mia.")
        g = K.grade(S["BOK1"], resp(bad))
        self.assertFalse(g["rules"]["thank_you_first"]["pass"])

    def test_booking_link_required(self):
        bad = ("Mia, thank you for the business! Once you fill in your info the appointment is set — I'll text "
               "a reminder the day before and again when we're on our way.")
        g = K.grade(S["BOK1"], resp(bad))
        self.assertFalse(g["rules"]["booking_link"]["pass"])

    def test_reminder_line_required(self):
        bad = ("Mia, thank you for the business! Here's the booking link: https://calendar.bathtubpros.com — "
               "once you fill in your info, the appointment is set. Talk soon!")
        g = K.grade(S["BOK1"], resp(bad))
        self.assertFalse(g["rules"]["reminder_promised"]["pass"])
        self.assertFalse(g["rules"]["on_our_way_promised"]["pass"])

    def test_name_required(self):
        bad = ("Thank you for the business! Here's the booking link with the dates available: "
               "https://calendar.bathtubpros.com — once you fill in your info, the appointment is set. "
               "I'll text a reminder the day before and again when we're on our way.")
        g = K.grade(S["BOK1"], resp(bad))
        self.assertFalse(g["rules"]["name_used"]["pass"])

    def test_hard_rules_inherited(self):
        bad = resp(GOOD + " Just $399!")
        g = K.grade(S["BOK1"], bad)
        self.assertIn("no_invented_price", g["hard_fails"])
        self.assertFalse(g["all_pass"])

    def test_bok3_good_with_customer_named_time(self):
        good3 = ("Sarah, thank you for the business — we sincerely appreciate it! The 9:30 on the 15th is in "
                 "your booking link here: https://calendar.bathtubpros.com — once you fill in your info, the "
                 "appointment is set. I'll text a reminder the day before and again when we're on our way. "
                 "Thanks again, Sarah!")
        g = K.grade(S["BOK3"], resp(good3))
        for k, v in g["rules"].items():
            self.assertTrue(v["pass"], f"{k}: {v}")
        # a time the CUSTOMER named is not an invented appointment time
        self.assertNotIn("no_invented_appt_time", g["hard_fails"])

    def test_requests_have_availability_only_where_specified(self):
        self.assertNotIn("availability", K.build_request(S["BOK1"]))
        req3 = K.build_request(S["BOK3"])
        self.assertEqual(req3["availability"], S["BOK3"]["availability"])
        self.assertEqual(req3["now_et"], K.NOW_ET)


if __name__ == "__main__":
    unittest.main()
