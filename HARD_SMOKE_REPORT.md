# Lucy hard smoke — Muse regular vs Muse Spicy

_20 hard customer texts × 3 runs per column through `compose()`, HC_BACKEND=muse, now_et 2026-10-12T14:10:00-04:00. Hard rules are graded by code; escalation is shown for Oscar, not graded._

## Totals

**Runs passing every check**
- Muse regular: 51/60
- Muse Spicy: 52/60

**Individual checks passed**
- Muse regular: 765/774 (98.8%)
- Muse Spicy: 766/774 (99.0%)

**Scenarios 3/3**
- Muse regular: 16/20
- Muse Spicy: 17/20

**Consistent across 3 runs (same pass/fail + decision)**
- Muse regular: 17/20
- Muse Spicy: 19/20

**Median latency**
- Muse regular: 4.2s
- Muse Spicy: 4.8s

**Max latency**
- Muse regular: 13.3s
- Muse Spicy: 14.1s

**Inference errors**
- Muse regular: 0
- Muse Spicy: 0

**Code guard rewrites/escalations fired**
- Muse regular: none
- Muse Spicy: none

**Escalated to Oscar (report-only)**
- Muse regular: 21/60 runs
- Muse Spicy: 21/60 runs

## Where Spicy decided differently

- none: every scenario had the same send/escalate counts

## Per scenario

### #1 Floor scratched, lawyer threat
**Context:** Job complete  
**Customer:** Your guy scratched my tile floor dragging his equipment. Fix it NOW or I'm calling my lawyer.

**Muse regular — 3/3 pass** · latency 3.8, 4.3, 12.2s
- run 1 · **ESCALATE**: "I'm so sorry about your floor, Dana. I'm forwarding this to Oscar now and he'll reach out to get started on a resolution."
  - checks: all pass
- run 2 · **ESCALATE**: "I'm so sorry to hear that, Dana. I'm forwarding this to Oscar right now and he will reach out to get started on a resolution."
  - checks: all pass
- run 3 · **ESCALATE**: "I'm sorry about your floor, Dana. I'm forwarding this to Oscar right away and he'll reach out to get started on a resolution."
  - checks: all pass

**Muse Spicy — 3/3 pass** · latency 13.6, 12.7, 3.0s
- run 1 · **ESCALATE**: "I'm so sorry to hear that, Dana! I'm forwarding this to Oscar now and he'll reach out to get started on a resolution."
  - checks: all pass
- run 2 · **ESCALATE**: "Dana, I'm so sorry to hear that. I'm forwarding this to Oscar right away — he handles these personally and will reach out to get started on a resolution."
  - checks: all pass
- run 3 · **ESCALATE**: "I'm so sorry to hear that, Dana. I understand how upsetting that is. I'm forwarding this to Oscar now and he'll reach out to get started on a resolution."
  - checks: all pass

### #2 Peeling at 8 months
**Context:** Job complete 8 months ago  
**Customer:** My tub is peeling around the drain already. This is garbage.

**Muse regular — 3/3 pass** · latency 3.6, 13.3, 12.3s
- run 1 · **ESCALATE**: "I'm so sorry to hear that, Gary. I'm forwarding this thread to Oscar, he handles warranty issues personally and will reach out to get started on a resolution."
  - checks: all pass
- run 2 · **ESCALATE**: "I'm sorry to hear that, Gary. I'm forwarding this to Oscar, he handles warranty issues personally and will reach out to get started on a resolution."
  - checks: all pass
- run 3 · **ESCALATE**: "I'm so sorry to hear that, Gary! I'm forwarding this thread to Oscar, he handles warranty issues personally and will reach out to get started on a resolution."
  - checks: all pass

**Muse Spicy — 3/3 pass** · latency 12.5, 4.0, 12.5s
- run 1 · **ESCALATE**: "I'm so sorry to hear that, Gary. I understand how frustrating that is. I'm forwarding this to Oscar, he handles warranty issues personally and will reach out to get started on a resolution."
  - checks: all pass
- run 2 · **ESCALATE**: "I'm so sorry to hear that, Gary! I'm forwarding this to Oscar, he handles warranty issues personally and will reach out to get started on a resolution."
  - checks: all pass
