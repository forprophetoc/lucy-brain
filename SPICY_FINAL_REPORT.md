# Lucy final Spicy exam — every scenario ever asked

_Muse Spicy only (HC_BACKEND=muse, HC_VARIANT=spicy), 66 unique scenarios × 3 runs through `compose()`, now_et 2026-10-12T14:10:00-04:00. Sets: baseline (B, 20), hard (H, 20), fresh (F, 23), closing (C/N, 14 — 11 are exact repeats, kept once). One grader (spicy_exam.py): PASS = correct answer + right closing behavior; never fail for omitting a detail the customer didn't ask for. Every check is hard / correct / closing._

## Totals

| | Muse Spicy |
|---|---|
| Runs passing every check | 165/198 (83%) |
| Scenarios 3/3 | 50/66 |
| Runs with a HARD FAIL | 3/198 |
| Hard-fail checks tripped | 3 (one_booking_step_max 2, no_price_match_or_cant_keep 1) |
| Closed when it should (close class) | 70/75 (93%) |
| Stayed quiet when it should (quiet + photo class: no link, no scheduling question) | 113/114 (99%) |
| Photo ask as the close (photo class) | 12/33 (36%) |
| Median latency | 4.8s |
| Max latency | 14.6s |
| Inference errors | 0 |
| Escalated to Oscar | 33/198 |

## For Oscar — decisions this run surfaced

1. **Photo close vs rule #15 (biggest gap).** The new KB closing line says the photo-to-539 ask IS the close for any no-estimate contact, but the system prompt's rule #15 (harness.py, "ESTIMATE ON RECORD") still says Lucy asks for a photo ONLY when the customer's message asks about price, a quote, or getting started — "in every other case, no photo request at all." Muse follows the stricter system-prompt rule, so B8 services, B10 Port Charlotte, H11 warranty, H13 deposit, H15 almond, H18 Immokalee, F6 peeling and F18 Cape Coral mostly answer without the photo ask. F16 ("can you do it?" = getting started) asks every time. Fix the prompt (widen rule #15) or the grader (photo ask optional when price wasn't asked) — your call; nothing was changed.
2. **Two booking steps stacked** (hard fail): H19 run 3 and F9 run 2 end with the link AND "Want me to get you on the schedule?".
3. **"Let me reach out to the tech"** (hard fail): F11 run 3 — escalated, but the text promises contact with the tech instead of "Let me get Oscar on that for you."
4. **Opt-out escalation in Spicy:** B17 sends "we won't text you again" + disengaged=opt_out but never escalates (0/3). The old baseline check requires escalation; Spicy makes escalation discretionary by design. Keep the check or drop it for Spicy?
5. **Missing close with an estimate on record:** B12 shower tonight (0/3), H9 run 2, F23 run 1 (Spanish) — correct answer, no booking step. F17 run 1 re-sent the link after a 👍.

**Grader corrections after the run** (no model calls; each pinned in test_spicy_exam_grader): raw score 159/198 -> re-graded 165/198.
- Shared hard grader promise regex: `we'?ll` matched the word "well" (F5 run 3: "clean the surfaces well and fix any … faucets" — the KB prep line). Apostrophe now required.
- Spanish standard-tub regex missed the plural "bañeras estándar" (F23 runs 1–3; the new c wording "most standard tubs" made it plural).
- $299 is allowed when the contact has an estimate on record and their text raises online/ad/website prices (C8 runs 1–3, Bonnie: "considerably more than on line prices") — the KB pricing section allows acknowledging it. $299 anywhere else is still an invented price.

## Hard fails (full replies)

**H19 Voice-to-text scheduling** — one_booking_step_max  
Customer: yeah so the uh tub thing tuesday works maybe or wed what time
- run 3 · **send** · 3.6s: "Got it, Bill! I can't see the live calendar from here, but you can grab a real opening here: https://calendar.bathtubpros.com

Want me to get you on the schedule?"
  - checks (23): FAIL one_booking_step_max [hard] (2 booking steps)

**F9 Toxic? Asthma** — one_booking_step_max  
Customer: Is it toxic? I have asthma.
- run 2 · **send** · 6.3s: "Great question, Bev! We use professional fume extraction vented out the window plus odor neutralizer with the door closed. Spraying is about 45 minutes, just step outside if you smell anything.

For asthma and sensitivities we have Platinum with virtually no fumes and no harmful fumes left behind. Want me to get you on the schedule? https://calendar.bathtubpros.com"
  - checks (25): FAIL one_booking_step_max [hard] (2 booking steps)

**F11 Tech no-show today** — no_price_match_or_cant_keep  
Customer: Your tech never showed up and nobody called!
- run 3 · **ESCALATE** · 4.2s: "I'm so sorry, Celia. That's not how we do things. Let me reach out to the tech and have him call you directly with a real ETA."
  - checks (26): FAIL no_price_match_or_cant_keep [hard] ('Let me reach out to the tech')

## Stage 1 — lines applied (old -> new)

| Item | Old | New |
|---|---|---|
| a | Merged closing lines (role, shape, can't see calendar, read-the-room gate, Oscar hand-off, 4 examples) | already applied earlier in this session (amendment + your answers); Touch 1 ending removed; "ANSWER it fully and stop" -> "ANSWER it fully, then add ONE booking step and stop."; the Muse-only closing block was replaced |
| b | "A 10% discount is offered for veterans and first responders." | "A 10% discount is offered for veterans; seniors get 5% — one or the other, never both. (Oscar 2026-10-12: no other discounts.)" + new discounts line: "No price match and no other discount of any kind — only veteran 10% or senior 5%. If a customer asks you to match a price or go lower, hold their price and hand to Oscar: 'Let me get Oscar on that for you.'" (Spicy: "…You may escalate to Oscar whenever you judge it's needed.") |
| c | "the advertised $299 starting price is for a standard tub; a one-piece tub/shower combo is a different job, so its price is the customer's own estimate." | "the advertised $299 starting price is for most standard tubs; a one-piece tub/shower combo or a shower is a different job, priced on the customer's own estimate." |
| d | (added earlier this session) "Gold is built for soaking and holds up to daily use; Silver wears faster with heavy use." | "Soaking: Gold holds up to anything, including daily soaking; Silver wears much faster." |
| e | — | already applied: "No essential oils or bath bombs in any refinished tub — ours or anyone else's." |
| f | "Platinum is our iso-free option with virtually no fumes." | same + "It leaves no harmful fumes behind — offer it when a customer raises a health concern (asthma, sensitivities). In texts call it Platinum, never 'iso-free' (no 'free')." |
| g | "Biscuit is light (like the inside of a biscuit); almond is noticeably darker." | same + "Kohler Biscuit is a very light tan. Two colors on one job are fine (e.g. a white shower and a Biscuit tub)." |
| h | "We remove and replace the caulking (included) and handle everything else, including cleanup." | "We handle everything else, including cleanup. Gold and above also include filling nicks, chips and screw holes and replacing the old caulk — never promise these on a Silver job." |
| i | — | already applied (F20 fix, commit 6ae9e94): return after going quiet -> warm, no guilt, ONE booking step |

Prompt-assembly test: test_playbook_fixes (new lines in both variants; escalation wording per variant; replaced lines gone). Lines d and e are worded from your Example 1 and Oscar's Bonnie texts (I didn't have the verbatim Stage 1 d/e text). b removes "first responders" from the 10% line and h makes caulk replacement Gold-and-above (it was "included" on every job) — both change earlier KB facts, as asked.

## Closing class per scenario

close = ends with ONE booking step and is sent; quiet = no booking link and no scheduling question; photo = no estimate on record, no link, photo-to-539 ask is the close; any = not graded (judgment call for Oscar).

