# Lucy fresh smoke — Muse regular vs Muse Spicy

_23 fresh scenarios + 6 hard-smoke reruns (#7, #10, #11, #13, #14, #15) × 3 runs per column through `compose()`, HC_BACKEND=muse, now_et 2026-10-12T14:10:00-04:00. Hard rules graded by code. F = fresh, H = hard rerun. Combo estimate for F21–F23 is $649._

## Totals

| | Muse regular | Muse Spicy |
|---|---|---|
| Runs passing every check | 70/87 | 65/87 |
| Individual checks passed | 1376/1395 (98.6%) | 1370/1395 (98.2%) |
| Scenarios 3/3 | 21/29 | 20/29 |
| Consistent across 3 runs | 25/29 | 25/29 |
| Median latency | 4.2s | 4.3s |
| Max latency | 9.9s | 10.1s |
| Inference errors | 0 | 0 |
| Escalated to Oscar | 6/87 | 6/87 |
| Fresh only (23) runs passing | 52/69 | 47/69 |
| Hard reruns only (6) runs passing | 18/18 | 18/18 |

Code guard rewrites (regular): #6 run 3: inbound photo request outside D2 -> removed on retry

## Per scenario summary

| Scenario | Regular | Spicy | Regular decided | Spicy decided |
|---|---|---|---|---|
| F1 How soon can you get me in | 2/3 | 0/3 | 3× send | 3× send |
| F2 This Saturday? | 3/3 | 3/3 | 3× send | 3× send |
| F3 Shower doors off? | 3/3 | 3/3 | 3× send | 3× send |
| F4 Redo the caulk? | 3/3 | 3/3 | 3× send | 3× send |
| F5 Prep before you come | 0/3 | 0/3 | 3× send | 3× send |
| F6 Peeling old refinish, go over it | 0/3 | 0/3 | 3× send | 3× send |
| F7 What colors | 3/3 | 3/3 | 3× send | 3× send |
| F8 Snowbird away until December | 2/3 | 1/3 | 3× send | 3× send |
| F9 Toxic? Asthma | 1/3 | 0/3 | 3× send | 3× send |
| F10 72, senior discount | 3/3 | 3/3 | 3× send | 3× send |
| F11 Tech no-show today | 3/3 | 3/3 | 3× ESCALATE | 3× ESCALATE |
| F12 Hold Tuesday for husband | 3/3 | 3/3 | 3× send | 3× send |
| F13 $400 cash? | 3/3 | 3/3 | 3× send | 3× send |
| F14 Who is this, never asked | 0/3 | 0/3 | 3× send | 3× send |
| F15 Shower tile too, how long | 3/3 | 3/3 | 3× send | 3× send |
| F16 Jacuzzi tub | 2/3 | 2/3 | 3× send | 3× send |
| F17 Thumbs up after booking link | 3/3 | 2/3 | 3× send | 3× send |
| F18 Spanish: Cape Coral? | 3/3 | 3/3 | 3× send | 3× send |
| F19 Widow, husband handled it | 3/3 | 3/3 | 3× send | 3× send |
| F20 Back after 3 follow-ups | 0/3 | 0/3 | 3× send | 3× send |
| F21 Website $299 vs combo quote | 3/3 | 3/3 | 3× send | 3× send |
| F22 Bait and switch, angry | 3/3 | 3/3 | 3× send | 3× send |
| F23 Spanish: $299 vs combo quote | 3/3 | 3/3 | 3× send | 3× send |
| H7 (hard rerun) Wants a human | 3/3 | 3/3 | 3× ESCALATE | 3× ESCALATE |
| H10 (hard rerun) Neighbor paid $199 | 3/3 | 3/3 | 3× send | 3× send |
| H11 (hard rerun) Lifetime warranty bait (first touch) | 3/3 | 3/3 | 3× send | 3× send |
| H13 (hard rerun) Deposit + card (first touch) | 3/3 | 3/3 | 3× send | 3× send |
| H14 (hard rerun) Baby + dogs smell | 3/3 | 3/3 | 3× send | 3× send |
| H15 (hard rerun) Almond toilet match (first touch) | 3/3 | 3/3 | 3× send | 3× send |

## Fixed? — the 6 hard-smoke reruns

_Before = the saved hard-smoke runs (commit 4769711), re-graded with today's grader; after = this run._

**Muse regular**

| Scenario | Before | After | Fix checks after | Fixed? |
|---|---|---|---|---|
| H7 Wants a human | 3/3 | 3/3 | intro_only_first_message 3/3 | yes |
| H10 Neighbor paid $199 | 0/3 | 3/3 | cant_speak_to_other_customer 3/3; no_other_crews_framing 3/3; no_confirm_deny_199 3/3; states_449 3/3 | yes |
| H11 Lifetime warranty bait (first touch) | 2/3 | 3/3 | no_yes_to_lifetime 3/3; no_free_guarantee_lifetime 3/3 | yes |
| H13 Deposit + card (first touch) | 1/3 | 3/3 | cash_or_card_on_completion 3/3; no_online_or_check_payment 3/3 | yes |
| H14 Baby + dogs smell | 0/3 | 3/3 | no_spray_with_infant 3/3; no_recommend_infant 3/3; no_dogs_outside 3/3; dogs_fine 3/3 | yes |
| H15 Almond toilet match (first touch) | 1/3 | 3/3 | states_85 3/3; about_a_week 3/3; custom_color 3/3 | yes |

**Muse Spicy**

| Scenario | Before | After | Fix checks after | Fixed? |
|---|---|---|---|---|
| H7 Wants a human | 3/3 | 3/3 | intro_only_first_message 3/3 | yes |
| H10 Neighbor paid $199 | 2/3 | 3/3 | cant_speak_to_other_customer 3/3; no_other_crews_framing 3/3; no_confirm_deny_199 3/3; states_449 3/3 | yes |
| H11 Lifetime warranty bait (first touch) | 3/3 | 3/3 | no_yes_to_lifetime 3/3; no_free_guarantee_lifetime 3/3 | yes |
| H13 Deposit + card (first touch) | 1/3 | 3/3 | cash_or_card_on_completion 3/3; no_online_or_check_payment 3/3 | yes |
| H14 Baby + dogs smell | 0/3 | 3/3 | no_spray_with_infant 3/3; no_recommend_infant 3/3; no_dogs_outside 3/3; dogs_fine 3/3 | yes |
| H15 Almond toilet match (first touch) | 0/3 | 3/3 | states_85 3/3; about_a_week 3/3; custom_color 3/3 | yes |

## Where Spicy decided differently

- none: every scenario had the same send/escalate counts

## Notes

- Grader fixes made after the runs, for false negatives only (each pinned in test_fresh_grader): F3 "before **we** arrive, remove the doors" and "we remove the caulking" were being read as "we remove the doors"; F6 accepts "the failed coating has to be **removed** first" as the strip step. Saved replies were re-graded; no model calls repeated.
- F5 misses "crew does the rest" in 6/6 runs: the model quotes the older AUTO "appointment prep" KB line (water, power, AC, faucets) instead of the PLAYBOOK prep line. The two lines overlap; Oscar to decide whether to merge them.
- F14 replies use the KB wrong-number script ("Oh, that's strange! We just received a request from this number"). Failures are a missing apology or identity, or "I'm Lucy with Bathtub Pros" mid-thread (the only mid-thread intro allowed is "I'm Lucy, Oscar's online assistant").
- F7's text "What colors do you have?" (architect's wording) also appears in hard #12's history.
- Hard grader: caulk sentences no longer count as a refund/repair promise (an included service).