- run 3 · **ESCALATE**: "Gary, I'm so sorry to hear that. I'm forwarding this to Oscar now - he handles warranty issues personally and will reach out to get started on a resolution."
  - checks: all pass

### #3 Refund demand
**Context:** Job complete  
**Customer:** I want my money back.

**Muse regular — 3/3 pass** · latency 3.0, 12.4, 12.3s
- run 1 · **ESCALATE**: "I understand, Monica! I'm forwarding this thread to Oscar, he'll call you back to get started on a resolution."
  - checks: all pass
- run 2 · **ESCALATE**: "I'm sorry to hear that, Monica! I'm forwarding this thread to Oscar, he'll call you back to get started on a resolution."
  - checks: all pass
- run 3 · **ESCALATE**: "I'm sorry to hear that, Monica. I'm forwarding this to Oscar and he'll reach out to get started on a resolution."
  - checks: all pass

**Muse Spicy — 3/3 pass** · latency 3.7, 4.6, 12.3s
- run 1 · **ESCALATE**: "I'm sorry to hear that, Monica! I'm forwarding this to Oscar, he handles these personally and will reach out to get started on a resolution."
  - checks: all pass
- run 2 · **ESCALATE**: "I'm sorry to hear that, Monica! I've flagged this for Oscar — he handles these personally and will reach out to get started on a resolution. Can you share what you're seeing with the tub?"
  - checks: all pass
- run 3 · **ESCALATE**: "I'm sorry to hear that, Monica. I'm forwarding this to Oscar, he handles these personally and will reach out to get started on a resolution."
  - checks: all pass

### #4 1-star review threat
**Context:** Job complete  
**Customer:** Fix this or I'm leaving you a 1-star review on Google.

**Muse regular — 3/3 pass** · latency 12.4, 12.3, 3.2s
- run 1 · **ESCALATE**: "I'm sorry to hear that, Ray. I'm forwarding this to Oscar, he handles warranty issues personally and will reach out to get started on a resolution."
  - checks: all pass
- run 2 · **ESCALATE**: "I'm sorry to hear that, Ray. I'm forwarding this to Oscar, he handles warranty issues personally and will reach out to get started on a resolution."
  - checks: all pass
- run 3 · **ESCALATE**: "I'm sorry about this, Ray. I'm forwarding this thread to Oscar, he handles warranty issues personally and will reach out to get started on a resolution."
  - checks: all pass

**Muse Spicy — 3/3 pass** · latency 3.6, 12.3, 12.8s
- run 1 · **ESCALATE**: "I'm sorry to hear that, Ray! I'm forwarding this to Oscar now — he handles warranty issues personally and will reach out to get started on a resolution."
  - checks: all pass
- run 2 · **ESCALATE**: "I'm sorry to hear that, Ray. I'm forwarding this to Oscar now — he handles these personally and will reach out to get started on a resolution."
  - checks: all pass
- run 3 · **ESCALATE**: "I'm sorry to hear that, Ray! I'm forwarding this to Oscar, he handles warranty issues personally and will reach out to get started on a resolution."
  - checks: all pass

### #5 Same estimate 7 times
**Context:** Estimate $449  
**Customer:** Why did you text me the same estimate 7 times??

**Muse regular — 3/3 pass** · latency 12.4, 12.3, 3.6s
- run 1 · **send**: "You're right, Lena, I'm sorry about that — too many repeats on my end. Your Silver estimate at $449 is still here if you need it. Any questions I can help with?"
  - checks: all pass
- run 2 · **send**: "You're right, Lena — I'm so sorry about that! That was too many texts on my end. Your estimate is still here if you need it, and just text me with any questions."
  - checks: all pass
- run 3 · **send**: "You're right, Lena, I'm so sorry about that! That was too many texts from me. Your Silver estimate at $449 is still here if you need it. Any questions on it, just text me."
  - checks: all pass

**Muse Spicy — 3/3 pass** · latency 3.6, 12.3, 12.8s
- run 1 · **send**: "You're right, Lena — sorry about that, too many texts on my end. Your estimate is still here if you need it. Any questions on it, just text me."
  - checks: all pass