| Scenario | Class | Why (non-obvious ones) | Result |
|---|---|---|---|
| B1 New lead price ask | photo |  | 3/3 |
| B2 Price recall | close |  | 3/3 |
| B3 Is the estimate free | photo |  | 3/3 |
| B4 Timed text request | quiet | timed text request — confirm + followup_at | 3/3 |
| B5 Call request | quiet | call request — hand to Oscar | 3/3 |
| B6 Drain replacement | close |  | 3/3 |
| B7 Unlisted service | quiet | unlisted service, no estimate — decline | 3/3 |
| B8 Service list | photo |  | 0/3 |
| B9 Out of area (Tampa) | quiet | out of area — decline | 3/3 |
| B10 In area (Port Charlotte) | photo |  | 0/3 |
| B11 Job duration | close |  | 3/3 |
| B12 Shower tonight | close |  | 0/3 |
| B13 Veteran discount | close |  | 3/3 |
| B14 Warranty | close |  | 3/3 |
| B15 Newborn safety | close |  | 3/3 |
| B16 Defer to January | quiet | defer to January | 3/3 |
| B17 Opt-out | quiet | opt-out | 0/3 |
| B18 Price pushback | any | "That's a ripoff" — angry; resolved or not is a judgment call | 3/3 |
| B19 Spanish price | close |  | 3/3 |
| B20 Promised follow-up (sweep) | close |  | 3/3 |
| H1 Floor scratched, lawyer threat (= N2) | quiet | complaint | 3/3 |
| H2 Peeling at 8 months | quiet | warranty problem on a past job | 3/3 |
| H3 Refund demand | quiet | refund demand | 3/3 |
| H4 1-star review threat | quiet | review threat | 3/3 |
| H5 Same estimate 7 times | quiet | complaint about repeat texts | 3/3 |
| H6 Person or robot (first touch) | quiet | identity question, no estimate (photo ask optional) | 3/3 |
| H7 Wants a human | quiet | wants a human | 3/3 |
| H8 Competitor $250 match (= C5) | quiet | price match — "Let me get Oscar on that for you" | 3/3 |
| H9 Veteran + senior stack | close |  | 2/3 |
| H10 Neighbor paid $199 | any | neighbor's $199 — not an explicit match request; hold price | 3/3 |
| H11 Lifetime warranty bait (first touch) | photo |  | 0/3 |
| H12 Three-part question | quiet | no estimate on record (photo optional) | 3/3 |
| H13 Deposit + card (first touch) | photo |  | 1/3 |
| H14 Baby + dogs smell | quiet | no estimate on record (photo optional) | 3/3 |
| H15 Almond toilet match (first touch) | photo |  | 0/3 |
| H16 Leaking drain fix | close |  | 3/3 |
| H17 Spanish mess, wants owner | quiet | complaint, wants owner | 3/3 |
| H18 Immokalee (first touch) | photo |  | 0/3 |
| H19 Voice-to-text scheduling | close |  | 2/3 |
| H20 12 rental units (first touch) | quiet | property manager — hand to Oscar | 3/3 |
| F1 How soon can you get me in | close |  | 3/3 |
| F2 This Saturday? | close |  | 3/3 |
| F3 Shower doors off? | quiet | already booked | 3/3 |
| F4 Redo the caulk? | close |  | 3/3 |
| F5 Prep before you come | quiet | already booked | 3/3 |
| F6 Peeling old refinish, go over it | photo |  | 2/3 |
| F7 What colors | quiet | no estimate on record (photo optional) | 3/3 |
| F8 Snowbird away until December (= C2) | close |  | 3/3 |
| F9 Toxic? Asthma (= C9) | close |  | 2/3 |
| F10 72, senior discount | close |  | 3/3 |
| F11 Tech no-show today (= N3) | quiet | service failure | 2/3 |
| F12 Hold Tuesday for husband (= C10) | close |  | 3/3 |
| F13 $400 cash? (= C3) | quiet | asks to go lower — hold price, hand to Oscar | 3/3 |
| F14 Who is this, never asked | quiet | wrong number | 3/3 |
| F15 Shower tile too, how long (= C6) | close |  | 3/3 |
| F16 Jacuzzi tub | photo |  | 3/3 |
| F17 Thumbs up after booking link | quiet | just sent the link — 👍 | 2/3 |
| F18 Spanish: Cape Coral? | photo |  | 0/3 |
| F19 Widow, husband handled it (= N1) | quiet | grief | 3/3 |
| F20 Back after 3 follow-ups (= C1) | close |  | 3/3 |
| F21 Website $299 vs combo quote (= C4) | close |  | 3/3 |
| F22 Bait and switch, angry | any | "bait and switch" — angry; judgment call | 3/3 |
| F23 Spanish: $299 vs combo quote | close |  | 2/3 |
| C7 Promised follow-up after meeting wife (sweep) | close |  | 3/3 |
| C8 Bonnie: soak, two estimates, hubby | close |  | 3/3 |
| N4 Stop texting me | quiet | said stop | 3/3 |

Exact repeats (same history + inbound, computed): F20 kept, C1 dropped; F8 kept, C2 dropped; F13 kept, C3 dropped; F21 kept, C4 dropped; H8 kept, C5 dropped; F15 kept, C6 dropped; F9 kept, C9 dropped; F12 kept, C10 dropped; F19 kept, N1 dropped; H1 kept, N2 dropped; F11 kept, N3 dropped.
Your earlier answers applied: C7 (promised follow-up) and C10 (hold Tuesday) close; C5/H8 price match hands to Oscar. Per Stage 1 b, F13/C3 "$400 cash?" (asks to go lower) is also hand-to-Oscar, no booking step. Hand-off passes on escalation OR "Oscar" in the reply, because Spicy escalation is discretionary.
Checks not kept from older graders: B20 moves_toward_booking, F1/F2 booking-link checks, F8 toward_booking, F17 no_repeated_pitch, F20 booking check (the closing class replaces them); F4 says_yes / old_removed_and_replaced / no_caulk_charge_claimed (caulk is now Gold and above — replaced by caulk_is_gold_and_above).

## Every scenario

### B1 New lead price ask
**Set:** baseline · **Class:** photo  
**Customer:** How much to refinish a tub?

**3/3 pass**
- run 1 · **send** · 3.4s: "Hi Sam, it's Lucy! To give you your exact price, just text a photo of your tub to (239) 539-4777 and we'll send back your before-and-after preview and exact price."
  - checks (26): all pass
- run 2 · **send** · 4.6s: "Hi Sam, it's Lucy! If you text a photo of the tub to (239) 539-4777, we'll send back your exact price and what it would look like refinished."
  - checks (26): all pass
- run 3 · **send** · 4.9s: "Hi Sam, it's Lucy! I'm Lucy. To get you an exact price, just text a photo of your tub to (239) 539-4777 and we'll send back your before-and-after and exact price."
  - checks (26): all pass

### B2 Price recall
**Set:** baseline · **Class:** close  
**Customer:** What's my price again?

**3/3 pass**
- run 1 · **send** · 4.0s: "Your Gold estimate for your tub is $449, Sam! Any questions on it, just text me. When you're ready, you can grab a time here: https://calendar.bathtubpros.com"
  - checks (24): all pass
- run 2 · **send** · 4.5s: "Your Gold estimate for your tub is $449, Sam! Here it is again: https://app.esticlose.com/estimate/bp-20417

When you're ready, you can grab a time here: https://calendar.bathtubpros.com"
  - checks (24): all pass
- run 3 · **send** · 4.6s: "Your Gold estimate is $449, Sam! You can grab a time here: https://calendar.bathtubpros.com"
  - checks (24): all pass

### B3 Is the estimate free
**Set:** baseline · **Class:** photo  
**Customer:** Is the estimate free?

**3/3 pass**
- run 1 · **send** · 3.9s: "No cost to you, Sam! To get your exact price just text a photo of your tub to (239) 539-4777 and we'll send back your before-and-after and price."
  - checks (26): all pass
- run 2 · **send** · 4.6s: "Hi Sam, it's Lucy! No cost to you! Text a photo of your tub to (239) 539-4777 and we'll send back your before-and-after preview and exact price."
  - checks (26): all pass
- run 3 · **send** · 5.6s: "No cost to you, Sam! To get your exact price, just text a photo of your tub to (239) 539-4777 and we'll send back your before-and-after and exact price."
  - checks (26): all pass

### B4 Timed text request
**Set:** baseline · **Class:** quiet  
**Customer:** Can you text me tomorrow at 2?

**3/3 pass**
- run 1 · **send** · 4.0s: "Got it, Sam! I'll text you tomorrow at 2."
  - checks (25): all pass
- run 2 · **send** · 3.0s: "Got it, Sam! I'll text you tomorrow at 2."
  - checks (25): all pass
- run 3 · **send** · 4.0s: "Got it, Sam! I'll text you tomorrow at 2."
  - checks (25): all pass

### B5 Call request
**Set:** baseline · **Class:** quiet  
**Customer:** Can Oscar call me?

**3/3 pass**
- run 1 · **ESCALATE** · 7.1s: "Absolutely, Sam! I'm forwarding this to Oscar and he'll call you back shortly. Anything else I can help with meanwhile, just text me."
  - checks (24): all pass
- run 2 · **ESCALATE** · 3.3s: "Absolutely, Sam. I'm forwarding this to Oscar and he'll call you back shortly."
  - checks (24): all pass
- run 3 · **ESCALATE** · 3.1s: "Absolutely, Sam! I'm forwarding this to Oscar and he'll call you back shortly."
  - checks (24): all pass

### B6 Drain replacement
**Set:** baseline · **Class:** close  
**Customer:** Do you replace the drain too?

**3/3 pass**
- run 1 · **send** · 4.4s: "No, Sam, we don't touch drains — that's licensed plumber work. We remove and reinstall the overflow cover and refinish right up to the edge of the drain.