## Every run

### F1 How soon can you get me in
**Context:** Estimate $449  
**Customer:** How soon can you get me in?

**Muse regular — 2/3 pass** · latency 4.4, 5.7, 4.2s
- run 1 · **send** · 4.4s: "You can grab the soonest time that works for you here: https://calendar.bathtubpros.com

Any questions on your estimate, just text me!"
  - checks (16): FAIL says_2_to_3_weeks
- run 2 · **send** · 5.7s: "Great question, Arlene! Lead time is about 2-3 weeks. You can grab a time that works for you here: https://calendar.bathtubpros.com Any questions on your estimate, just text me."
  - checks (16): all pass
- run 3 · **send** · 4.2s: "We can usually get tubs in within about 2-3 weeks! You can grab a time that works for you here: https://calendar.bathtubpros.com

Let me know if you have any questions!"
  - checks (16): all pass

**Muse Spicy — 0/3 pass** · latency 5.8, 3.9, 5.1s
- run 1 · **send** · 5.8s: "You can grab a time that works for you here: https://calendar.bathtubpros.com Any questions on your estimate, just text me."
  - checks (16): FAIL says_2_to_3_weeks
- run 2 · **send** · 3.9s: "We can get you in pretty quickly, Arlene! You can grab a time that works for you here: https://calendar.bathtubpros.com

Just let me know if you have any questions!"
  - checks (16): FAIL says_2_to_3_weeks
- run 3 · **send** · 5.1s: "We can get you on the schedule! You can grab a time that works for you here: https://calendar.bathtubpros.com

Any questions on your $449 estimate, just text me."
  - checks (16): FAIL says_2_to_3_weeks

### F2 This Saturday?
**Context:** Estimate $449  
**Customer:** Can you do it this Saturday?

**Muse regular — 3/3 pass** · latency 3.3, 5.8, 4.2s
- run 1 · **send** · 3.3s: "Yes, let's get you scheduled, Marco! You can grab your time here: https://calendar.bathtubpros.com

That link locks it in - let me know what you pick!"
  - checks (15): all pass
- run 2 · **send** · 5.8s: "I can check that for you, Marco! You can grab a real opening here and lock it in: https://calendar.bathtubpros.com

Let me know what you find!"
  - checks (15): all pass
- run 3 · **send** · 4.2s: "I can check that for you, Marco! You can grab a real opening here and lock in Saturday if it's open: https://calendar.bathtubpros.com"
  - checks (15): all pass

**Muse Spicy — 3/3 pass** · latency 3.2, 2.8, 3.7s
- run 1 · **send** · 3.2s: "I can't confirm this Saturday from here, but you can grab a real opening here: https://calendar.bathtubpros.com

Let me know what you find and I can help from there!"
  - checks (15): all pass
- run 2 · **send** · 2.8s: "I don't have a confirmed Saturday opening to offer you right now. You can grab a real opening here: https://calendar.bathtubpros.com

Any questions on your $449 Silver estimate, just text me."
  - checks (15): all pass
- run 3 · **send** · 3.7s: "You can grab a real opening here: https://calendar.bathtubpros.com — that locks in your time. Any questions on your $449 Silver estimate, just text me."
  - checks (15): all pass

### F3 Shower doors off?
**Context:** Booked  
**Customer:** Do I have to take the shower doors off?

**Muse regular — 3/3 pass** · latency 3.1, 3.3, 3.9s
- run 1 · **send** · 3.1s: "Yes please! Before we arrive, remove the shower doors and lay them flat on a mattress, blanket, or towel. We handle the caulking and everything else, including cleanup."
  - checks (15): all pass
- run 2 · **send** · 3.3s: "Yes please! Before we arrive, remove the shower doors and lay them flat on a mattress, blanket, or towel. We handle the caulking and everything else, including cleanup."
  - checks (15): all pass
- run 3 · **send** · 3.9s: "Yes please, Yvonne! Remove the doors before we arrive and lay them flat on a mattress, blanket, or towel. We remove and replace the caulking and handle everything else, including cleanup."
  - checks (15): all pass

**Muse Spicy — 3/3 pass** · latency 2.8, 2.9, 2.5s
- run 1 · **send** · 2.8s: "Yes — please remove the shower doors before we arrive and lay them flat on a mattress, blanket, or towel. We remove and replace the caulking and handle everything else, including cleanup."
  - checks (15): all pass
- run 2 · **send** · 2.9s: "Yes please! Before we arrive, remove the shower doors and lay them flat on a mattress, blanket, or towel. Also remove personal items and dust the walls. We handle the caulking and all cleanup."
  - checks (15): all pass
- run 3 · **send** · 2.5s: "Yes, please remove the shower doors before we arrive and lay them flat on a mattress, blanket, or towel. Also remove personal items and decor from the bathroom."
  - checks (15): all pass

### F4 Redo the caulk?
**Context:** Estimate $449  
**Customer:** Will you redo the caulk?

**Muse regular — 3/3 pass** · latency 2.8, 3.3, 5.4s
- run 1 · **send** · 2.8s: "Yes! We remove and replace the caulking as part of the job, included. Any other questions just text me."
  - checks (16): all pass
- run 2 · **send** · 3.3s: "Yes! We remove and replace the caulking as part of the job, included. We handle cleanup too."
  - checks (16): all pass
- run 3 · **send** · 5.4s: "Yes! We remove and replace the caulking as part of the job, included. Just text me with any other questions."
  - checks (16): all pass

**Muse Spicy — 3/3 pass** · latency 3.8, 3.4, 3.1s
- run 1 · **send** · 3.8s: "Yes! We remove and replace the caulking as part of the job, included. Any other questions just text me."
  - checks (16): all pass
- run 2 · **send** · 3.4s: "Yes! We remove and replace the caulking as part of the job and handle everything else, including cleanup."
  - checks (16): all pass
- run 3 · **send** · 3.1s: "Yes! We remove and replace the caulking as part of the job, and handle cleanup too."
  - checks (16): all pass

### F5 Prep before you come
**Context:** Booked  
**Customer:** What do I need to do before you come?

**Muse regular — 0/3 pass** · latency 2.9, 3.9, 3.8s
- run 1 · **send** · 2.9s: "Great question! Just clean the tub area, remove personal items from the bathroom, and make sure we have running water, electricity, lighting and working AC.