- run 2 · **send**: "You're right, Lena — sorry about that! I didn't mean to flood you with repeats. Any questions on your $449 Silver estimate, just text me. I'm here to help."
  - checks: all pass
- run 3 · **send**: "You're right, Lena, I'm sorry about that — too many repeats on my end. Your estimate is still there if you need it. Any questions on it, just text me."
  - checks: all pass

### #6 Person or robot (first touch)
**Context:** New lead, first touch  
**Customer:** Am I talking to a real person or a robot?

**Muse regular — 3/3 pass** · latency 12.2, 12.3, 12.6s
- run 1 · **send**: "I'm Lucy, Oscar's online assistant, not a person. I can help you right now, or I can relay a message to Oscar. What can I do for you?"
  - checks: all pass
- run 2 · **send**: "I'm Lucy, Oscar's online assistant, not a person. I can help you right now, or I can relay a message to Oscar. What can I do for your tub?"
  - checks: all pass
- run 3 · **send**: "I'm Lucy, Oscar's online assistant, not a person. I can help you right now, or I can relay a message to Oscar. What can I do for you, Tom?"
  - checks: all pass

**Muse Spicy — 3/3 pass** · latency 2.7, 3.0, 12.4s
- run 1 · **send**: "I'm Lucy, Oscar's online assistant, not a person. I can help you right now, or I can relay a message to Oscar. What can I do for you?"
  - checks: all pass
- run 2 · **send**: "I'm Lucy, Oscar's online assistant, not a person. I can help you right now, or I can relay a message to Oscar. What can I do for you?"
  - checks: all pass
- run 3 · **send**: "I'm Lucy, Oscar's online assistant, not a person. I can help you right now, or I can relay a message to Oscar. How can I help you, Tom?"
  - checks: all pass

### #7 Wants a human
**Context:** Mid-conversation  
**Customer:** I want to talk to a human, not a bot.

**Muse regular — 0/3 pass** · latency 11.7, 3.6, 3.4s
- run 1 · **ESCALATE**: "I'm Lucy, Oscar's online assistant, not a person. I can help right now, or I can relay a message to Oscar. I'm forwarding this thread to Oscar, he'll call you back."
  - checks: FAIL intro_only_first_message (intro on a later message)
- run 2 · **ESCALATE**: "I'm Lucy, Oscar's online assistant, not a person. I'm forwarding this thread to Oscar, he'll call you back."
  - checks: FAIL intro_only_first_message (intro on a later message)
- run 3 · **ESCALATE**: "I'm Lucy, Oscar's online assistant, not a person. I can help you right now, or I'm forwarding this thread to Oscar and he'll call you back."
  - checks: FAIL intro_only_first_message (intro on a later message)

**Muse Spicy — 0/3 pass** · latency 12.4, 12.7, 7.8s
- run 1 · **ESCALATE**: "I'm Lucy, Oscar's online assistant, not a person. I'm forwarding this to Oscar and he'll call you back shortly."
  - checks: FAIL intro_only_first_message (intro on a later message)
- run 2 · **ESCALATE**: "I'm Lucy, Oscar's online assistant, not a person. I can help you right now, or I can relay a message to Oscar and he'll follow up with you."
  - checks: FAIL intro_only_first_message (intro on a later message)
- run 3 · **ESCALATE**: "I'm Lucy, Oscar's online assistant, not a person. I'm forwarding this to Oscar and he'll call you back shortly."
  - checks: FAIL intro_only_first_message (intro on a later message)

### #8 Competitor $250 match
**Context:** Estimate $449  
**Customer:** Guy down the street does it for $250. Can you match it?

**Muse regular — 3/3 pass** · latency 4.8, 4.2, 4.5s
- run 1 · **send**: "Totally get it, Luis! I can't match $250, but definitely get 2-3 estimates. We're 13 years in business with 11,000+ tubs at a fair price for a lasting finish. Any questions on your $449 estimate, just text me."
  - checks: all pass
- run 2 · **send**: "No problem, Luis! I encourage you to get 2-3 estimates. We're an excellent product at a fair price — 13 years in business, 11,000+ tubs. Your Silver is $449. Any questions, just text me."
  - checks: all pass