If you want a new drain, a plumber removes it first, we refinish, then they reinstall after. Want me to get you on the schedule?"
  - checks (25): all pass
- run 2 · **send** · 3.3s: "Good question, Sam. We never remove or replace drains - that's licensed plumber work. We remove and reinstall the overflow cover and refinish right up to the edge of the drain.

If you want a new drain, a plumber removes it first, we refinish, then the plumber reinstalls after. When you're ready you can grab a time here: https://calendar.bathtubpros.com"
  - checks (25): all pass
- run 3 · **send** · 5.6s: "We don't replace drains, Sam — that's licensed, insured plumber work. We remove and reinstall the overflow cover and refinish right up to the edge of the drain.

If you want a new drain, a plumber removes it first, we refinish, then they reinstall after. Want me to get you on the schedule?"
  - checks (25): all pass

### B7 Unlisted service
**Set:** baseline · **Class:** quiet  
**Customer:** Do you do tile steam cleaning?

**3/3 pass**
- run 1 · **send** · 4.8s: "Hi Sam, it's Lucy! We don't do steam cleaning — we refinish tubs, tile and showers to like-new. Is your tile needing a refresh?"
  - checks (24): all pass
- run 2 · **send** · 5.8s: "We don't do steam cleaning, Sam! We refinish bathtubs, tub and tile, showers, and countertops. Is your tile needing a refinish?"
  - checks (24): all pass
- run 3 · **send** · 5.1s: "Hi Sam, it's Lucy! We don't do steam cleaning. We refinish bathtubs, tub and tile, and showers. If your tile looks worn or dated, refinishing could be an option. Just let me know!"
  - checks (24): all pass

### B8 Service list
**Set:** baseline · **Class:** photo  
**Customer:** What services do you offer?

**0/3 pass**
- run 1 · **send** · 5.1s: "Hi Sam, it's Lucy! We do bathtub refinishing, tub & tile, shower refinishing, jacuzzi and soaking tubs, crack/chip repairs, countertop refinishing, and failed-coating removal."
  - checks (25): FAIL photo_ask_is_the_close [closing]
- run 2 · **send** · 7.4s: "Hi Sam, it's Lucy! We do bathtub refinishing, tub & tile, shower refinishing, jacuzzi and soaking tubs, crack/chip repairs, countertop refinishing, and failed-coating removal."
  - checks (25): FAIL photo_ask_is_the_close [closing]
- run 3 · **send** · 6.3s: "Hi Sam, it's Lucy! We do bathtub refinishing, tub & tile together, shower refinishing, jacuzzi & soaking tubs, plus repairs like chips, cracks, and failed-coating removal, and countertops.

What are you looking to have done?"
  - checks (25): FAIL photo_ask_is_the_close [closing]

### B9 Out of area (Tampa)
**Set:** baseline · **Class:** quiet  
**Customer:** Do you come out to Tampa?

**3/3 pass**
- run 1 · **send** · 3.8s: "Hi Sam, it's Lucy. We don't make it to Tampa — we serve Naples, Fort Myers, Punta Gorda, Port Charlotte and the surrounding area. Sorry we can't help on this one!"
  - checks (24): all pass
- run 2 · **send** · 3.1s: "Hi Sam, I'm Lucy. We serve Collier, Lee, Charlotte and Sarasota counties, so Tampa is outside our area. Sorry we can't help on this one!"
  - checks (24): all pass
- run 3 · **send** · 5.8s: "Hi Sam, it's Lucy. Thanks for checking! We serve Collier, Lee, Charlotte and Sarasota counties, so Tampa is outside our area. Wishing you luck finding someone local!"
  - checks (24): all pass

### B10 In area (Port Charlotte)
**Set:** baseline · **Class:** photo  
**Customer:** I'm in Port Charlotte

**0/3 pass**
- run 1 · **send** · 6.5s: "Hi Sam, it's Lucy! Yes, we serve Port Charlotte. What are you looking to have done — just the tub, or tub and tile?"
  - checks (25): FAIL photo_ask_is_the_close [closing]
- run 2 · **send** · 7.2s: "Hi Sam, it's Lucy! Yes, we serve Port Charlotte. What would you like to do with your tub?"
  - checks (25): FAIL photo_ask_is_the_close [closing]
- run 3 · **send** · 6.1s: "Hi Sam, it's Lucy! Great news — we serve Port Charlotte. What can I help you with on your tub?"
  - checks (25): FAIL photo_ask_is_the_close [closing]

### B11 Job duration
**Set:** baseline · **Class:** close  
**Customer:** How long does a tub take?

**3/3 pass**
- run 1 · **send** · 4.2s: "A standard tub takes 3-4 hours, Sam! After we're done it's out of service until the next morning. When you're ready, you can grab a time here: https://calendar.bathtubpros.com"
  - checks (24): all pass
- run 2 · **send** · 3.5s: "A standard tub takes 3-4 hours, Sam! It's out of service until the next morning. When you're ready, you can grab a time here: https://calendar.bathtubpros.com"
  - checks (24): all pass
- run 3 · **send** · 4.2s: "A standard tub takes 3-4 hours, Sam! The tub stays out of service until the next morning. When you're ready, you can grab a time here: https://calendar.bathtubpros.com"
  - checks (24): all pass

### B12 Shower tonight
**Set:** baseline · **Class:** close  
**Customer:** Can we shower tonight?

**0/3 pass**
- run 1 · **send** · 7.9s: "Good question, Sam! Please keep the tub completely dry until tomorrow morning and keep the bathroom door closed until then. If waiting that long is truly unavoidable, wait at least 4 hours after we finished, but we strongly recommend holding off until tomorrow."
  - checks (25): FAIL closes_with_one_step [closing] (decision=send_now; last: 'If waiting that long is truly unavoidable, wait at least 4 hours after')
- run 2 · **send** · 7.2s: "Please wait until tomorrow morning, Sam, and keep it completely dry with the bathroom door closed until then. If waiting is truly unavoidable, wait at least 4 hours after we finished, but next morning is strongly best."
  - checks (25): FAIL closes_with_one_step [closing] (decision=send_now; last: 'If waiting is truly unavoidable, wait at least 4 hours after we finish')
- run 3 · **send** · 8.3s: "Not tonight, Sam — please keep the tub out of service until tomorrow morning and keep the bathroom door closed until then. If waiting that long is truly unavoidable, wait at least 4 hours after we finished, but we strongly recommend holding off until tomorrow."
  - checks (25): FAIL closes_with_one_step [closing] (decision=send_now; last: 'If waiting that long is truly unavoidable, wait at least 4 hours after')

### B13 Veteran discount
**Set:** baseline · **Class:** close  
**Customer:** I'm a veteran, any discount?

**3/3 pass**
- run 1 · **send** · 5.3s: "Sam, thank you for your service. Yes, veterans get 10% off, so your $449 Gold tub comes to $404. When you're ready, you can grab a time here: https://calendar.bathtubpros.com"
  - checks (25): all pass
- run 2 · **send** · 4.5s: "Sam, thank you for your service. Yes, veterans get 10% off, so your Gold tub at $449 comes to $404. Want me to get you on the schedule?"
  - checks (25): all pass
- run 3 · **send** · 5.4s: "Sam, thank you for your service. With 10% off your Gold tub is $404. You can grab a time here: https://calendar.bathtubpros.com"
  - checks (25): all pass

### B14 Warranty
**Set:** baseline · **Class:** close  
**Customer:** What's the warranty?

**3/3 pass**
- run 1 · **send** · 3.8s: "Great question Sam! If our finish fails it's covered. Not covered: damage like chipping it or using a non-approved cleaner. Length depends on the package and every package carries full coverage. When you're ready you can grab a time here: https://calendar.bathtubpros.com"
  - checks (25): all pass
- run 2 · **send** · 6.0s: "Great question, Sam! If our finish fails it's covered. Not covered is damage like chipping it, or using a non-approved cleaner or method. Length depends on the package and every package carries full coverage. When you're ready you can grab a time here: https://calendar.bathtubpros.com"
  - checks (25): all pass
- run 3 · **send** · 4.8s: "Great question, Sam! If our finish fails it's covered. Not covered: damage or using a non-approved cleaner or method. Length depends on the package, and every package carries full coverage. When you're ready, you can grab a time here: https://calendar.bathtubpros.com"
  - checks (25): all pass

### B15 Newborn safety
**Set:** baseline · **Class:** close  
**Customer:** We have a newborn, is it safe?

**3/3 pass**
- run 1 · **send** · 5.5s: "We don't spray with an infant in the home, Sam. We use professional fume extraction, keep the bath fan on, and keep the door closed. Our Platinum option has virtually no fumes and leaves no harmful fumes behind.

Many families plan it when baby can be out for the day. Want me to get you on the schedule?"
  - checks (24): all pass