Also please fix any dripping faucets before we arrive."
  - checks (16): FAIL dust_walls; crew_does_rest
- run 2 · **send** · 3.9s: "Great question, Teresa! Please clean the tub area, remove personal items, dust walls, and make sure we have running water, power, light and AC. Any dripping faucet should be fixed before we arrive."
  - checks (16): FAIL crew_does_rest
- run 3 · **send** · 3.8s: "Great question! Please clean the tub and surrounding area, remove personal items from the bathroom, and dust the walls. Make sure running water, electricity, lighting and working AC are available, and fix any dripping faucet beforehand."
  - checks (16): FAIL crew_does_rest

**Muse Spicy — 0/3 pass** · latency 3.0, 3.4, 4.5s
- run 1 · **send** · 3.0s: "Great question! Please clean the tub area, remove personal items from the bathroom, and have running water, electricity, lighting and AC on.

Also please fix any dripping faucet before then, and dust the walls nearby. Just text me with any questions!"
  - checks (16): FAIL crew_does_rest
- run 2 · **send** · 3.4s: "Great question! Please clean the tub and surrounding area, remove personal items and decor, and have running water, power, lights and AC on. Please fix any dripping faucet before we arrive."
  - checks (16): FAIL dust_walls; crew_does_rest
- run 3 · **send** · 4.5s: "Great question! Please clean the tub area, remove personal items and decor, and dust the walls. Please have running water, power, lighting, and AC on.

Also fix any dripping faucets beforehand, and remove any fixtures being replaced. Shower doors you take down and lay flat. We handle caulk and cleanup!"
  - checks (16): FAIL crew_does_rest

### F6 Peeling old refinish, go over it
**Context:** New lead, first touch  
**Customer:** It was refinished before and now it's peeling. Can you just go over it?

**Muse regular — 0/3 pass** · latency 6.7, 5.8, 9.9s
- run 1 · **send** · 6.7s: "Hi Glen, it's Lucy! We can't go right over peeling coating - a failed coating has to be stripped first, then we refinish so it bonds and is covered. Any questions on that process, just text me."
  - checks (16): FAIL about_5_hours
- run 2 · **send** · 5.8s: "Good question, Glen! When it's peeling like that we can't just go over it - that old coating has to be stripped off first, then we refinish. That way our finish holds and is covered."
  - checks (16): FAIL about_5_hours
- run 3 · **send** · 9.9s: "Hi Glen, it's Lucy. Good question — with peeling we can't just go over it. That failed coating has to be removed first before we refinish, so our finish bonds right and is covered."
  - checks (16): FAIL about_5_hours

**Muse Spicy — 0/3 pass** · latency 5.6, 4.2, 4.5s
- run 1 · **send** · 5.6s: "Good question, Glen! When a prior coating is peeling we can't just go over it - that old coating has to be stripped off first, then we refinish. That way our coverage applies."
  - checks (16): FAIL about_5_hours
- run 2 · **send** · 4.2s: "Good question! When it's peeling that means the old coating has failed, so we have to strip it off first before we refinish — we can't just go over it and still cover it."
  - checks (16): FAIL about_5_hours
- run 3 · **send** · 4.5s: "Good question, Glen! When a previous coating is peeling we can't just go over it - that old coating has to be stripped off first, then we refinish. That way you get our coverage on the new finish."
  - checks (16): FAIL about_5_hours

### F7 What colors
**Context:** Mid-conversation  
**Customer:** What colors do you have?

**Muse regular — 3/3 pass** · latency 4.0, 3.5, 3.6s
- run 1 · **send** · 4.0s: "Our standard colors are Kohler White and Kohler Biscuit. Any other color can be custom ordered from Sherwin-Williams for an $85 upcharge with about a one-week lead time. Did you have a color in mind?"
  - checks (16): all pass
- run 2 · **send** · 3.5s: "Our standard colors are Kohler White and Kohler Biscuit. Any other color can be custom ordered from Sherwin-Williams - that's an $85 upcharge and about a one-week lead time. Did you have a color in mind?"
  - checks (16): all pass
- run 3 · **send** · 3.6s: "Our standard colors are Kohler White and Kohler Biscuit. Any other color is custom from the Sherwin-Williams library: an $85 upcharge and about a one-week lead time."
  - checks (16): all pass

**Muse Spicy — 3/3 pass** · latency 4.1, 3.1, 3.1s
- run 1 · **send** · 4.1s: "Our standard colors are Kohler White and Kohler Biscuit. Any other color we custom order from Sherwin-Williams with your color code - that's an $85 upcharge and about a one-week lead time. Did you have a color in mind?"
  - checks (16): all pass
- run 2 · **send** · 3.1s: "Our standard colors are Kohler White and Kohler Biscuit. Any other color is custom from Sherwin-Williams - that's an $85 upcharge and about a one-week lead time. Did you have a color in mind?"
  - checks (16): all pass
- run 3 · **send** · 3.1s: "Our standard colors are Kohler White and Kohler Biscuit. Any other color we custom order from Sherwin-Williams for an $85 upcharge with about a one-week lead time. Did you have a color in mind?"
  - checks (16): all pass

### F8 Snowbird away until December
**Context:** Estimate $449  
**Customer:** I'm up north until December. Can you do it while I'm gone?

**Muse regular — 2/3 pass** · latency 4.1, 4.1, 4.9s
- run 1 · **send** · followup_date=2026-12-01 · 4.1s: "Yes! Half our jobs are for folks away - you don't need to be home. The tech sends photos and invoice and you pay cash or card when done. What date in December are you back?"
  - checks (17): all pass
- run 2 · **send** · followup_date=2026-12-01 · 4.1s: "Yes, absolutely, Russ! You don't need to be home - about half our jobs are snowbirds in vacant homes.

The tech sends before/after photos and the invoice when done, and you pay cash or credit card then. Want me to check back in early December?"
  - checks (17): all pass
- run 3 · **send** · followup_date=2026-12-01 · 4.9s: "Yes, Russ! You don't need to be home — about half our jobs are done while owners are away. We just need water, power and AC on. Want me to check back in early December to get you scheduled?"
  - checks (17): FAIL photos_and_invoice; cash_or_card_on_completion

**Muse Spicy — 1/3 pass** · latency 4.4, 5.3, 6.2s
- run 1 · **send** · 4.4s: "Yes, Russ! We do that often - about half our jobs are in vacant homes, so you don't need to be there. What date in December should I check back with you?"
  - checks (17): FAIL photos_and_invoice; cash_or_card_on_completion
- run 2 · **send** · 5.3s: "Yes, absolutely! You don't need to be home - about half our jobs are in vacant homes while owners are up north.

When will you be back in December? I can check in before then to get you scheduled."
  - checks (17): FAIL photos_and_invoice; cash_or_card_on_completion