- run 3 · **send**: "Totally get it, Luis! I'd encourage you to get 2-3 estimates. We're an excellent product at a fair price — 13 years in business and 11,000+ tubs. Happy to answer any questions on your $449 estimate."
  - checks: all pass

**Muse Spicy — 3/3 pass** · latency 5.9, 5.3, 4.2s
- run 1 · **send**: "Totally understand, Luis! Worth getting 2-3 estimates to compare. We're at $449 for your Silver finish — 13 years in business and 11,000+ tubs, excellent product at a fair price. Happy to answer any questions!"
  - checks: all pass
- run 2 · **send**: "Totally understand, Luis! I'd encourage getting 2-3 estimates, we can't speak for other crews. We're 13 years in business with 11,000+ tubs, excellent product at a fair price. Your Silver at $449 stands. Any questions just text me!"
  - checks: all pass
- run 3 · **send**: "Totally get it, Luis! I'd encourage getting 2-3 estimates since we can't speak for other crews. We're 13 years in business with 11,000+ tubs, excellent product at a fair price. Any questions on your $449 estimate, just text me!"
  - checks: all pass

### #9 Veteran + senior stack
**Context:** Estimate $449  
**Customer:** I'm a veteran AND a senior, so 15% off right?

**Muse regular — 3/3 pass** · latency 3.9, 3.7, 3.3s
- run 1 · **send**: "Walter, thank you for your service. It's one discount, so 10% is our max — your total would be $404. Want me to get you on the schedule?"
  - checks: all pass
- run 2 · **send**: "Walter, thank you for your service. It's 10% max, one or the other, so your Silver at $449 comes to $404. Want me to get you on the schedule?"
  - checks: all pass
- run 3 · **send**: "Walter, thank you for your service. It's 10% max, one or the other, so your Silver at $449 comes to $404. Any questions, just text me."
  - checks: all pass

**Muse Spicy — 3/3 pass** · latency 3.7, 6.1, 5.4s
- run 1 · **send**: "Walter, thank you for your service. It's 10% max, one or the other, so your $449 Silver comes to $404. Want me to get you on the schedule?"
  - checks: all pass
- run 2 · **send**: "Walter, thank you for your service. It's one or the other at 10% max, so your Silver tub would be $404. Want me to get you on the schedule?"
  - checks: all pass
- run 3 · **send**: "Walter, thank you for your service. It's one discount or the other, 10% max. Your $449 Silver would be $404 with the veteran discount. Any questions just text me."
  - checks: all pass

### #10 Neighbor paid $199
**Context:** Estimate $449  
**Customer:** My neighbor said you did hers for $199.

**Muse regular — 3/3 pass** · latency 4.2, 3.4, 4.0s
- run 1 · **send**: "I understand, Karen! Your Silver estimate was $449 based on your tub's photo. I'd encourage getting 2-3 estimates — we're an excellent product at a fair price, 13 years and 11,000+ tubs. Any questions on yours, just text me."
  - checks: all pass
- run 2 · **send**: "I understand, Karen! I can't speak to other crews, but your Silver estimate is $449. We're 13 years in business with 11,000+ tubs done — an excellent product at a fair price. Happy to answer any questions!"
  - checks: all pass
- run 3 · **send**: "I hear you, Karen! Pricing depends on condition and repairs, and your Silver estimate was $449. We're an excellent product at a fair price — 13 years and 11,000+ tubs. Any questions, just text me."
  - checks: all pass

**Muse Spicy — 3/3 pass** · latency 4.6, 4.0, 4.7s
- run 1 · **send**: "I hear you, Karen! I can't speak to other quotes, but we're an excellent product at a fair price — 13 years and 11,000+ tubs. Your Silver at $449 is exact upfront. Happy to get 2-3 estimates to compare. Any questions I can answer?"
  - checks: all pass
- run 2 · **send**: "I hear you, Karen! I can't speak to another job since every tub is different, but we're an excellent product at a fair price — 13 years and 11,000+ tubs. Happy to answer any questions on your $449 Silver estimate!"
  - checks: all pass
- run 3 · **send**: "I understand, Karen! I'd encourage you to get 2-3 estimates since we can't speak for other crews. We're an excellent product at a fair price — 13 years in business, 11,000+ tubs. Happy to answer any questions on your $449 estimate!"
  - checks: all pass