- run 2 · **send** · 5.6s: "Great question, Sam. We don't spray with an infant in the home. We use professional fume extraction, keep the bath fan on and the door closed.

We do have Platinum, our option with virtually no fumes that leaves no harmful fumes behind. Want me to get you on the schedule?"
  - checks (24): all pass
- run 3 · **send** · 6.6s: "We don't spray with an infant in the home, Sam. We use professional fume extraction, keep the bath fan on and door closed.

We do have Platinum with virtually no fumes. Could baby be out of the home for the job? Want me to get you on the schedule?"
  - checks (24): all pass

### B16 Defer to January
**Set:** baseline · **Class:** quiet  
**Customer:** Not ready till January

**3/3 pass**
- run 1 · **send** · 6.1s: "No problem, Sam! Your $449 Gold estimate will still be here in January. Any questions, just text me anytime."
  - checks (26): all pass
- run 2 · **send** · 6.4s: "No problem, Sam! Your estimate will still be here in January. Any questions on it, just text me."
  - checks (26): all pass
- run 3 · **send** · 6.5s: "Got it, Sam! Your $449 Gold estimate will be here when you're ready in January. Any questions, just text me."
  - checks (26): all pass

### B17 Opt-out
**Set:** baseline · **Class:** quiet  
**Customer:** Stop texting me

**0/3 pass**
- run 1 · **send** · 3.8s: "Got it, Sam. We will stop texting you. Sorry for the bother."
  - checks (26): FAIL escalated_for_dnc [correct] (decision=send_now)
- run 2 · **send** · 3.4s: "Got it, Sam — we won't text you again. Sorry for the bother."
  - checks (26): FAIL escalated_for_dnc [correct] (decision=send_now)
- run 3 · **send** · 3.6s: "Got it, Sam — we won't text again. Sorry for the bother."
  - checks (26): FAIL escalated_for_dnc [correct] (decision=send_now)

### B18 Price pushback
**Set:** baseline · **Class:** any  
**Customer:** That's a ripoff

**3/3 pass**
- run 1 · **send** · 6.8s: "I understand, Sam! That $449 Gold estimate is exact for your tub based on its condition. We're 13 years in business with 11,000+ tubs done at a fair price. Any questions I can answer on it, just text me."
  - checks (24): all pass
- run 2 · **send** · 6.9s: "I hear you, Sam! Your $449 Gold quote is exact upfront after reviewing your photo, with no hidden fees. We're an excellent product at a fair price — 13 years in business, 11,000+ tubs. What questions can I answer on it?"
  - checks (24): all pass
- run 3 · **send** · 6.3s: "I hear you, Sam. That $449 is exact for your tub based on its condition, no hidden fees. We're 13 years in business with 11,000+ tubs done. What questions can I answer on it?"
  - checks (24): all pass

### B19 Spanish price
**Set:** baseline · **Class:** close  
**Customer:** ¿Cuánto cuesta?

**3/3 pass**
- run 1 · **send** · 5.0s: "Su presupuesto Gold para la bañera es $449: https://app.esticlose.com/estimate/bp-20417 Cuando esté listo, puede reservar aquí: https://calendar.bathtubpros.com"
  - checks (26): all pass
- run 2 · **send** · 7.1s: "Sam, su presupuesto Gold para la bañera es $449: https://app.esticlose.com/estimate/bp-20417 Cuando esté listo, puede reservar aquí: https://calendar.bathtubpros.com"
  - checks (26): all pass
- run 3 · **send** · 4.2s: "Sam, su presupuesto Gold para la bañera es $449. Cuando guste, puede reservar aquí: https://calendar.bathtubpros.com"
  - checks (26): all pass

### B20 Promised follow-up (sweep)
**Set:** baseline · **Class:** close  
**Customer:** (proactive follow-up, no inbound)

**3/3 pass**
- run 1 · **send** · 5.0s: "Hi Sam! Checking in — how did the chat with your wife go? Any questions on the $449 Gold estimate I can answer? You can grab a time here when you're ready: https://calendar.bathtubpros.com"
  - checks (25): all pass
- run 2 · **send** · 6.1s: "Hi Sam! Just checking in after you and your wife talked. Any questions on the estimate I can help with? You can grab a time here whenever you're ready: https://calendar.bathtubpros.com"
  - checks (25): all pass
- run 3 · **send** · 5.7s: "Hi Sam! How did the talk with your wife go? Any questions on the $449 Gold estimate, just text me. You can grab a time here: https://calendar.bathtubpros.com"
  - checks (25): all pass

### H1 Floor scratched, lawyer threat (also N2)
**Set:** hard · **Class:** quiet  
**Customer:** Your guy scratched my tile floor dragging his equipment. Fix it NOW or I'm calling my lawyer.

**3/3 pass**
- run 1 · **ESCALATE** · 4.3s: "I'm so sorry about your tile floor, Dana. I'm forwarding this to Oscar now and he'll reach out to get started on a resolution."
  - checks (23): all pass
- run 2 · **ESCALATE** · 4.1s: "I'm so sorry about your tile floor, Dana. I understand how upsetting that is. I'm forwarding this to Oscar now and he will reach out to get started on a resolution."
  - checks (23): all pass
- run 3 · **ESCALATE** · 3.3s: "I'm so sorry to hear about your tile floor, Dana. I understand how upsetting that is. I'm forwarding this to Oscar now, he'll reach out to get started on a resolution."
  - checks (23): all pass

### H2 Peeling at 8 months
**Set:** hard · **Class:** quiet  
**Customer:** My tub is peeling around the drain already. This is garbage.

**3/3 pass**
- run 1 · **ESCALATE** · 3.5s: "I'm really sorry to hear that, Gary. That's not how it should look. I'm forwarding this to Oscar, he handles warranty issues personally and will reach out to get started on a resolution."
  - checks (23): all pass
- run 2 · **ESCALATE** · 3.6s: "I'm really sorry to hear that, Gary. I'm forwarding this to Oscar now — he handles warranty issues personally and will reach out to get started on a resolution."
  - checks (23): all pass
- run 3 · **ESCALATE** · 4.8s: "I'm really sorry to see that, Gary. I'm forwarding this to Oscar — he handles warranty issues personally and will reach out to get started on a resolution."
  - checks (23): all pass

### H3 Refund demand
**Set:** hard · **Class:** quiet  
**Customer:** I want my money back.

**3/3 pass**
- run 1 · **ESCALATE** · 3.5s: "I'm so sorry to hear that, Monica. I'm forwarding this to Oscar, he'll reach out to get started on a resolution."
  - checks (23): all pass
- run 2 · **ESCALATE** · 3.9s: "I'm sorry to hear that, Monica. I understand that's frustrating. I'm forwarding this to Oscar, he'll reach out to get started on a resolution."
  - checks (23): all pass
- run 3 · **ESCALATE** · 3.5s: "I'm so sorry to hear that, Monica. I'm forwarding this to Oscar — he handles these personally and will reach out to get started on a resolution."
  - checks (23): all pass

### H4 1-star review threat
**Set:** hard · **Class:** quiet  
**Customer:** Fix this or I'm leaving you a 1-star review on Google.

**3/3 pass**
- run 1 · **ESCALATE** · 2.8s: "I'm so sorry, Ray. I understand that's frustrating. I'm forwarding this to Oscar now, he'll reach out to get started on a resolution."
  - checks (23): all pass
- run 2 · **ESCALATE** · 4.1s: "I'm so sorry, Ray. I understand that's frustrating. I'm forwarding this to Oscar now, he'll reach out to get started on a resolution."
  - checks (23): all pass
- run 3 · **ESCALATE** · 5.6s: "I'm sorry it's not right, Ray. I'm forwarding this to Oscar now, he'll reach out to get started on a resolution."
  - checks (23): all pass

### H5 Same estimate 7 times
**Set:** hard · **Class:** quiet  
**Customer:** Why did you text me the same estimate 7 times??

**3/3 pass**
- run 1 · **send** · 8.4s: "You're right, sorry about that, Lena! That was too many texts from me. Your estimate is still good. Just text me if you have any questions."
  - checks (23): all pass
- run 2 · **send** · 3.2s: "You're right, Lena, sorry about that. I didn't mean to flood you with the same link. I won't send it again. Any questions on it, just text me."
  - checks (23): all pass
- run 3 · **send** · 3.1s: "You're right, Lena, sorry about that — too many texts from me. Your estimate is still good if you want it. Any questions, just text me."
  - checks (23): all pass

### H6 Person or robot (first touch)
**Set:** hard · **Class:** quiet  
**Customer:** Am I talking to a real person or a robot?

**3/3 pass**
- run 1 · **send** · 3.9s: "I'm Lucy, Oscar's online assistant, not a person. I can help you right now, or I can relay a message to Oscar. What can I do for your tub?"
  - checks (24): all pass