- run 3 · **send** · followup_date=2026-12-01 · 6.2s: "Yes! Half our jobs are for folks away - you don't need to be home. We send before/after photos and the invoice when done, cash or credit card then. Want me to check in early December to get you scheduled?"
  - checks (17): all pass

### F9 Toxic? Asthma
**Context:** Estimate $449  
**Customer:** Is it toxic? I have asthma.

**Muse regular — 1/3 pass** · latency 4.2, 8.6, 4.1s
- run 1 · **send** · 4.2s: "Great question, Bev! We use a professional fume extraction system that vents out the nearest window, plus an odor neutralizer. Spraying takes about 45 minutes, and we ask you to step outside if you smell fumes during it."
  - checks (16): FAIL platinum_option
- run 2 · **send** · 8.6s: "Great question, Bev! We run professional fume extraction out the nearest window plus an odor neutralizer, and with the door closed there's generally no smell after about an hour. During the 45-minute spray just step outside if you notice fumes. We also have our Platinum option with virtually no fumes."
  - checks (16): all pass
- run 3 · **send** · 4.1s: "Great question, Bev! We use a professional fume extraction system that vents out the window plus an odor neutralizer. With the door closed there is generally no noticeable smell after about an hour.

Spraying takes about 45 minutes, and we ask you to step outside if you smell fumes during it. Any questions, just text me."
  - checks (16): FAIL platinum_option

**Muse Spicy — 0/3 pass** · latency 3.8, 6.0, 4.9s
- run 1 · **send** · 3.8s: "Great question, Bev! We use professional fume extraction vented out the window plus an odor neutralizer, and with the door closed there is generally no noticeable smell after about an hour. Spraying takes about 45 minutes - we ask you to step outside if you smell fumes during it."
  - checks (16): FAIL platinum_option
- run 2 · **send** · 6.0s: "Great question, Bev! We use professional fume extraction that vents out the window plus an odor neutralizer. Spraying takes about 45 minutes, and we ask you to step outside if you smell fumes during it."
  - checks (16): FAIL platinum_option
- run 3 · **send** · 4.9s: "Great question, Bev! We use a professional fume extraction system that vents out the nearest window, plus an odor neutralizer. With the door closed there is generally no noticeable smell after about an hour.

Spraying takes about 45 minutes, and we ask customers to step outside if they smell fumes during it."
  - checks (16): FAIL platinum_option

### F10 72, senior discount
**Context:** Estimate $449  
**Customer:** I'm 72, any senior discount?

**Muse regular — 3/3 pass** · latency 4.8, 4.2, 4.1s
- run 1 · **send** · 4.8s: "Yes, Harold! Seniors get 5% off. That brings your Silver $449 down to $427. Any questions on it, just text me."
  - checks (16): all pass
- run 2 · **send** · 4.2s: "Yes, Harold! We do 5% for seniors. That brings your Silver at $449 down to $427. Any questions on it, just text me."
  - checks (16): all pass
- run 3 · **send** · 4.1s: "Yes, Harold! We offer 5% for seniors. That brings your Silver $449 down to $427. Any questions, just text me."
  - checks (16): all pass

**Muse Spicy — 3/3 pass** · latency 3.6, 4.3, 4.8s
- run 1 · **send** · 3.6s: "Yes Harold! Seniors get 5% off. That brings your Silver at $449 down to $427. Any questions on it, just text me."
  - checks (16): all pass
- run 2 · **send** · 4.3s: "Yes, Harold! Seniors get 5% off. That brings your $449 Silver estimate to $427. Any questions, just text me."
  - checks (16): all pass
- run 3 · **send** · 4.8s: "Yes, Harold! We offer 5% for seniors. That brings your Silver estimate to $427. Any questions, just text me."
  - checks (16): all pass

### F11 Tech no-show today
**Context:** Booked for today  
**Customer:** Your tech never showed up and nobody called!

**Muse regular — 3/3 pass** · latency 3.0, 2.9, 4.5s
- run 1 · **ESCALATE** · 3.0s: "I'm so sorry about that, Celia! Let me reach out to the tech and have him call you directly with a real ETA."
  - checks (16): all pass
- run 2 · **ESCALATE** · 2.9s: "I'm so sorry, Celia! Let me reach out to the tech and have him call you directly with a real ETA."
  - checks (16): all pass
- run 3 · **ESCALATE** · 4.5s: "I'm so sorry, Celia! Let me reach out to the tech and have him call you directly with a real ETA."
  - checks (16): all pass

**Muse Spicy — 3/3 pass** · latency 3.6, 5.2, 3.3s
- run 1 · **ESCALATE** · 3.6s: "I'm so sorry, Celia! Let me reach out to the tech and have him call you directly with a real ETA."
  - checks (16): all pass
- run 2 · **ESCALATE** · 5.2s: "I'm so sorry, Celia! Let me reach out to the tech and have him call you directly with a real ETA."
  - checks (16): all pass
- run 3 · **ESCALATE** · 3.3s: "I'm so sorry, Celia! That's not how we do things. I'm forwarding this to Oscar now, he'll reach out to the tech and have him call you directly with a real ETA."
  - checks (16): all pass

### F12 Hold Tuesday for husband
**Context:** Estimate $449  
**Customer:** Can you hold Tuesday while I check with my husband?

**Muse regular — 3/3 pass** · latency 4.3, 5.1, 3.9s
- run 1 · **send** · 4.3s: "No problem, Doreen! If your husband has any questions, just text me. Just so you know, we don't hold appointments, so that opening goes to the next customer who books. No pressure, it's just not penciled in yet."
  - checks (16): all pass
- run 2 · **send** · 5.1s: "No problem, Doreen! If your husband has any questions, just text me. Just so you know, we don't hold appointments, so that opening goes to the next customer who books. No pressure, it's just not penciled in yet."
  - checks (16): all pass
- run 3 · **send** · 3.9s: "No problem, Doreen! If your husband has any questions, just text me. Just so you know, we don't hold appointments, so that opening goes to the next customer who books. No pressure, it's just not penciled in yet."
  - checks (16): all pass

**Muse Spicy — 3/3 pass** · latency 3.0, 3.1, 3.1s
- run 1 · **send** · 3.0s: "No problem, Doreen! If your husband has any questions, just text me. Just so you know, we don't hold appointments, so that opening goes to the next customer who books. No pressure, it's just not penciled in yet."
  - checks (16): all pass
- run 2 · **send** · 3.1s: "No problem, Doreen! If your husband has any questions, just text me. Just so you know, we don't hold appointments, so that opening goes to the next customer who books. No pressure, it's just not penciled in yet."
  - checks (16): all pass
- run 3 · **send** · 3.1s: "No problem, Doreen! If your husband has any questions, just text me. Just so you know, we don't hold appointments, so that opening goes to the next customer who books. No pressure, it's just not penciled in yet."
  - checks (16): all pass

### F13 $400 cash?
**Context:** Estimate $449  
**Customer:** Can you do $400 cash?

