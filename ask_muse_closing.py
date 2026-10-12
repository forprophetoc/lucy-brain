#!/usr/bin/env python3
"""
ask_muse_closing.py — ONE direct call to muse-spark-1.3 (Standard tier): Lucy's current full system prompt
(regular variant) as context + the architect's closing request. Saves the full answer to MUSE_CLOSING_ADVICE.md.
The key is read from the MUSE_API_KEY line only (baseline_scenarios.load_keys) and never printed.

Run: py -3.14 ask_muse_closing.py
"""
import json
import os
import sys
import urllib.error
import urllib.request

import harness
from baseline_scenarios import load_keys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "MUSE_CLOSING_ADVICE.md")

REQUEST = """This sales-first approach for Lucy was your idea -- you know how to sell, so write her the way you would sell. In testing you (as Lucy) are warm, human and accurate, but you don't close: you answer and end with 'any questions, just text me' instead of moving the customer toward booking. The owner wants Lucy to sell the way he does: answer fully, be honest, never pushy, and end with ONE clear next step toward booking (the booking link or a direct scheduling question). Here is a real conversation of his:
BONNIE: I received it but considerably more than on line prices. I will be using the tub to soak so will that still hold up?
BONNIE: I'm getting two estimates and hubby would want to talk about what you actually do as we would do but health issues won't permit right now
OWNER: The gold package will hold up to anything. The silver package will wear much faster than the gold. Also, you cannot use any essential oil or bath bombs in any refinished tub. Mine or others. We have an iso free option that will not leave any harmful fumes behind. This case is EXACTLY why we offer an iso free option. Bonnie, if you show me a cheaper price online, and it's within reason, I will honor it. Truth- I doubt you will find one for a one piece tub/shower combo.
BONNIE: Not trying to offend I but the price I was referring to was on this ad I responded to. Also have a question can I have shower in white color but tub/combo in a beige/tan color? Also tub has 4 screws holding a grab bar can I remove and will those be covered up?
OWNER: No problem. The price on the ad says most tubs start at 299. Neither of yours are tubs!! And yes, we carry the same color it is now. That's Kohler Biscuit. A very light tan. And we fill any nicks or chips or screw holes before refinish, remove any old caulking and replace with new as well. Any other questions I can answer for you?
(The price match is the owner's only -- Lucy has no discount power except veteran 10% / senior 5%. Hole-filling and caulk replacement are Gold and above only.)
Answer: 1) what instructions/examples in your system prompt would make you consistently end with a booking step without sounding salesy; 2) whether to use real texts as few-shot examples, how many, what format; 3) when NOT to push for booking; 4) the exact playbook lines to add -- tone and closing behavior only, no facts, prices, rules or discounts changed."""


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    load_keys()
    key = os.environ.get("MUSE_API_KEY")
    if not key:
        raise SystemExit("no MUSE_API_KEY line found — HOLD")
    os.environ.pop("HC_VARIANT", None)
    system_prompt = harness._prompts()[0]  # regular variant, as Lucy runs today
    user = ("Below is Lucy's current full system prompt, between the markers, as context. Do not act as Lucy; "
            "answer the request that follows it as yourself.\n\n=== LUCY SYSTEM PROMPT START ===\n"
            f"{system_prompt}\n=== LUCY SYSTEM PROMPT END ===\n\n{REQUEST}")
    body = json.dumps({
        "model": harness.MUSE_MODEL,
        "messages": [{"role": "user", "content": user}],
        "reasoning_effort": "medium",
        "max_completion_tokens": 8000,
        "stream": False,
    }).encode("utf-8")
    req = urllib.request.Request(harness.MUSE_URL, data=body, method="POST",
                                 headers={"Content-Type": "application/json", "Authorization": f"Bearer {key}"})
    try:
        with urllib.request.urlopen(req, timeout=300) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        raise SystemExit(f"HTTP {e.code}: {harness._redact_tokens(e.read().decode('utf-8', 'replace'))[:500]} — HOLD")
    answer = ((data.get("choices") or [{}])[0].get("message") or {}).get("content") or ""
    if not answer.strip():
        raise SystemExit(f"empty answer — HOLD: {json.dumps(data)[:500]}")
    u = data.get("usage") or {}
    md = ["# Muse closing advice", "",
          f"_One direct call to `{data.get('model') or harness.MUSE_MODEL}` (Standard tier), reasoning_effort medium. "
          f"Context: Lucy's full regular system prompt ({len(system_prompt):,} chars) + the architect's request. "
          f"Tokens: {u.get('prompt_tokens')} in / {u.get('completion_tokens')} out. Saved verbatim below._", "",
          "## Request sent (after the system prompt)", "", "```text", REQUEST, "```", "",
          "## Muse's answer (verbatim)", "", answer.strip(), ""]
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write("\n".join(md))
    print(f"written: {OUT}  ({len(answer)} chars)")


if __name__ == "__main__":
    main()