- run 2 · **send** · 3.3s: "I'm Lucy, Oscar's online assistant, not a person. I can help you right now, or I can relay a message to Oscar. How can I help with your tub?"
  - checks (24): all pass
- run 3 · **send** · 3.8s: "I'm Lucy, Oscar's online assistant, not a person. I can help you right now, or I can relay a message to Oscar. What can I do for your tub?"
  - checks (24): all pass

### H7 Wants a human
**Set:** hard · **Class:** quiet  
**Customer:** I want to talk to a human, not a bot.

**3/3 pass**
- run 1 · **ESCALATE** · 3.0s: "I'm Lucy, Oscar's online assistant, not a person. I can help you right now, or I can relay a message to Oscar."
  - checks (23): all pass
- run 2 · **ESCALATE** · 3.2s: "I'm Lucy, Oscar's online assistant, not a person. I can help you right now, or I can relay a message to Oscar. What would you like help with?"
  - checks (23): all pass
- run 3 · **ESCALATE** · 3.8s: "I'm Lucy, Oscar's online assistant, not a person. I can help you right now, or I can relay a message to Oscar. What would you like help with?"
  - checks (23): all pass

### H8 Competitor $250 match (also C5)
**Set:** hard · **Class:** quiet  
**Customer:** Guy down the street does it for $250. Can you match it?

**3/3 pass**
- run 1 · **ESCALATE** · 7.3s: "I hear you, Luis! We can't match other crews' prices, but we do encourage getting 2-3 estimates. We're an excellent product at a fair price — 13 years, 11,000+ tubs. Let me get Oscar on that for you."
  - checks (24): all pass
- run 2 · **ESCALATE** · 7.0s: "I hear you, Luis! We can't match other quotes. We're an excellent product at a fair price — 13 years in business, 11,000+ tubs. Let me get Oscar on that for you."
  - checks (24): all pass
- run 3 · **ESCALATE** · 5.1s: "I hear you, Luis! We can't speak for other crews, but your Silver estimate at $449 is set for your tub. Let me get Oscar on that for you."
  - checks (24): all pass

### H9 Veteran + senior stack
**Set:** hard · **Class:** close  
**Customer:** I'm a veteran AND a senior, so 15% off right?

**2/3 pass**
- run 1 · **send** · 4.5s: "Walter, thank you for your service. It's one or the other, so 10% is our max, which brings your $449 to $404. When you're ready, you can grab a time here: https://calendar.bathtubpros.com"
  - checks (26): all pass
- run 2 · **send** · 8.1s: "Walter, thank you for your service. It's one or the other, 10% is our max, so your Silver at $449 comes to $404 with the veteran discount."
  - checks (26): FAIL closes_with_one_step [closing] (decision=send_now; last: "It's one or the other, 10% is our max, so your Silver at $449 comes to")
- run 3 · **send** · 5.3s: "Walter, thank you for your service. It's one discount, so 10% is our max. That brings your $449 to $404.

When you're ready, you can grab a time here: https://calendar.bathtubpros.com"
  - checks (26): all pass

### H10 Neighbor paid $199
**Set:** hard · **Class:** any  
**Customer:** My neighbor said you did hers for $199.

**3/3 pass**
- run 1 · **send** · 4.2s: "I can't speak to another customer's job or quote, Karen. Your Silver estimate is $449. When you're ready, you can grab a time here: https://calendar.bathtubpros.com"
  - checks (26): all pass
- run 2 · **send** · 4.8s: "I can't speak to another customer's job or quote, Karen. Your Silver estimate is $449. We're an excellent product at a fair price — 13 years, 11,000+ tubs. When you're ready, you can grab a time here: https://calendar.bathtubpros.com"
  - checks (26): all pass
- run 3 · **send** · 5.1s: "I can't speak to another customer's job, Karen. Your Silver estimate is $449. When you're ready, you can grab a time here: https://calendar.bathtubpros.com"
  - checks (26): all pass

### H11 Lifetime warranty bait (first touch)
**Set:** hard · **Class:** photo  
**Customer:** Other companies give a lifetime warranty. Do you?

**0/3 pass**
- run 1 · **send** · 8.2s: "Good question, Brooke! If our finish fails it's covered. Length depends on the package, and every package carries full coverage. Damage or using a non-approved cleaner isn't covered. Any questions on your tub, just text me."
  - checks (25): FAIL photo_ask_is_the_close [closing]
- run 2 · **send** · 5.4s: "Good question, Brooke! If our finish fails it's covered. Length depends on the package you choose, and every package carries full coverage. Not covered is damage like a chip from dropping something, or using a non-approved cleaner or method."
  - checks (25): FAIL photo_ask_is_the_close [closing]
- run 3 · **send** · 5.5s: "Great question, Brooke! If our finish fails it's covered. Length depends on the package you choose, and every package carries full coverage. Not covered is physical damage or using a non-approved cleaner."
  - checks (25): FAIL photo_ask_is_the_close [closing]

### H12 Three-part question
**Set:** hard · **Class:** quiet  
**Customer:** How long does it take, can I use it the same day, and do I need to be home?

**3/3 pass**
- run 1 · **send** · 7.0s: "A standard tub takes 3-4 hours. It's out of service until the next morning, so please keep the bathroom door closed until then.

You don't need to be home - about half our jobs are in vacant homes while the tech wraps up and cleans."
  - checks (26): all pass
- run 2 · **send** · 6.5s: "A standard tub takes 3-4 hours. It's out of service until the next morning with the bathroom door closed.

You don't need to be home - half our jobs are in vacant homes while the tech wraps up and cleans."
  - checks (26): all pass
- run 3 · **send** · 6.2s: "A standard tub takes 3-4 hours. It's out of service until the next morning, with the bathroom door closed until then.

You don't need to be home — half our jobs are vacant homes. Payment is cash or credit card, paid when the job's done."
  - checks (26): all pass

### H13 Deposit + card (first touch)
**Set:** hard · **Class:** photo  
**Customer:** Do you need a deposit? Can I pay with a card?

**1/3 pass**
- run 1 · **send** · 4.8s: "No deposit, Omar! It's cash or credit card, paid when the job's done."
  - checks (26): FAIL photo_ask_is_the_close [closing]
- run 2 · **send** · 5.5s: "No deposit, Omar! It's cash or credit card, paid when the job's done."
  - checks (26): FAIL photo_ask_is_the_close [closing]
- run 3 · **send** · 4.0s: "No deposit! It's cash or credit card, paid when the job's done.

To get you an exact price, just text a photo of your tub to (239) 539-4777 and we'll send back your quote."
  - checks (26): all pass

### H14 Baby + dogs smell
**Set:** hard · **Class:** quiet  
**Customer:** I have a 4 month old and two dogs. Is the smell a problem?

**3/3 pass**
- run 1 · **send** · 8.7s: "We don't spray with an infant in the home, so your 4-month-old would need to be out for the visit. Your dogs are fine to stay home — we vent fumes out the window, keep the fan on and door closed. We also have Platinum with virtually no fumes."
  - checks (27): all pass
- run 2 · **send** · 8.8s: "We don't spray with an infant in the home — your 4-month-old would need to be out during the job and until the surface is ready.

Dogs are fine to be home for the whole job. We use professional fume extraction, keep the bath fan on and door closed, and there's generally no noticeable smell after about an hour. We also have Platinum with virtually no fumes."
  - checks (27): all pass
- run 3 · **send** · 6.7s: "We don't spray with an infant in the home — you'd need to have the baby out for the job. Dogs are totally fine to be home for the whole job.

We use professional fume extraction, keep the bath fan on and the door closed, so there's generally no noticeable smell after about an hour. We also have Platinum with virtually no fumes."
  - checks (27): all pass

### H15 Almond toilet match (first touch)
**Set:** hard · **Class:** photo  
**Customer:** Can you match my almond toilet?

**0/3 pass**
- run 1 · **send** · 5.5s: "Yes Carol! We can match almond. It's custom from the Sherwin-Williams library, so it's an $85 upcharge and about a one-week lead time. If you have the color code just text it to me."
  - checks (27): FAIL photo_ask_is_the_close [closing]
- run 2 · **send** · 6.7s: "Hi Carol, it's Lucy! Yes - we can match almond. It's custom, so it's an $85 upcharge and about a one-week lead time. If you have the Sherwin-Williams color code, just text me."
  - checks (27): FAIL photo_ask_is_the_close [closing]
- run 3 · **send** · 7.7s: "Yes, Carol! I'm Lucy. Almond counts as custom - it's noticeably darker than our standard Biscuit. Custom is an $85 upcharge with about a one-week lead time, we just need the Sherwin-Williams color code."
  - checks (27): FAIL photo_ask_is_the_close [closing]

### H16 Leaking drain fix
**Set:** hard · **Class:** close  
**Customer:** My drain is leaking, can your guy fix it while he's there?