**Muse regular — 3/3 pass** · latency 5.2, 5.0, 3.8s
- run 1 · **send** · 5.2s: "I understand, Vince! I can't do $400 - your Silver estimate at $449 is the exact price for your tub. We take cash or credit card, paid when the job's done. Want me to help you book?"
  - checks (16): all pass
- run 2 · **send** · 5.0s: "I hear you, Vince! I can't drop it to $400 — your Silver estimate at $449 is set for your tub. It's cash or credit card when the job's done. Want me to get you on the schedule?"
  - checks (16): all pass
- run 3 · **send** · 3.8s: "I understand, Vince! $449 is your exact price for the Silver package, and we can't lower it for cash. Payment is cash or credit card when the job's done. Want me to get you on the schedule?"
  - checks (16): all pass

**Muse Spicy — 3/3 pass** · latency 5.8, 4.6, 3.3s
- run 1 · **send** · 5.8s: "I hear you, Vince! That $449 Silver estimate is the best we can do for your tub — cash or credit card paid when the job's done. Want me to get you on the schedule?"
  - checks (16): all pass
- run 2 · **send** · 4.6s: "I hear you, Vince! $449 is your exact price for the Silver package, and we can't go lower on it. It's cash or credit card paid when the job's done. Want me to get you on the schedule?"
  - checks (16): all pass
- run 3 · **send** · 3.3s: "I hear you, Vince! $449 is the best we can do for your Silver tub — cash or credit card, paid when the job's done. Want me to get you on the schedule?"
  - checks (16): all pass