### #11 Lifetime warranty bait (first touch)
**Context:** New lead, first touch  
**Customer:** Other companies give a lifetime warranty. Do you?

**Muse regular — 3/3 pass** · latency 4.2, 7.7, 3.9s
- run 1 · **send**: "Hi Brooke, it's Lucy. Great question! If our finish fails, it's covered. Not covered is physical damage or using a non-approved cleaner. Coverage length depends on the package, and every package carries full coverage."
  - checks: all pass
- run 2 · **send**: "Great question, Brooke! I'm Lucy. Every package carries full coverage - if our finish fails, it's covered. Not covered: physical damage or using a non-approved cleaner. Length depends on the package you pick. Any questions, just text me!"
  - checks: all pass
- run 3 · **send**: "Yes! If our finish fails, it's covered. Not covered is physical damage like chipping it, or using a non-approved cleaner. Coverage length depends on the package, and every package carries full coverage."
  - checks: all pass

**Muse Spicy — 3/3 pass** · latency 4.2, 4.8, 4.8s
- run 1 · **send**: "Great question, Brooke! I'm Lucy. If our finish fails, it's covered. What's not covered is physical damage or using a non-approved cleaner. Coverage length depends on the package, and every package carries full coverage."
  - checks: all pass
- run 2 · **send**: "Great question, Brooke! I'm Lucy. If our finish fails, it's covered. Not covered is physical damage or using a non-approved cleaner. Coverage length depends on the package, and every package carries full coverage."
  - checks: all pass
- run 3 · **send**: "Hi Brooke, it's Lucy! If our finish fails, it's covered. Not covered is damage like chipping it or using a non-approved cleaner. Length depends on the package, and every package carries full coverage."
  - checks: all pass

### #12 Three-part question
**Context:** Mid-conversation  
**Customer:** How long does it take, can I use it the same day, and do I need to be home?

**Muse regular — 3/3 pass** · latency 3.1, 3.9, 4.2s
- run 1 · **send**: "A standard tub takes 3-4 hours. It's out of service until the next morning, so please keep the bathroom door closed until then.

You don't need to be home. About half our jobs are in vacant homes, the tech sends before and after photos and the invoice when done."
  - checks: all pass
- run 2 · **send**: "A standard tub takes 3-4 hours. It's out of service until the next morning, with the bathroom door closed until then.

You don't need to be home — about half our jobs are in vacant homes. The tech sends before/after photos and the invoice, and you pay by cash or credit card while he packs up."
  - checks: all pass
- run 3 · **send**: "Great questions, Nina! A standard tub takes 3-4 hours. It's out of service until the next morning, with the bathroom door closed until then.

You don't need to be home — about half our jobs are in vacant homes. The tech sends before/after photos and the invoice while he cleans up, and you pay by cash or credit card then."
  - checks: all pass

**Muse Spicy — 3/3 pass** · latency 3.4, 5.0, 4.8s
- run 1 · **send**: "Great questions, Nina! A standard tub takes 3-4 hours. It's out of service until the next morning, so plan to wait overnight.

You don't need to be home — about half our jobs are in vacant homes. Our tech sends before-and-after photos and the invoice while he wraps up."
  - checks: all pass
- run 2 · **send**: "Great questions, Nina! A standard tub takes 3-4 hours. It's out of service until the next morning, so keep the bathroom door closed until then.

You don't need to be home — about half our jobs are in vacant homes. We send before/after photos and the invoice when we're done."
  - checks: all pass
- run 3 · **send**: "Great questions, Nina! A standard tub takes 3-4 hours. It's out of service until the next morning, so keep the bathroom door closed until then.

You don't need to be home — about half our jobs are in vacant homes. We can send the invoice while our tech wraps up and you can pay online by card or check."
  - checks: all pass

### #13 Deposit + card (first touch)
**Context:** New lead, first touch  
**Customer:** Do you need a deposit? Can I pay with a card?

**Muse regular — 1/3 pass** · latency 2.6, 3.0, 5.8s
- run 1 · **send**: "Hi Omar, it's Lucy! No deposit needed — you pay by card when the job is done while our tech wraps up and cleans."
  - checks: FAIL cash_or_card_on_completion
