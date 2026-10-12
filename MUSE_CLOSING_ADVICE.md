# Muse closing advice

_One direct call to `muse-spark-1.3` (Standard tier), reasoning_effort medium. Context: Lucy's full regular system prompt (34,796 chars) + the architect's request. Tokens: 8990 in / 3560 out. Saved verbatim below._

## Request sent (after the system prompt)

```text
This sales-first approach for Lucy was your idea -- you know how to sell, so write her the way you would sell. In testing you (as Lucy) are warm, human and accurate, but you don't close: you answer and end with 'any questions, just text me' instead of moving the customer toward booking. The owner wants Lucy to sell the way he does: answer fully, be honest, never pushy, and end with ONE clear next step toward booking (the booking link or a direct scheduling question). Here is a real conversation of his:
BONNIE: I received it but considerably more than on line prices. I will be using the tub to soak so will that still hold up?
BONNIE: I'm getting two estimates and hubby would want to talk about what you actually do as we would do but health issues won't permit right now
OWNER: The gold package will hold up to anything. The silver package will wear much faster than the gold. Also, you cannot use any essential oil or bath bombs in any refinished tub. Mine or others. We have an iso free option that will not leave any harmful fumes behind. This case is EXACTLY why we offer an iso free option. Bonnie, if you show me a cheaper price online, and it's within reason, I will honor it. Truth- I doubt you will find one for a one piece tub/shower combo.
BONNIE: Not trying to offend I but the price I was referring to was on this ad I responded to. Also have a question can I have shower in white color but tub/combo in a beige/tan color? Also tub has 4 screws holding a grab bar can I remove and will those be covered up?
OWNER: No problem. The price on the ad says most tubs start at 299. Neither of yours are tubs!! And yes, we carry the same color it is now. That's Kohler Biscuit. A very light tan. And we fill any nicks or chips or screw holes before refinish, remove any old caulking and replace with new as well. Any other questions I can answer for you?
(The price match is the owner's only -- Lucy has no discount power except veteran 10% / senior 5%. Hole-filling and caulk replacement are Gold and above only.)
Answer: 1) what instructions/examples in your system prompt would make you consistently end with a booking step without sounding salesy; 2) whether to use real texts as few-shot examples, how many, what format; 3) when NOT to push for booking; 4) the exact playbook lines to add -- tone and closing behavior only, no facts, prices, rules or discounts changed.
```

## Muse's answer (verbatim)

This is a closing problem, not a warmth/accuracy problem.

Lucy ends with `any questions, just text me` because the prompt teaches her to. `ANSWER, DON'T PUNT: answer it COMPLETELY and stop` + Touch 1: `any questions about the process or your estimate` + `warm and genuinely helpful, never salesy` = she reads a booking step as salesy. You have to redefine a booking step as helpful.

### 1) What instruction makes her close without sounding salesy

Abstract rules don't work for selling. You need a **CLOSING rule** that is as explicit as rule #15:

> Answer fully first, then end with ONE next step. Answer + Close is one turn.

The owner pattern in your Bonnie transcript is the model:
Answer honestly and completely, correct the misconception flatly, hold the line, then invite forward. He doesn't use urgency, discount, or pressure. He educates.

Lucy needs that written as: **honest answer is the sell, the close just makes it easy to act.**

Without this, she will keep choosing between "be helpful" OR "book the job." She needs: helpful = answer + make booking easy.

### 2) Should you use real texts as few-shots? Yes.

Don't add 10. Add **3, trimmed, in USER / LUCY format**, all under 320 chars, all showing: complete answer + ONE booking step.

Format to add in the prompt:

```
USER: Will the gold hold up if I soak every day?
LUCY: Yes - Gold is built for daily soaking. Just no essential oils or bath bombs in any refinished tub, mine or anyone's. Want me to get you on the schedule? You can grab a time here: {{booking_link}}
```

Why 3:
1. durability / use question -> answer + booking link
2. process / what-you-do question -> answer + scheduling question
3. color / repair scope question -> answer + booking link

Do NOT use the Bonnie price-match text verbatim as a few-shot. That is owner-only power. Lucy has no discount power except veteran 10% / senior 5%. If you show her `I will honor it`, she will copy it. Show her the *shape* - direct, honest, no defensiveness - but with Lucy-legal closes.

Few-shots beat a paragraph rule because tone lives in the last sentence. She currently copies `any questions, just text me` because that's the only last-sentence she sees.

### 3) When NOT to push for booking

This is critical or she'll sound salesy. No booking push when:

1. No estimate on record + price/quote/starting question -> photo request only per rule #15. No link, no price.
2. Customer defers: `let me think / talk to spouse / get back to you` -> use defer script verbatim. No repeat of times, no added link same turn.
3. Opt-out / not_interested / wrong number -> short polite close, `escalate_oscar=true`. Never text again.
4. Hand-off jobs: owner request, property manager / multi-unit / commercial, warranty problem or peeling on PAST job, tech running late, afternoon request for non-tub service, legal/refund/safety, call request or asked for Oscar/human.
5. Timed callback request: `text me at 4 / tomorrow` -> confirm you'll TEXT then + set `followup_at`. No booking link. That's a contact request, not a booking.
6. You promised to text at this time in a PROACTIVE follow-up -> just send that text naturally. Don't stack a hard close on it.
7. Just booked / picked a slot -> thank them for their business + send booking link to lock it in. Don't add another push.

Everywhere else with an estimate on record: answer + ONE booking step.

### 4) Exact playbook lines to add - tone + closing only

Add this block, change nothing else about facts/prices/rules/discounts:

```
### closing - one clear next step (Oscar 2026-10-12)
- After you answer fully, end with ONE next step toward booking. Never end with "any questions, just text me" alone.
- ONE means one: either the booking link OR a direct scheduling question, never both stacked, never twice.
- Default language, pick one:
  "Want me to get you on the schedule?"
  "Want to grab a time here: {{booking_link}}"
  "If you want to move forward, you can grab a time here: {{booking_link}}"
- It must sound optional: "when you're ready," "if you want to move forward." No urgency, no discount mention, no pressure, no mention of viewed/opened estimate.
- If availability is given, offer only those labels exactly, then the link. If no availability, just the link.
- If they defer, do NOT close for booking that turn. Use the defer script as-is.
- If no estimate on record, the photo request IS the close. No booking link.
```

And change this one line in ANSWER, DON'T PUNT:

From: `ANSWER it fully and stop.`
To: `ANSWER it fully, then add ONE booking step from Closing above and stop.`

That keeps her warm/human/accurate, but makes `no close` feel like an incomplete answer.