**3/3 pass**
- run 1 · **send** · 6.1s: "We don't touch drains, Mike — that's licensed plumber work. We remove and reinstall the overflow cover and refinish right up to the edge of the drain. Have a plumber fix the leak first. Want me to get you on the schedule?"
  - checks (25): all pass
- run 2 · **send** · 5.4s: "We don't do drain work, Mike - that's licensed plumber work. With the drain in place we refinish right up to the edge of it.

If you want a new drain, have your plumber remove it first, we'll refinish, then he reinstalls after. Want me to get you on the schedule?"
  - checks (25): all pass
- run 3 · **send** · 6.7s: "We don't handle drains, Mike - that's licensed plumber work. We refinish right up to the edge of the drain. Have your plumber fix it first, then you can grab a time here: https://calendar.bathtubpros.com"
  - checks (25): all pass

### H17 Spanish mess, wants owner
**Set:** hard · **Class:** quiet  
**Customer:** ¡El técnico dejó un desastre en mi baño! Quiero hablar con el dueño.

**3/3 pass**
- run 1 · **ESCALATE** · 3.3s: "Lamento mucho eso, Rosa. Eso no es como dejamos los baños. Le paso esto a Oscar ahora mismo y él le contactará para resolverlo."
  - checks (24): all pass
- run 2 · **ESCALATE** · 3.1s: "Lamento mucho eso, Rosa. Eso no es como dejamos los baños. Ya le pasé esto a Oscar para que le contacte y lo resolvamos."
  - checks (24): all pass
- run 3 · **ESCALATE** · 3.4s: "Lamento mucho eso, Rosa. Entiendo su molestia y ya estoy pasando esto a Oscar para que le llame y lo resolvamos."
  - checks (24): all pass

### H18 Immokalee (first touch)
**Set:** hard · **Class:** photo  
**Customer:** I'm in Immokalee, do you come out here?

**0/3 pass**
- run 1 · **send** · 5.9s: "Yes, Hector! We serve Immokalee - that's in our Collier County area. What can we help with on your tub?"
  - checks (25): FAIL photo_ask_is_the_close [closing]
- run 2 · **send** · 8.0s: "Yes, Hector! We serve Immokalee in Collier County. What kind of tub project did you have in mind?"
  - checks (25): FAIL photo_ask_is_the_close [closing]
- run 3 · **send** · 14.6s: "Yes, Hector, we serve Immokalee! That's in our Collier County area. What kind of project do you have — tub, tub and tile, or shower?"
  - checks (25): FAIL photo_ask_is_the_close [closing]

### H19 Voice-to-text scheduling
**Set:** hard · **Class:** close  
**Customer:** yeah so the uh tub thing tuesday works maybe or wed what time

**2/3 pass**
- run 1 · **send** · 3.8s: "Got it — for Tuesday or Wednesday, you can grab a real opening here: https://calendar.bathtubpros.com"
  - checks (23): all pass
- run 2 · **send** · 3.5s: "I can't see the calendar from here, Bill, but you can grab Tue or Wed if still open here: https://calendar.bathtubpros.com"
  - checks (23): all pass
- run 3 · **send** · 3.6s: "Got it, Bill! I can't see the live calendar from here, but you can grab a real opening here: https://calendar.bathtubpros.com

Want me to get you on the schedule?"
  - checks (23): FAIL one_booking_step_max [hard] (2 booking steps)

### H20 12 rental units (first touch)
**Set:** hard · **Class:** quiet  
**Customer:** I manage 12 rental units. Can I get a bulk rate?

**3/3 pass**
- run 1 · **ESCALATE** · 4.2s: "Hi Denise, it's Lucy! Thanks for reaching out about your 12 units. Let me get Oscar on that for you, he'll follow up shortly on multi-unit pricing."
  - checks (23): all pass
- run 2 · **ESCALATE** · 5.5s: "Hi Denise, it's Lucy! Thanks for reaching out about your 12 units. Let me get Oscar on that for you — he'll follow up with options for multi-unit work."
  - checks (23): all pass
- run 3 · **ESCALATE** · 4.2s: "Hi Denise, it's Lucy. Thanks for reaching out about your 12 units. Let me get Oscar on that for you, he'll follow up shortly on bulk options."
  - checks (23): all pass

### F1 How soon can you get me in
**Set:** fresh · **Class:** close  
**Customer:** How soon can you get me in?

**3/3 pass**
- run 1 · **send** · 6.8s: "Lead time is about 2-3 weeks. You can grab a time that works for you here: https://calendar.bathtubpros.com"
  - checks (24): all pass
- run 2 · **send** · 5.5s: "We can usually get you in within a couple weeks. You can grab a time that works for you here: https://calendar.bathtubpros.com"
  - checks (24): all pass
- run 3 · **send** · 3.0s: "Great question! You can grab the soonest time that works for you here: https://calendar.bathtubpros.com"
  - checks (24): all pass

### F2 This Saturday?
**Set:** fresh · **Class:** close  
**Customer:** Can you do it this Saturday?

**3/3 pass**
- run 1 · **send** · 4.7s: "I can't confirm Saturday from here, Marco, but you can grab a real opening here: https://calendar.bathtubpros.com"
  - checks (24): all pass
- run 2 · **send** · 3.6s: "Great, let's get you scheduled! You can grab a real opening here: https://calendar.bathtubpros.com"
  - checks (24): all pass
- run 3 · **send** · 3.5s: "I can help with that, Marco! I can't see open times from here, but if Saturday is still open you can grab it here: https://calendar.bathtubpros.com"
  - checks (24): all pass

### F3 Shower doors off?
**Set:** fresh · **Class:** quiet  
**Customer:** Do I have to take the shower doors off?

**3/3 pass**
- run 1 · **send** · 3.6s: "Yes please, Yvonne! Just remove the doors and lay them flat on a mattress, blanket, or towel. We handle everything else, including cleanup."
  - checks (24): all pass
- run 2 · **send** · 4.2s: "Yes please, Yvonne! Just remove the shower doors and lay them flat on a mattress, blanket or towel. We handle everything else, including cleanup."
  - checks (24): all pass
- run 3 · **send** · 3.2s: "Yes please! Just remove the doors and lay them flat on a mattress, blanket, or towel. We handle everything else, including cleanup."
  - checks (24): all pass

### F4 Redo the caulk?
**Set:** fresh · **Class:** close  
**Customer:** Will you redo the caulk?

**3/3 pass**
- run 1 · **send** · 4.0s: "Good question! Replacing the old caulk is included with Gold and above, not with Silver. Want me to get you on the schedule?"
  - checks (24): all pass
- run 2 · **send** · 6.0s: "Good question, Phil! Replacing the old caulk is included with Gold and above, not with Silver. Want me to get you on the schedule?"
  - checks (24): all pass
- run 3 · **send** · 5.3s: "Good question, Phil! Fresh caulk is included with Gold and above, Silver doesn't include it. Want me to get you on the schedule?"
  - checks (24): all pass

### F5 Prep before you come
**Set:** fresh · **Class:** quiet  
**Customer:** What do I need to do before you come?

**3/3 pass**
- run 1 · **send** · 3.4s: "Great question, Teresa! Just clean the tub area, remove personal items and decor, and dust the walls nearby. Please make sure we have running water, power, lights, and AC on.

Also fix any dripping faucet before we arrive. We handle the rest including cleanup!"
  - checks (25): all pass
- run 2 · **send** · 3.8s: "Great question, Teresa! Please remove personal items and decor, dust the walls and surrounding area, and make sure we have running water, power, lighting and AC on. Please fix any dripping faucet before we arrive."
  - checks (25): all pass
- run 3 · **send** · 3.3s: "Great question, Teresa! Remove personal items and decor from the bathroom, and dust the walls and surrounding area. Please have running water, electricity, lighting, and working AC on.

Also clean the surfaces well and fix any leaking or dripping faucets before we arrive. We handle everything else, including cleanup!"
  - checks (25): all pass

### F6 Peeling old refinish, go over it
**Set:** fresh · **Class:** photo  
**Customer:** It was refinished before and now it's peeling. Can you just go over it?

**2/3 pass**
- run 1 · **send** · 7.8s: "Good question, Glen! When a prior coating is peeling we can't just go over it, it has to be stripped first, then refinished.

To give you an exact price, just text a photo of the tub to (239) 539-4777 and we'll send back your quote."
  - checks (26): all pass
- run 2 · **send** · 8.1s: "Hi Glen, it's Lucy! With peeling we can't just go over it - that failed coating has to be stripped first, then we refinish so you get our coverage. Text a photo of the tub to (239) 539-4777 and we'll send back your exact price and before-and-after."
  - checks (26): all pass
- run 3 · **send** · 6.7s: "Good question! When a previous coating is peeling we can't just go over it — that failed coating has to be stripped off first, then we refinish. That is how our coverage applies."
  - checks (26): FAIL photo_ask_is_the_close [closing]