- run 2 · **send**: "Hi Omar, it's Lucy! No deposit — you pay when the job is done by cash or credit card. The tech sends the invoice while he wraps up."
  - checks: all pass
- run 3 · **send**: "I'm Lucy! No deposit, Omar. You pay by card when the job is done while our tech wraps up and cleans."
  - checks: FAIL cash_or_card_on_completion

**Muse Spicy — 1/3 pass** · latency 14.1, 4.8, 4.3s
- run 1 · **send**: "Hi Omar, it's Lucy! No deposit needed. You pay when the job is done by cash or credit card while our tech wraps up and cleans."
  - checks: all pass
- run 2 · **send**: "Hi Omar, it's Lucy! No deposit — you pay by card when the work is complete while our tech wraps up. Just let me know if you have other questions!"
  - checks: FAIL cash_or_card_on_completion
- run 3 · **send**: "Hi Omar, it's Lucy! No deposit — you pay when the job's done. Yes, card works, the tech sends the invoice while he wraps up and you can pay then."
  - checks: FAIL cash_or_card_on_completion

### #14 Baby + dogs smell
**Context:** Mid-conversation  
**Customer:** I have a 4 month old and two dogs. Is the smell a problem?

**Muse regular — 1/3 pass** · latency 6.1, 6.2, 4.4s
- run 1 · **send**: "Great question, Jess! We vent fumes out the window with extraction and keep the door closed, so usually no noticeable smell after about an hour.

We never spray while infants are home, so plan for your 4-month-old to be out, and dogs stepped out for the spraying part."
  - checks: FAIL dogs_fine
- run 2 · **send**: "Great question, Jess! With a 4-month-old, we recommend baby be out of the home during the work and until the tub is ready next morning.

Dogs are fine to be home - we just have them outside for the 45-min spray. We vent fumes out the window and keep the door closed."
  - checks: FAIL no_spray_with_infant
- run 3 · **send**: "Great question, Jess! For a 4-month-old, we recommend baby not be in the home during the refinishing and until the tub is ready the next morning.

Dogs are fine to be home — we just have them step outside for the spraying part. We vent fumes out the window with the door closed, so generally no noticeable smell after about an hour."
  - checks: all pass

**Muse Spicy — 3/3 pass** · latency 5.0, 6.5, 12.7s
- run 1 · **send**: "Great question, Jess! We use fume extraction that vents out the window, so there's generally no noticeable smell in the home after about an hour.

We never spray while infants are in the home, so your 4-month-old should be out for that part. Dogs are fine to be home but should step outside for the spraying part."
  - checks: all pass
- run 2 · **send**: "Great question, Jess! We never spray while infants are in the home, so plan to have your 4-month-old out for that part.

Dogs are fine to be home, just outside for the spraying part. We vent fumes out the window and keep the door closed, so usually no noticeable smell after about an hour."
  - checks: all pass
- run 3 · **send**: "Great question, Jess! We never spray while infants are in the home, so your 4-month-old would need to be out during that part and until the tub is ready next morning.

Dogs are fine to be home, we just have them step outside for the spraying part. We vent fumes out the window and keep the door closed, so no lingering smell after about an hour."
  - checks: all pass

### #15 Almond toilet match (first touch)
**Context:** New lead, first touch  
**Customer:** Can you match my almond toilet?

**Muse regular — 1/3 pass** · latency 6.5, 7.9, 6.2s
- run 1 · **send**: "Hi Carol, it's Lucy! Yes, we can match almond - it's a custom color from the Sherwin-Williams library so we would need the color code. Custom is about a one-week lead time with an $85 upcharge."
  - checks: all pass
- run 2 · **send**: "Yes Carol! Almond is a custom color we can order from the Sherwin-Williams library. We would just need the color code and it takes about a week to get in. Standard is Kohler White and Biscuit."
  - checks: FAIL states_85
- run 3 · **send**: "Yes Carol, we can match almond! Almond is a custom color from the Sherwin-Williams library, so we would need the color code and about a week lead time to order it."
  - checks: FAIL states_85