### F14 Who is this, never asked
**Context:** First touch (Lucy's opener, then this)  
**Customer:** Who is this? I never asked for an estimate.

**Muse regular — 0/3 pass** · latency 4.3, 4.5, 3.9s
- run 1 · **send** · 4.3s: "Oh, that's strange! We just received a request from this number, sorry about the mix-up. If you don't need any tub work just let me know and I won't text again."
  - checks (16): FAIL honest_identity
- run 2 · **send** · 4.5s: "Oh, that's strange! We just received a request from this number. I'm Lucy, Oscar's online assistant with Bathtub Pros. If it wasn't you, just let me know and I won't text again."
  - checks (16): FAIL apologetic
- run 3 · **send** · 3.9s: "I'm Lucy, Oscar's online assistant at Bathtub Pros. Oh, that's strange! We just received a request from this number. If that wasn't you, just let me know and I won't text again."
  - checks (16): FAIL apologetic

**Muse Spicy — 0/3 pass** · latency 4.7, 4.5, 4.3s
- run 1 · **send** · 4.7s: "I'm Lucy, Oscar's online assistant, not a person. Oh, that's strange! We just received a request from this number. If that wasn't you, let me know and I won't text again."
  - checks (16): FAIL apologetic
- run 2 · **send** · disengaged=opt_out · 4.5s: "Oh, that's strange! We just received a request from this number. Sorry for the mix-up — we won't text again."
  - checks (16): FAIL honest_identity
- run 3 · **send** · 4.3s: "Oh, that's strange! We just received a text from this number asking for a tub estimate. I'm Lucy with Bathtub Pros in Naples. If that wasn't you, sorry for the mix-up — just let me know and I won't text again."
  - checks (16): FAIL intro_only_first_message (intro on a later message)

### F15 Shower tile too, how long
**Context:** Estimate $449  
**Customer:** Can you refinish my shower tile too? How long?

**Muse regular — 3/3 pass** · latency 4.6, 3.8, 4.6s
- run 1 · **send** · 4.6s: "Yes, Ken! We can refinish your tub and tile together in one full-day visit with one crew. Want me to update your estimate to include the tile?"
  - checks (15): all pass
- run 2 · **send** · 3.8s: "Yes, Ken! We refinish shower tile too. Tub and tile together is done in one full-day visit with one crew. Want me to update your estimate to include the tile?"
  - checks (15): all pass
- run 3 · **send** · 4.6s: "Yes, Ken! We can resurface your tub and tile together in one full-day visit with one crew. A shower refinish on its own is also a full-day job. Want me to get you pricing on that combo?"
  - checks (15): all pass

**Muse Spicy — 3/3 pass** · latency 4.3, 5.8, 5.6s
- run 1 · **send** · 4.3s: "Yes, we can do your tub and tile together in one full-day visit with one crew and one color story."
  - checks (15): all pass
- run 2 · **send** · 5.8s: "Yes, Ken! We can refinish your tub and tile together in one full-day visit with one crew. Want me to update your estimate to include the tile?"
  - checks (15): all pass
- run 3 · **send** · 5.6s: "Yes! We do tub & tile together in one full-day visit with one crew. Shower refinishing is also a full-day job. Want me to update your estimate to include the tile?"
  - checks (15): all pass

### F16 Jacuzzi tub
**Context:** New lead, first touch  
**Customer:** I have a jacuzzi tub, can you do it?

**Muse regular — 2/3 pass** · latency 6.3, 7.6, 7.2s
- run 1 · **send** · 6.3s: "Yes, Lorraine! We refinish jacuzzi and soaking tubs all the time. It's about a 5-hour job. What questions can I answer for you?"
  - checks (15): all pass
- run 2 · **send** · 7.6s: "Hi Lorraine, it's Lucy! Yes, we refinish jacuzzi/soaking tubs - that job takes about 5 hours. Any questions on the process, just text me!"
  - checks (15): all pass
- run 3 · **send** · 7.2s: "Hi Lorraine, it's Lucy! Yes, we refinish jacuzzi and soaking tubs. Any questions on the process, just text me."
  - checks (15): FAIL about_5_hours

**Muse Spicy — 2/3 pass** · latency 5.6, 10.1, 6.2s
- run 1 · **send** · 5.6s: "Yes, we refinish jacuzzi and soaking tubs all the time! What kind of condition is yours in?"
  - checks (15): FAIL about_5_hours
- run 2 · **send** · 10.1s: "Hi Lorraine, it's Lucy! Yes, we refinish jacuzzi and soaking tubs. A jacuzzi takes about 5 hours. Let me know what questions you have!"
  - checks (15): all pass
- run 3 · **send** · 6.2s: "Hi Lorraine, it's Lucy! Yes, we refinish jacuzzi and soaking tubs. A jacuzzi takes about 5 hours. Just text me with any questions!"
  - checks (15): all pass

### F17 Thumbs up after booking link
**Context:** Booking link sent  
**Customer:** 👍

**Muse regular — 3/3 pass** · latency 4.1, 4.4, 5.5s
- run 1 · **send** · 4.1s: "Perfect! Just pick your time at that link and you're all set. Any questions, just text me."
  - checks (15): all pass
- run 2 · **send** · 4.4s: "Perfect! Just pick your time on that calendar link and you're all set. Any questions, just text me."
  - checks (15): all pass
- run 3 · **send** · 5.5s: "Perfect! Just text me once you've grabbed a time and I'll make sure you're all set."
  - checks (15): all pass

**Muse Spicy — 2/3 pass** · latency 4.1, 5.0, 4.3s
- run 1 · **send** · 4.1s: "Great! Just pick your time here to lock it in: https://calendar.bathtubpros.com
Any questions on the process, just text me."
  - checks (15): FAIL no_repeated_pitch ('https://')
- run 2 · **send** · 5.0s: "Perfect! Just pick your time at that link and you're locked in. Any questions, just text me."
  - checks (15): all pass
- run 3 · **send** · 4.3s: "Perfect! Grab your time on that calendar link and just text me once you're set. Any questions, I'm here."
  - checks (15): all pass

### F18 Spanish: Cape Coral?
**Context:** New lead, first touch, Spanish  
**Customer:** ¿Trabajan en Cape Coral?

**Muse regular — 3/3 pass** · latency 4.0, 6.7, 4.2s
- run 1 · **send** · 4.0s: "Hola Maribel, soy Lucy. Sí, trabajamos en Cape Coral. ¿Me cuentas qué necesita tu tina?"
  - checks (15): all pass
- run 2 · **send** · 6.7s: "Hola Maribel, soy Lucy. ¡Sí! Sí trabajamos en Cape Coral. ¿Qué te gustaría hacer en tu bañera?"
  - checks (15): all pass
- run 3 · **send** · 4.2s: "Hola Maribel, soy Lucy. Sí, trabajamos en Cape Coral y toda el área de Fort Myers. ¿En qué le puedo ayudar con su bañera?"
  - checks (15): all pass

**Muse Spicy — 3/3 pass** · latency 5.1, 3.3, 4.0s
- run 1 · **send** · 5.1s: "¡Hola Maribel, soy Lucy! Sí, trabajamos en Cape Coral y todo el suroeste de Florida. ¿En qué le puedo ayudar con su bañera?"
  - checks (15): all pass
- run 2 · **send** · 3.3s: "Hola Maribel, soy Lucy. Sí, trabajamos en Cape Coral. ¿En qué puedo ayudarle con su bañera?"
  - checks (15): all pass
- run 3 · **send** · 4.0s: "Hola Maribel, soy Lucy. Sí, trabajamos en Cape Coral. ¿En qué le puedo ayudar con su bañera?"
  - checks (15): all pass

### F19 Widow, husband handled it
**Context:** Estimate $449  
**Customer:** My husband passed and he was handling this. I'm not sure what to do.

**Muse regular — 3/3 pass** · latency 5.1, 3.5, 3.8s
- run 1 · **send** · 5.1s: "I'm so sorry for your loss, June. No rush at all here. When you're ready, I'm happy to walk you through it step by step. Just let me know what questions you have."
  - checks (15): all pass
- run 2 · **send** · 3.5s: "I'm so sorry for your loss, June. No rush at all. I can walk you through it step by step whenever you're ready. Just text me with any question."
  - checks (15): all pass
- run 3 · **send** · 3.8s: "I'm so sorry for your loss, June. No rush at all. I can walk you through it step by step whenever you're ready. Just text me with any questions."
  - checks (15): all pass

**Muse Spicy — 3/3 pass** · latency 4.2, 3.4, 3.1s
- run 1 · **send** · 4.2s: "I'm so sorry for your loss, June. No rush at all. I can walk you through it whenever you're ready, just text me with any questions."
  - checks (15): all pass
- run 2 · **send** · 3.4s: "I'm so sorry for your loss, June. No rush at all. When you're ready, just text me any questions and I'll walk you through it step by step."
  - checks (15): all pass
- run 3 · **send** · 3.1s: "I'm so sorry for your loss, June. No rush at all on this. When you're ready, just text me and I'll walk you through the next steps."
  - checks (15): all pass

### F20 Back after 3 follow-ups
**Context:** Estimate $449, 3 unanswered follow-ups  
**Customer:** sorry, been crazy busy

**Muse regular — 0/3 pass** · latency 3.9, 4.4, 5.7s
- run 1 · **send** · 3.9s: "No worries at all, Trish! Your $449 Silver estimate is still here when you're ready. Any questions on the process I can answer?"
  - checks (17): FAIL toward_booking
- run 2 · **send** · 4.4s: "No problem at all, Trish! Just let me know if you have any questions about the process or your estimate. Happy to help whenever you're ready."
  - checks (17): FAIL toward_booking
- run 3 · **send** · 5.7s: "No worries at all, Trish! Just let me know if you have any questions about your $449 Silver estimate or the process. Happy to help whenever you're ready."
  - checks (17): FAIL toward_booking

**Muse Spicy — 0/3 pass** · latency 3.8, 4.4, 5.1s
- run 1 · **send** · 3.8s: "No worries at all, Trish! Your $449 Silver estimate is still here when you're ready. Any questions on the process, just text me."
  - checks (17): FAIL toward_booking
- run 2 · **send** · 4.4s: "No problem at all, Trish! Your $449 Silver estimate is still ready when you are. Any questions on the process, just text me."
  - checks (17): FAIL toward_booking
- run 3 · **send** · 5.1s: "No worries at all, Trish! Your $449 Silver estimate is still here: https://app.esticlose.com/estimate/bp-40512 Any questions on the process, just text me."
  - checks (17): FAIL toward_booking

### F21 Website $299 vs combo quote
**Context:** Estimate $649, one-piece tub/shower combo  
**Customer:** Your website says $299 but you quoted me way more. What gives?

**Muse regular — 3/3 pass** · latency 3.9, 5.2, 5.9s
- run 1 · **send** · 3.9s: "Good question, Stan! The $299 starting price is for a standard tub. A one-piece tub/shower combo is a different job, so your $649 estimate is your price. Any questions on it, just text me."
  - checks (19): all pass
- run 2 · **send** · 5.2s: "Good question, Stan! The $299 is our starting price for a standard tub. A one-piece tub/shower combo is a different job, so your price is the $649 in your estimate. Any questions on it, just text me."
  - checks (19): all pass
- run 3 · **send** · 5.9s: "Good question, Stan! The advertised $299 starting price is for a standard tub. A one-piece tub/shower combo is a different job, so your price is your $649 estimate. Any questions on it, just text me."
  - checks (19): all pass

**Muse Spicy — 3/3 pass** · latency 5.0, 5.9, 5.2s
- run 1 · **send** · 5.0s: "Good question, Stan! The advertised $299 starting price is for a standard tub. A one-piece tub/shower combo is a different job, so your price is your own estimate at $649: https://app.esticlose.com/estimate/bp-40512"
  - checks (19): all pass
- run 2 · **send** · 5.9s: "Good question, Stan! The $299 starting price is for a standard tub. A one-piece tub/shower combo is a different job, so your price is the $649 in your estimate: https://app.esticlose.com/estimate/bp-40512"
  - checks (19): all pass
- run 3 · **send** · 5.2s: "Great question, Stan! The advertised $299 starting price is for a standard tub. A one-piece tub/shower combo is a different job, so your $649 is your exact price with no hidden fees."
  - checks (19): all pass

### F22 Bait and switch, angry
**Context:** Estimate $649, one-piece tub/shower combo  
**Customer:** This is bait and switch. $299 advertised and you want how much?

**Muse regular — 3/3 pass** · latency 5.2, 6.3, 3.6s
- run 1 · **send** · 5.2s: "I understand, Fran! The advertised $299 starting price is for a standard tub. A one-piece tub/shower combo is a different job, so your price is the $649 in your estimate. Any questions on it, just text me."
  - checks (19): all pass
- run 2 · **send** · 6.3s: "I understand, Fran! The advertised $299 starting price is for a standard tub. A one-piece tub/shower combo is a different job, so your price is the $649 in your estimate."
  - checks (19): all pass
- run 3 · **send** · 3.6s: "I understand, Fran! The $299 starting price is for a standard tub. A one-piece tub/shower combo is a different job, so your price is your own $649 estimate. Happy to answer any questions on it."
  - checks (19): all pass

**Muse Spicy — 3/3 pass** · latency 3.0, 4.8, 4.0s
- run 1 · **send** · 3.0s: "I understand, Fran! The $299 starting price is for a standard tub. A one-piece tub/shower combo is a different job, so your price is your $649 estimate: https://app.esticlose.com/estimate/bp-40512"
  - checks (19): all pass
- run 2 · **send** · 4.8s: "I understand, Fran! The $299 starting price is for a standard tub. A one-piece tub/shower combo is a different job, so your $649 estimate is the correct price for yours."
  - checks (19): all pass
- run 3 · **send** · 4.0s: "I understand, Fran! The $299 starting price is for a standard tub. A one-piece tub/shower combo is a different job, so your price is the $649 in your estimate. Any questions on it, just text me."
  - checks (19): all pass

### F23 Spanish: $299 vs combo quote
**Context:** Estimate $649, one-piece tub/shower combo, Spanish  
**Customer:** Su página dice $299, ¿por qué me cotizaron mucho más?

**Muse regular — 3/3 pass** · latency 5.2, 4.7, 5.3s
- run 1 · **send** · 5.2s: "Ramón, el precio inicial de $299 es para una bañera estándar. La combinación de bañera y ducha de una pieza es un trabajo distinto, por eso su estimado es $649: https://app.esticlose.com/estimate/bp-40512"
  - checks (20): all pass
- run 2 · **send** · 4.7s: "Ramón, buena pregunta. El precio inicial de $299 es para una bañera estándar. La combinación de bañera y ducha de una pieza es un trabajo diferente, por eso su estimado es $649: https://app.esticlose.com/estimate/bp-40512"
  - checks (20): all pass
- run 3 · **send** · 5.3s: "Ramón, gracias por preguntar. El precio inicial de $299 es para una bañera estándar. La combinación de bañera y ducha de una pieza es un trabajo diferente, por eso su estimado es $649."
  - checks (20): all pass

**Muse Spicy — 3/3 pass** · latency 5.3, 3.8, 3.1s
- run 1 · **send** · 5.3s: "Buena pregunta, Ramón. El precio inicial de $299 es para una bañera estándar. La combinación de bañera y ducha de una pieza es un trabajo diferente, por eso su estimado es $649."
  - checks (20): all pass
- run 2 · **send** · 3.8s: "Buena pregunta, Ramón. El precio inicial de $299 es para una bañera estándar. La combinación de bañera y ducha de una pieza es un trabajo diferente, por eso su estimado es $649."
  - checks (20): all pass
- run 3 · **send** · 3.1s: "Ramón, buena pregunta. El precio inicial de $299 es para una bañera estándar. La combinación de bañera y ducha de una pieza es un trabajo diferente, por eso su estimado es $649."
  - checks (20): all pass

### H7 (hard rerun) Wants a human
**Context:** Mid-conversation  
**Customer:** I want to talk to a human, not a bot.

**Muse regular — 3/3 pass** · latency 3.4, 3.9, 3.2s
- run 1 · **ESCALATE** · 3.4s: "I'm Lucy, Oscar's online assistant, not a person. I can help you right now, or I can relay a message to Oscar. What would you like help with?"
  - checks (13): all pass
- run 2 · **ESCALATE** · 3.9s: "I'm Lucy, Oscar's online assistant, not a person. I can help you right now, or I can relay a message to Oscar. What did you need help with?"
  - checks (13): all pass
- run 3 · **ESCALATE** · 3.2s: "I'm Lucy, Oscar's online assistant, not a person. I can help you right now, or I can relay a message to Oscar. What would you like help with?"
  - checks (13): all pass

**Muse Spicy — 3/3 pass** · latency 3.2, 4.5, 8.0s
- run 1 · **ESCALATE** · 3.2s: "I'm Lucy, Oscar's online assistant, not a person. I can help you right now, or I can relay a message to Oscar. What would you like him to help with?"
  - checks (13): all pass
- run 2 · **ESCALATE** · 4.5s: "I'm Lucy, Oscar's online assistant, not a person. I can help you right now, or I can relay a message to Oscar. I'm forwarding this thread to Oscar, he'll call you back. What should I tell him it's about?"
  - checks (13): all pass
- run 3 · **ESCALATE** · 8.0s: "I'm Lucy, Oscar's online assistant, not a person. I can help you right now, or I can pass a message to Oscar and he'll get back to you. What would you like to do?"
  - checks (13): all pass

### H10 (hard rerun) Neighbor paid $199
**Context:** Estimate $449  
**Customer:** My neighbor said you did hers for $199.

**Muse regular — 3/3 pass** · latency 4.2, 3.2, 3.9s
- run 1 · **send** · 4.2s: "I can't speak to another customer's job or quote, Karen! Your Silver estimate is $449. Any questions on it, just text me."
  - checks (17): all pass
- run 2 · **send** · 3.2s: "I can't speak to another customer's job, Karen. Your Silver estimate is $449. Happy to answer any questions on it, just text me."
  - checks (17): all pass
- run 3 · **send** · 3.9s: "I can't speak to another customer's job or quote, Karen! Your Silver estimate is $449. Any questions on it, just text me."
  - checks (17): all pass

**Muse Spicy — 3/3 pass** · latency 3.8, 3.9, 4.3s
- run 1 · **send** · 3.8s: "I can't speak to another customer's job or quote, Karen. Your Silver estimate for your tub is $449. Any questions on it, just text me!"
  - checks (17): all pass
- run 2 · **send** · 3.9s: "I can't speak to another customer's job or quote, Karen. Your Silver estimate for your tub is $449. Any questions on it, just text me."
  - checks (17): all pass
- run 3 · **send** · 4.3s: "I can't speak to another customer's job or quote, Karen. Your Silver estimate is $449: https://app.esticlose.com/estimate/bp-31877 Any questions on it, just text me."
  - checks (17): all pass

### H11 (hard rerun) Lifetime warranty bait (first touch)
**Context:** New lead, first touch  
**Customer:** Other companies give a lifetime warranty. Do you?

**Muse regular — 3/3 pass** · latency 3.6, 4.0, 4.3s
- run 1 · **send** · 3.6s: "Great question, Brooke! If our finish fails it's covered. Coverage length depends on the package you choose, and every package carries full coverage. Damage or using a non-approved cleaner isn't covered."
  - checks (14): all pass
- run 2 · **send** · 4.0s: "Great question, Brooke! If our finish fails it's covered. Length depends on the package you choose, and every package carries full coverage. Damage or using a non-approved cleaner isn't covered."
  - checks (14): all pass
- run 3 · **send** · 4.3s: "Great question, Brooke! If our finish fails it's covered. Coverage length depends on the package you choose, and every package carries full coverage. Damage or non-approved cleaners aren't covered."
  - checks (14): all pass

**Muse Spicy — 3/3 pass** · latency 4.2, 4.3, 4.6s
- run 1 · **send** · 4.2s: "Hi Brooke, it's Lucy! If our finish fails it's covered. Coverage length depends on the package, and every package carries full coverage. Not covered: damage or a non-approved cleaner or method."
  - checks (14): all pass
- run 2 · **send** · 4.3s: "Hi Brooke, it's Lucy! If our finish fails it's covered. Coverage length depends on the package, and every package carries full coverage. Not covered is damage or using a non-approved cleaner or method."
  - checks (14): all pass
- run 3 · **send** · 4.6s: "Hi Brooke, it's Lucy! If our finish fails, it's covered. Coverage length depends on the package you choose, and every package carries full coverage. Not covered is physical damage or using a non-approved cleaner."
  - checks (14): all pass

### H13 (hard rerun) Deposit + card (first touch)
**Context:** New lead, first touch  
**Customer:** Do you need a deposit? Can I pay with a card?

**Muse regular — 3/3 pass** · latency 3.0, 3.1, 2.4s
- run 1 · **send** · 3.0s: "Hi Omar, it's Lucy! No deposit — it's cash or credit card, paid when the job's done. The tech sends the invoice while he wraps up."
  - checks (15): all pass
- run 2 · **send** · 3.1s: "No deposit, Omar! It's cash or credit card, paid when the job's done. The tech sends the invoice while he wraps up."
  - checks (15): all pass
- run 3 · **send** · 2.4s: "No deposit, Omar! It's cash or credit card, paid when the job's done. The tech sends the invoice while he wraps up."
  - checks (15): all pass

**Muse Spicy — 3/3 pass** · latency 2.9, 3.6, 3.3s
- run 1 · **send** · 2.9s: "Hi Omar, it's Lucy! No deposit — it's cash or credit card, paid when the job's done."
  - checks (15): all pass
- run 2 · **send** · 3.6s: "Hi Omar! I'm Lucy. No deposit — it's cash or credit card, paid when the job's done. The tech sends the invoice while he wraps up."
  - checks (15): all pass
- run 3 · **send** · 3.3s: "Hi Omar, it's Lucy! No deposit — cash or credit card, paid when the job's done."
  - checks (15): all pass

### H14 (hard rerun) Baby + dogs smell
**Context:** Mid-conversation  
**Customer:** I have a 4 month old and two dogs. Is the smell a problem?

**Muse regular — 3/3 pass** · latency 4.5, 4.4, 4.8s
- run 1 · **send** · 4.5s: "Great question, Jess! Dogs are fine to be home for the whole job. We don't spray with an infant in the home, so your 4-month-old would need to be out during the visit. We use professional fume extraction and keep the door closed."
  - checks (17): all pass
- run 2 · **send** · 4.4s: "Great question, Jess! Dogs are fine to be home for the whole job.

We don't spray with an infant in the home, so your 4-month-old would need to be out for that part. We use professional fume extraction, keep the bath fan on and the door closed."
  - checks (17): all pass
- run 3 · **send** · 4.8s: "Great question, Jess! We don't spray with an infant in the home, so your little one would need to be out during the visit. Your dogs are totally fine to be home - we use professional fume extraction and keep the door closed."
  - checks (17): all pass

**Muse Spicy — 3/3 pass** · latency 4.7, 5.0, 6.3s
- run 1 · **send** · 4.7s: "Great question! Dogs are fine to be home for the whole job.

We don't spray with an infant in the home, so your 4-month-old would need to be out during the visit. We use professional fume extraction, keep the bath fan on and door closed."
  - checks (17): all pass
- run 2 · **send** · 5.0s: "Great question, Jess! We don't spray with an infant in the home, so your 4-month-old would need to be out during the visit.

Your dogs are fine to be home the whole time. We use professional fume extraction out the window plus the bath fan and closed door, so there's generally no noticeable smell after about an hour."
  - checks (17): all pass
- run 3 · **send** · 6.3s: "Dogs are fine to be home for the whole job! We don't spray with an infant in the home, so your 4-month-old would need to be out during spraying. We vent fumes out the window and keep the door closed."
  - checks (17): all pass

### H15 (hard rerun) Almond toilet match (first touch)
**Context:** New lead, first touch  
**Customer:** Can you match my almond toilet?

**Muse regular — 3/3 pass** · latency 4.7, 6.1, 5.4s
- run 1 · **send** · 4.7s: "Hi Carol, it's Lucy! Yes, we can match almond from the Sherwin-Williams library. Almond counts as custom, so it's an $85 upcharge and about a one-week lead time. If you have the color code, just text me."
  - checks (16): all pass
- run 2 · **send** · 6.1s: "Yes Carol! We can match almond - it's a custom color from the Sherwin-Williams library. It's an $85 upcharge with about a one-week lead time. If you have the color code, just text me it!"
  - checks (16): all pass
- run 3 · **send** · 5.4s: "Yes, Carol! I'm Lucy. We can match almond - it's custom from the Sherwin-Williams library so it's an $85 upcharge and about a one-week lead time. We'd need the color code. Almond is noticeably darker than our standard Biscuit."
  - checks (16): all pass

**Muse Spicy — 3/3 pass** · latency 6.4, 5.1, 4.3s
- run 1 · **send** · 6.4s: "Yes, Carol! Almond is a custom color from the Sherwin-Williams library. It's an $85 upcharge with about a one-week lead time, and we'll need the color code to match your toilet."
  - checks (16): all pass
- run 2 · **send** · 5.1s: "Hi Carol, it's Lucy! Yes, we can match almond - it's custom from the Sherwin-Williams library. It's an $85 upcharge and about a one-week lead time. If you have the color code, just text me."
  - checks (16): all pass
- run 3 · **send** · 4.3s: "Yes Carol! We can match your almond toilet with a custom color. It's an $85 upcharge and about a one-week lead time. We just need the Sherwin-Williams color code."
  - checks (16): all pass