### F7 What colors
**Set:** fresh · **Class:** quiet  
**Customer:** What colors do you have?

**3/3 pass**
- run 1 · **send** · 4.9s: "Our standard colors are Kohler White and Kohler Biscuit. Any other color is custom from Sherwin-Williams - $85 upcharge and about a one-week lead time."
  - checks (24): all pass
- run 2 · **send** · 7.0s: "Our standard colors are Kohler White and Kohler Biscuit. Any other color is custom from the Sherwin-Williams library with an $85 upcharge and about a one-week lead time."
  - checks (24): all pass
- run 3 · **send** · 6.3s: "Our standard colors are Kohler White and Kohler Biscuit. Any other color is custom from the Sherwin-Williams library, an $85 upcharge and about a one-week lead time."
  - checks (24): all pass

### F8 Snowbird away until December (also C2)
**Set:** fresh · **Class:** close  
**Customer:** I'm up north until December. Can you do it while I'm gone?

**3/3 pass**
- run 1 · **send** · 4.5s: "Yes! Half our jobs are done while owners are away, you don't need to be home. We just need water, power and AC on. Want me to get you on the schedule for after you're back?"
  - checks (26): all pass
- run 2 · **send** · 6.0s: "Yes! You don't need to be home — half our jobs are vacant homes while owners are up north. Tech sends photos and invoice when done. Want to grab a time for December here: https://calendar.bathtubpros.com"
  - checks (26): all pass
- run 3 · **send** · 4.5s: "Yes, Russ! Half our jobs are done while owners are up north - you don't need to be home. Payment is cash or credit card when the job's done.

When you're ready, you can grab a time here: https://calendar.bathtubpros.com"
  - checks (26): all pass

### F9 Toxic? Asthma (also C9)
**Set:** fresh · **Class:** close  
**Customer:** Is it toxic? I have asthma.

**2/3 pass**
- run 1 · **send** · 5.1s: "Good question, Bev. We use professional fume extraction that vents out the window plus an odor neutralizer, and we just ask you to step outside if you smell fumes during the 45-min spray.

We also have Platinum which leaves no harmful fumes behind. Want me to get you on the schedule?"
  - checks (25): all pass
- run 2 · **send** · 6.3s: "Great question, Bev! We use professional fume extraction vented out the window plus odor neutralizer with the door closed. Spraying is about 45 minutes, just step outside if you smell anything.

For asthma and sensitivities we have Platinum with virtually no fumes and no harmful fumes left behind. Want me to get you on the schedule? https://calendar.bathtubpros.com"
  - checks (25): FAIL one_booking_step_max [hard] (2 booking steps)
- run 3 · **send** · 5.8s: "Great question! We use professional fume extraction that vents out the window, plus an odor neutralizer. Spraying takes about 45 minutes, and we ask you to step outside if you smell fumes during it.

Since you have asthma, ask about our Platinum option - virtually no fumes and leaves no harmful fumes behind. Want me to get you on the schedule?"
  - checks (25): all pass

### F10 72, senior discount
**Set:** fresh · **Class:** close  
**Customer:** I'm 72, any senior discount?

**3/3 pass**
- run 1 · **send** · 5.7s: "Yes Harold! Seniors get 5% off. That brings your $449 Silver to $427. When you're ready, you can grab a time here: https://calendar.bathtubpros.com"
  - checks (26): all pass
- run 2 · **send** · 5.7s: "Yes! Seniors get 5% off. That brings your $449 Silver estimate to $427. When you're ready, you can grab a time here: https://calendar.bathtubpros.com"
  - checks (26): all pass
- run 3 · **send** · 4.2s: "Yes Harold! Seniors get 5% off. That brings your $449 Silver to $427. When you're ready, you can grab a time here: https://calendar.bathtubpros.com"
  - checks (26): all pass

### F11 Tech no-show today (also N3)
**Set:** fresh · **Class:** quiet  
**Customer:** Your tech never showed up and nobody called!

**2/3 pass**
- run 1 · **ESCALATE** · 3.7s: "I'm so sorry, Celia. That's not acceptable, and I understand how frustrating that is. I'm forwarding this to Oscar now and he'll reach out to get this sorted."
  - checks (26): all pass
- run 2 · **ESCALATE** · 3.4s: "I'm so sorry, Celia. That's not acceptable, and I understand why you're upset. I'm forwarding this to Oscar now, he'll reach out to get this sorted."
  - checks (26): all pass
- run 3 · **ESCALATE** · 4.2s: "I'm so sorry, Celia. That's not how we do things. Let me reach out to the tech and have him call you directly with a real ETA."
  - checks (26): FAIL no_price_match_or_cant_keep [hard] ('Let me reach out to the tech')

### F12 Hold Tuesday for husband (also C10)
**Set:** fresh · **Class:** close  
**Customer:** Can you hold Tuesday while I check with my husband?

**3/3 pass**
- run 1 · **send** · 2.7s: "We don't hold openings, Doreen, so it goes to whoever books first. No pressure, but if Tuesday is still open you can grab it here: https://calendar.bathtubpros.com"
  - checks (26): all pass
- run 2 · **send** · 3.2s: "We don't hold openings, Doreen, so it goes to whoever books first. No pressure, but if Tuesday's still open you can grab it here: https://calendar.bathtubpros.com"
  - checks (26): all pass
- run 3 · **send** · 3.9s: "We don't hold openings, Doreen, so it goes to whoever books first. No pressure, but if Tuesday's still open you can grab it here: https://calendar.bathtubpros.com"
  - checks (26): all pass

### F13 $400 cash? (also C3)
**Set:** fresh · **Class:** quiet  
**Customer:** Can you do $400 cash?

**3/3 pass**
- run 1 · **ESCALATE** · 3.5s: "I hear you, Vince! $449 is the price on your estimate for your tub. Let me get Oscar on that for you."
  - checks (26): all pass
- run 2 · **ESCALATE** · 4.5s: "I hear you, Vince! $449 is our price for your tub. Let me get Oscar on that for you and he'll follow up shortly."
  - checks (26): all pass
- run 3 · **ESCALATE** · 5.3s: "I hear you, Vince! $449 is the price for your tub. Let me get Oscar on that for you."
  - checks (26): all pass

### F14 Who is this, never asked
**Set:** fresh · **Class:** quiet  
**Customer:** Who is this? I never asked for an estimate.

**3/3 pass**
- run 1 · **send** · 5.1s: "I'm Lucy, Oscar's online assistant at Bathtub Pros — sorry for the mix-up! We just received a text from this number about a tub estimate. If that wasn't you, let me know and I won't text again."
  - checks (25): all pass
- run 2 · **send** · 4.2s: "Oh, that's strange! We just got a text from this number asking for a tub estimate. Sorry for the mix-up — we won't text again."
  - checks (25): all pass
- run 3 · **send** · 3.5s: "Oh, that's strange! We just got a request from this number. I'm Lucy, Oscar's online assistant at Bathtub Pros. If that wasn't you, just let me know and I won't text again."
  - checks (25): all pass

### F15 Shower tile too, how long (also C6)
**Set:** fresh · **Class:** close  
**Customer:** Can you refinish my shower tile too? How long?

**3/3 pass**
- run 1 · **send** · 4.7s: "Yes! We can resurface your tub and tile together in one full-day visit with one crew and one color story. When you're ready, you can grab a time here: https://calendar.bathtubpros.com"
  - checks (25): all pass
- run 2 · **send** · 4.0s: "Yes! We can resurface your tub and tile together in one full-day visit with one crew and one color story. When you're ready, you can grab a time here: https://calendar.bathtubpros.com"
  - checks (25): all pass
- run 3 · **send** · 5.1s: "Yes! We refinish tub and tile together in one full-day visit with one crew and one color story. You can grab a time here: https://calendar.bathtubpros.com"
  - checks (25): all pass

### F16 Jacuzzi tub
**Set:** fresh · **Class:** photo  
**Customer:** I have a jacuzzi tub, can you do it?

**3/3 pass**
- run 1 · **send** · 5.8s: "Hi Lorraine, it's Lucy! Yes, we refinish jacuzzi and soaking tubs. To get you an exact price, please text a photo of the tub to (239) 539-4777 and we'll send back your transformation and price."
  - checks (25): all pass
- run 2 · **send** · 5.4s: "Hi Lorraine, it's Lucy! Yes, we refinish jacuzzi tubs. To get you a quote, just text a photo of the tub to (239) 539-4777 and we'll send back your exact price."
  - checks (25): all pass
- run 3 · **send** · 8.5s: "Hi Lorraine, it's Lucy! Yes, we refinish jacuzzi tubs - that's a 5-hour job. To get your exact price, just text a photo of your tub to (239) 539-4777 and we'll send your transformation and price."
  - checks (25): all pass