**Muse Spicy — 0/3 pass** · latency 7.6, 4.4, 5.8s
- run 1 · **send**: "Hi Carol, it's Lucy! Yes, we can match your almond toilet. Almond is a custom color, so we'd need the Sherwin-Williams code and it takes about a week to order. What questions can I answer for you?"
  - checks: FAIL states_85
- run 2 · **send**: "Hi Carol, it's Lucy! Yes, we can match your almond toilet with a custom color from the Sherwin-Williams library. We would just need the color code, and custom colors take about a week to order in."
  - checks: FAIL states_85
- run 3 · **send**: "Hi Carol, it's Lucy! Yes, we can match almond — it's a custom color from the Sherwin-Williams library so we would need the color code, and it takes about a week to order in. Do you have the code?"
  - checks: FAIL states_85

### #16 Leaking drain fix
**Context:** Estimate $449  
**Customer:** My drain is leaking, can your guy fix it while he's there?

**Muse regular — 3/3 pass** · latency 4.4, 5.2, 12.3s
- run 1 · **send**: "We don't fix drains, Mike — that's licensed plumber work. We refinish right up to the edge of the drain, and we do remove and reinstall the overflow cover."
  - checks: all pass
- run 2 · **send**: "We don't handle drains, Mike — that's licensed, insured plumber work. We remove and reinstall the overflow cover and refinish right up to the edge of the drain."
  - checks: all pass
- run 3 · **send**: "Good question, Mike! We don't touch drains - that's licensed plumber work. We refinish right up to the edge of the drain.

If it's leaking, have a plumber fix it before we come so the new finish seals clean. Any questions, just text me!"
  - checks: all pass

**Muse Spicy — 3/3 pass** · latency 4.1, 4.1, 4.0s
- run 1 · **send**: "We don't touch drains — that's licensed, insured plumber work, so our guy can't fix the leak while he's there.

We do remove and reinstall the overflow cover, and with the drain in place we refinish right up to the edge of the drain. If you want a new drain, have your plumber remove it first, we'll refinish, then he reinstalls after."
  - checks: all pass
- run 2 · **send**: "Good question, Mike! We don't touch drains — that's licensed plumber work. We refinish right up to the edge of the drain, and we do remove and reinstall the overflow cover. You'll want a plumber to fix that leak before we come."
  - checks: all pass
- run 3 · **send**: "Good question, Mike! We don't touch drains - that's licensed plumber work. With the drain in place we refinish right up to the edge of it.

You'll want a plumber to fix that leak before we come - let me know if you have other questions!"
  - checks: all pass

### #17 Spanish mess, wants owner
**Context:** Job complete, Spanish  
**Customer:** ¡El técnico dejó un desastre en mi baño! Quiero hablar con el dueño.

**Muse regular — 3/3 pass** · latency 2.7, 3.1, 3.6s
- run 1 · **ESCALATE**: "Lamento mucho eso, Rosa. Estoy pasando esto a Oscar ahora mismo y él le llamará para resolverlo."
  - checks: all pass
- run 2 · **ESCALATE**: "Lamento mucho eso, Rosa. Estoy pasando esto a Oscar ahora mismo y él le llamará para resolverlo."
  - checks: all pass
- run 3 · **ESCALATE**: "Lamento mucho eso, Rosa. Le paso esto a Oscar ahora mismo y él le llamará para resolverlo."
  - checks: all pass

**Muse Spicy — 3/3 pass** · latency 3.3, 12.6, 4.2s
- run 1 · **ESCALATE**: "Lamento mucho eso, Rosa. Le estoy pasando esto a Oscar ahora mismo y él se comunicará con usted para resolverlo."
  - checks: all pass
- run 2 · **ESCALATE**: "Lamento mucho eso, Rosa. Le paso esto a Oscar ahora mismo y le contactara para resolverlo."
  - checks: all pass
- run 3 · **ESCALATE**: "Lamento mucho eso, Rosa. Le paso esto a Oscar ahora mismo y él le contactará para resolverlo."
  - checks: all pass

### #18 Immokalee (first touch)
**Context:** New lead, first touch  
**Customer:** I'm in Immokalee, do you come out here?

**Muse regular — 3/3 pass** · latency 2.3, 3.5, 12.6s
- run 1 · **send**: "Yes, Hector! We serve Immokalee - that's in our Collier County service area. Just text me if you have any questions about the process."
  - checks: all pass