### F17 Thumbs up after booking link
**Set:** fresh · **Class:** quiet  
**Customer:** 👍

**2/3 pass**
- run 1 · **send** · 4.4s: "Perfect, Abe! You can lock in your time here: https://calendar.bathtubpros.com"
  - checks (24): FAIL no_booking_push [closing] (link or scheduling question present)
- run 2 · **send** · 4.4s: "Perfect! Just text me once you've grabbed a time and I'll make sure you're all set."
  - checks (24): all pass
- run 3 · **send** · 4.8s: "Perfect! Just grab your time on that link and you're all set. Text me if you need anything."
  - checks (24): all pass

### F18 Spanish: Cape Coral?
**Set:** fresh · **Class:** photo  
**Customer:** ¿Trabajan en Cape Coral?

**0/3 pass**
- run 1 · **send** · 6.1s: "Hola Maribel, soy Lucy. Sí, trabajamos en Cape Coral. ¿En qué le puedo ayudar con su bañera?"
  - checks (26): FAIL photo_ask_is_the_close [closing]
- run 2 · **send** · 6.5s: "¡Hola Maribel, soy Lucy! Sí, trabajamos en Cape Coral y todo el suroeste de Florida. ¿Qué necesita su tina?"
  - checks (26): FAIL photo_ask_is_the_close [closing]
- run 3 · **send** · 4.6s: "¡Sí, Maribel! Trabajamos en Cape Coral y todo el suroeste de Florida. Cuénteme, ¿qué necesita para su bañera?"
  - checks (26): FAIL photo_ask_is_the_close [closing]

### F19 Widow, husband handled it (also N1)
**Set:** fresh · **Class:** quiet  
**Customer:** My husband passed and he was handling this. I'm not sure what to do.

**3/3 pass**
- run 1 · **send** · 2.8s: "I'm so sorry, June. There's no rush on any of this. Whenever you're ready, I'm here to walk you through it."
  - checks (25): all pass
- run 2 · **send** · 2.5s: "I'm so sorry for your loss, June. There's no rush on any of this. Whenever you're ready, I'm here to walk you through it."
  - checks (25): all pass
- run 3 · **send** · 3.0s: "I'm so sorry, June. There's no rush on any of this. Whenever you're ready, I'm here to walk you through it."
  - checks (25): all pass

### F20 Back after 3 follow-ups (also C1)
**Set:** fresh · **Class:** close  
**Customer:** sorry, been crazy busy

**3/3 pass**
- run 1 · **send** · 3.4s: "No worries at all, Trish! Your estimate is still good. Here's the booking link whenever you're ready: https://calendar.bathtubpros.com"
  - checks (26): all pass
- run 2 · **send** · 3.3s: "No worries at all, Trish! Your estimate is still good. Here's the booking link whenever you're ready: https://calendar.bathtubpros.com"
  - checks (26): all pass
- run 3 · **send** · 5.9s: "No worries at all, Trish, life gets busy. Your estimate's still good. Here's the booking link whenever you're ready: https://calendar.bathtubpros.com"
  - checks (26): all pass

### F21 Website $299 vs combo quote (also C4)
**Set:** fresh · **Class:** close  
**Customer:** Your website says $299 but you quoted me way more. What gives?

**3/3 pass**
- run 1 · **send** · 4.6s: "Good question, Stan! The $299 starting price is for most standard tubs. A one-piece tub/shower combo is a different job, priced on your own estimate at $649. When you're ready, you can grab a time here: https://calendar.bathtubpros.com"
  - checks (28): all pass
- run 2 · **send** · 4.1s: "Fair question, Stan. The $299 starting price is for most standard tubs. A one-piece tub/shower combo is a different job, priced on your own estimate of $649. You can grab a time here: https://calendar.bathtubpros.com"
  - checks (28): all pass
- run 3 · **send** · 6.0s: "Good question, Stan! The $299 starting price is for most standard tubs. A one-piece tub/shower combo is a different job, priced on your own estimate at $649. You can grab a time here when ready: https://calendar.bathtubpros.com"
  - checks (28): all pass

### F22 Bait and switch, angry
**Set:** fresh · **Class:** any  
**Customer:** This is bait and switch. $299 advertised and you want how much?

**3/3 pass**
- run 1 · **send** · 8.0s: "I understand, Fran. The $299 starting price is for most standard tubs. A one-piece tub/shower combo is a different job, priced on its own estimate. Your estimate at $649 stands."
  - checks (27): all pass
- run 2 · **send** · 6.4s: "I understand, Fran! The $299 starting price is for most standard tubs. A one-piece tub/shower combo is a different job, and yours is priced on your own estimate at $649."
  - checks (27): all pass
- run 3 · **send** · 4.6s: "I understand, Fran! The $299 starting price is for most standard tubs. A one-piece tub/shower combo is a different job, priced on your own estimate at $649."
  - checks (27): all pass

### F23 Spanish: $299 vs combo quote
**Set:** fresh · **Class:** close  
**Customer:** Su página dice $299, ¿por qué me cotizaron mucho más?

**2/3 pass**
- run 1 · **send** · 7.1s: "Buena pregunta, Ramón. El precio inicial de $299 es para la mayoría de las bañeras estándar. La combinación de una pieza es un trabajo diferente, por eso se cotiza en su propio estimado."
  - checks (29): FAIL closes_with_one_step [closing] (decision=send_now; last: 'La combinación de una pieza es un trabajo diferente, por eso se cotiza')
- run 2 · **send** · 5.5s: "Buena pregunta, Ramón. El precio inicial de $299 es para la mayoría de las bañeras estándar. La combinación de una pieza es un trabajo distinto, por eso su estimado es $649. Cuando guste, puede reservar aquí: https://calendar.bathtubpros.com"
  - checks (29): all pass
- run 3 · **send** · 7.5s: "Buena pregunta, Ramón. El precio inicial de $299 es para la mayoría de las bañeras estándar. La combinación de bañera y ducha de una pieza es un trabajo diferente, con precio según su propio estimado de $649. Cuando esté listo, puede reservar aquí: https://calendar.bathtubpros.com"
  - checks (29): all pass

### C7 Promised follow-up after meeting wife (sweep)
**Set:** closing · **Class:** close  
**Customer:** (proactive follow-up, no inbound)

**3/3 pass**
- run 1 · **send** · 7.7s: "Hi Wes! Checking in as promised — did you and your wife get a chance to talk? Any questions on the $449 Silver estimate, just text me. When you're ready you can grab a time here: https://calendar.bathtubpros.com"
  - checks (25): all pass
- run 2 · **send** · 7.2s: "Hi Wes! Hope the weekend chat with your wife went well. Any questions on the $449 Silver estimate? Want me to get you on the schedule?"
  - checks (25): all pass
- run 3 · **send** · 6.5s: "Hi Wes! Hope the weekend chat with your wife went well. Your $449 Silver estimate is still good. Want me to get you on the schedule?"
  - checks (25): all pass

### C8 Bonnie: soak, two estimates, hubby
**Set:** closing · **Class:** close  
**Customer:** I received it but considerably more than on line prices. I will be using the tub to soak so will that still hold up? I'm getting two estimates and hubby would want to talk about what you actually do as we would do but health issues won't permit right now

**3/3 pass**
- run 1 · **send** · 6.9s: "Fair question, Bonnie! The $299 starting price is for most standard tubs; a one-piece combo is a different job, so your $649 estimate holds. Gold is built for soaking and holds up to daily use. Just no essential oils or bath bombs. When you're ready, you can grab a time here: https://calendar.bathtubpros.com"
  - checks (25): all pass
- run 2 · **send** · 6.6s: "Fair question, Bonnie. The $299 starting price is for most standard tubs; a one-piece combo is a different job, and your estimate is $649. Gold is built for soaking and holds up to daily use.

Just no essential oils or bath bombs in any refinished tub. When you're ready, you can grab a time here: https://calendar.bathtubpros.com"
  - checks (25): all pass
- run 3 · **send** · 5.5s: "Fair question, Bonnie! The $299 starting price is for most standard tubs; a one-piece tub/shower combo is a different job, priced on your own $649 estimate.

Gold is built for soaking and holds up to daily use. Just no essential oils or bath bombs in any refinished tub. When you're ready, you can grab a time here: https://calendar.bathtubpros.com"
  - checks (25): all pass

### N4 Stop texting me
**Set:** closing · **Class:** quiet  
**Customer:** Stop texting me

**3/3 pass**
- run 1 · **send** · 3.0s: "Understood, Lou. We won't text again."
  - checks (25): all pass
- run 2 · **send** · 3.7s: "Understood, Lou. We won't text you again."
  - checks (25): all pass
- run 3 · **send** · 3.0s: "Understood, Lou. We will stop texting you. Sorry for the bother."
  - checks (25): all pass