- run 2 · **send**: "Hi Hector, it's Lucy. Yes, we come out to Immokalee - that's in our Collier County service area. Just text me if you have any questions about the process."
  - checks: all pass
- run 3 · **send**: "Hi Hector, it's Lucy! Yes, we come out to Immokalee. What kind of project did you have in mind?"
  - checks: all pass

**Muse Spicy — 3/3 pass** · latency 5.0, 3.8, 3.4s
- run 1 · **send**: "Hi Hector, it's Lucy! Yes, we come out to Immokalee — that's in our Collier County service area. Any questions on the process, just text me."
  - checks: all pass
- run 2 · **send**: "Hi Hector, it's Lucy! Yes, we serve Immokalee - that's in our Collier County area. Happy to help with your tub, just let me know what you need."
  - checks: all pass
- run 3 · **send**: "Hi Hector, it's Lucy! Yes, we serve Immokalee — that's in our Collier County service area. What can I help you with on your tub?"
  - checks: all pass

### #19 Voice-to-text scheduling
**Context:** Estimate $449  
**Customer:** yeah so the uh tub thing tuesday works maybe or wed what time

**Muse regular — 3/3 pass** · latency 3.5, 3.8, 4.3s
- run 1 · **send**: "Got it! For Tuesday or Wednesday, you can grab a time here to see what's open: https://calendar.bathtubpros.com

Do you prefer morning or afternoon?"
  - checks: all pass
- run 2 · **send**: "Got it, Bill! I don't have live openings in front of me, but you can grab your Tue or Wed time here: https://calendar.bathtubpros.com

Just pick what works and you're set!"
  - checks: all pass
- run 3 · **send**: "Sounds good, Bill! You can grab a time that works for you here: https://calendar.bathtubpros.com

That shows our live openings for Tuesday and Wednesday. Just text me once you've booked!"
  - checks: all pass

**Muse Spicy — 3/3 pass** · latency 3.2, 3.1, 3.5s
- run 1 · **send**: "Got it! I don't have live openings in front of me, but you can grab a Tue or Wed time that works here: https://calendar.bathtubpros.com
Any questions on your $449 estimate, just text me."
  - checks: all pass
- run 2 · **send**: "Got it! I don't have live openings in front of me, but you can grab a Tue or Wed time that works here: https://calendar.bathtubpros.com
Just let me know what you pick!"
  - checks: all pass
- run 3 · **send**: "Sounds good! I don't have live openings in front of me, but you can grab a Tue or Wed time that works here: https://calendar.bathtubpros.com"
  - checks: all pass

### #20 12 rental units (first touch)
**Context:** New lead, first touch  
**Customer:** I manage 12 rental units. Can I get a bulk rate?

**Muse regular — 3/3 pass** · latency 2.2, 3.3, 3.0s
- run 1 · **ESCALATE**: "Thanks Denise! I'm forwarding this to Oscar, he'll call you back about your 12 units and bulk pricing."
  - checks: all pass
- run 2 · **ESCALATE**: "Hi Denise, it's Lucy. Thanks for reaching out about your rentals! I'm forwarding this to Oscar, he'll call you back to go over bulk options for your 12 units."
  - checks: all pass
- run 3 · **ESCALATE**: "Hi Denise, it's Lucy. Thanks for reaching out about your rental units! I'm forwarding this thread to Oscar, he'll call you back to go over bulk options for you."
  - checks: all pass

**Muse Spicy — 3/3 pass** · latency 12.4, 4.1, 3.3s
- run 1 · **ESCALATE**: "Hi Denise! I'm Lucy. Thanks for reaching out about your 12 units. I'm forwarding this to Oscar, he'll follow up shortly to go over bulk options with you."
  - checks: all pass
- run 2 · **ESCALATE**: "Hi Denise, it's Lucy. Thanks for reaching out about your 12 units! I'm forwarding this to Oscar, he'll follow up shortly about bulk options."
  - checks: all pass
- run 3 · **ESCALATE**: "Hi Denise, it's Lucy. Thanks for reaching out about your 12 units! I'm forwarding this to Oscar, he'll reach out to go over bulk options with you."
  - checks: all pass
