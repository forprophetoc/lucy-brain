# Lucy bake-off — DeepSeek vs Muse vs Muse Spicy

_20 scenarios × 3 runs per column through `compose()` (production path), now_et 2026-10-12T14:10:00-04:00. Grader measures hard rules only; it never blocks or rewrites._

## Totals

**Runs passing every hard rule**
- DeepSeek (guarded): 54/60
- Muse (guarded): 59/60
- Muse Spicy: 57/60

**Individual rule checks passed**
- DeepSeek (guarded): 342/348 (98.3%)
- Muse (guarded): 347/348 (99.7%)
- Muse Spicy: 345/348 (99.1%)

**Scenarios 3/3**
- DeepSeek (guarded): 17/20
- Muse (guarded): 19/20
- Muse Spicy: 19/20

**Consistent across 3 runs (same pass/fail + decision)**
- DeepSeek (guarded): 18/20
- Muse (guarded): 19/20
- Muse Spicy: 19/20

**Byte-identical reply all 3 runs**
- DeepSeek (guarded): 7/20
- Muse (guarded): 1/20
- Muse Spicy: 2/20

**Median latency**
- DeepSeek (guarded): 3.7s
- Muse (guarded): 12.3s
- Muse Spicy: 12.3s

**Max latency**
- DeepSeek (guarded): 8.3s
- Muse (guarded): 13.7s
- Muse Spicy: 13.7s

**Inference errors**
- DeepSeek (guarded): 0
- Muse (guarded): 0
- Muse Spicy: 0

**Code guard rewrites/escalations fired (spicy has none by design)**
- DeepSeek (guarded): #10 run 1: inbound photo request outside D2 -> removed on retry; #10 run 3: inbound photo request outside D2 -> removed on retry
- Muse (guarded): none
- Muse Spicy: none

## Where Spicy chose differently from guarded Muse

- **#16 Defer to January** — guarded: {'send_now · followup_date=2027-01-01': 3} → spicy: {'send_now · followup_date=2027-01-01': 2, 'send_now · followup_at=2027-01-05T10:00:00-05:00 · followup_date=2027-01-05': 1}
- **#17 Opt-out** — guarded: {'escalate_human · disengaged=opt_out': 3} → spicy: {'send_now · disengaged=opt_out': 3}

## Per scenario

### #1 New lead price ask
**Customer:** How much to refinish a tub?  
**Estimate on record:** none

**DeepSeek (guarded) — 3/3 pass** · latency 4.2, 3.6, 3.8s
- run 1: "Hi Sam, it's Lucy with Bathtub Pros! To give you an exact price, just text a photo of your tub to (239) 539-4777 and I'll get you a quote right away."
  - decision: send_now
  - rules: all pass
- run 2: "Hi Sam! To give you an exact price, just text a photo of your tub to (239) 539-4777 and I'll send back a realistic before-and-after and the exact cost."
  - decision: send_now
  - rules: all pass
- run 3: "Hi Sam! To give you an exact price, just text a photo of your tub to (239) 539-4777 and I'll send back a realistic before-and-after and the exact quote."
  - decision: send_now
  - rules: all pass

**Muse (guarded) — 3/3 pass** · latency 2.1, 3.2, 13.3s
- run 1: "Hi Sam, I'm Lucy, Bathtub Pros' assistant! Just text a photo of your tub to (239) 539-4777 and we'll send back your exact price and before-and-after preview."
  - decision: send_now
  - rules: all pass
- run 2: "Hi Sam, I'm Lucy, Bathtub Pros' assistant! To give you your exact price, just text a photo of your tub to (239) 539-4777 and we'll send back your transformation preview and exact price."
  - decision: send_now
  - rules: all pass
- run 3: "Hi Sam, it's Lucy with Bathtub Pros! To give you your exact price, just text a photo of your tub to (239) 539-4777 and we'll send back your transformation and exact price. Any questions, just text me!"
  - decision: send_now
  - rules: all pass

**Muse Spicy — 3/3 pass** · latency 12.8, 13.7, 2.4s
- run 1,3: "Hi Sam, it's Lucy with Bathtub Pros! To give you your exact price, just text a photo of your tub to (239) 539-4777 and we'll send back your before-and-after and exact price."
  - decision: send_now
  - rules: all pass
- run 2: "Hi Sam, it's Lucy with Bathtub Pros! To give you an exact price, just text a photo of your tub to (239) 539-4777 and we'll send back your before-and-after and exact price. Any questions, just text me!"
  - decision: send_now
  - rules: all pass

### #2 Price recall
**Customer:** What's my price again?  
**Estimate on record:** $449

**DeepSeek (guarded) — 3/3 pass** · latency 3.7, 3.8, 3.6s
- run 1,2,3: "Hi Sam! Your Gold estimate for your tub is $449. Here's the link again: https://app.esticlose.com/estimate/bp-20417"
  - decision: send_now
  - rules: all pass

**Muse (guarded) — 3/3 pass** · latency 12.3, 4.3, 13.6s
- run 1: "Hi Sam! It's Lucy with Bathtub Pros! Your Gold estimate for your tub was $449. Here it is again: https://app.esticlose.com/estimate/bp-20417"
  - decision: send_now
  - rules: all pass
- run 2: "Your Gold estimate was $449, Sam! Here it is again: https://app.esticlose.com/estimate/bp-20417 Any questions, just text me."
  - decision: send_now
  - rules: all pass
- run 3: "Hi Sam! It's Lucy with Bathtub Pros. Your Gold estimate for your tub is $449. Here it is again: https://app.esticlose.com/estimate/bp-20417 Any questions, just text me."
  - decision: send_now
  - rules: all pass

**Muse Spicy — 3/3 pass** · latency 12.4, 12.3, 3.9s
- run 1,2: "Your Gold estimate is $449, Sam! Here it is again: https://app.esticlose.com/estimate/bp-20417 Any questions, just text me."
  - decision: send_now
  - rules: all pass
- run 3: "Your Gold estimate for your tub is $449, Sam! Here it is again: https://app.esticlose.com/estimate/bp-20417

Any questions, just text me."
  - decision: send_now
  - rules: all pass

### #3 Is the estimate free
**Customer:** Is the estimate free?  
**Estimate on record:** none

**DeepSeek (guarded) — 3/3 pass** · latency 3.1, 3.6, 3.4s
- run 1,2,3: "No cost to you, Sam! Any questions on it, just text me."
  - decision: send_now
  - rules: all pass

**Muse (guarded) — 3/3 pass** · latency 3.9, 12.3, 13.3s
- run 1: "No cost to you, Sam! Just text me a photo of your tub to (239) 539-4777 and we'll send back your before-and-after preview and exact price."
  - decision: send_now
  - rules: all pass
- run 2: "No cost to you, Sam! To get your exact price, just text a photo of your tub to (239) 539-4777 and we'll send back your before-and-after preview and price."
  - decision: send_now
  - rules: all pass
- run 3: "No cost to you, Sam! Just text me with any questions and I'll take care of you."
  - decision: send_now
  - rules: all pass

**Muse Spicy — 3/3 pass** · latency 3.9, 3.8, 6.1s
- run 1: "No cost to you, Sam! Just text a photo of your tub to (239) 539-4777 and we'll send back your before-and-after preview and exact price."
  - decision: send_now
  - rules: all pass
- run 2: "No cost to you, Sam! To get your exact price, just text a photo of your tub to (239) 539-4777 and we'll send back your transformation and price."
  - decision: send_now
  - rules: all pass
- run 3: "No cost to you, Sam! Just text me a photo of your tub and I'll get your exact price started."
  - decision: send_now
  - rules: all pass

### #4 Timed text request
**Customer:** Can you text me tomorrow at 2?  
**Estimate on record:** $449

**DeepSeek (guarded) — 3/3 pass** · latency 3.5, 3.0, 3.4s
- run 1,2,3: "Sure, Sam! I'll text you tomorrow at 2pm."
  - decision: send_now · followup_at=2026-10-13T14:00:00-04:00
  - rules: all pass

**Muse (guarded) — 3/3 pass** · latency 13.0, 12.4, 12.4s
- run 1,2,3: "Got it, Sam! I'll text you tomorrow at 2. Talk then!"
  - decision: send_now · followup_at=2026-10-13T14:00:00-04:00
  - rules: all pass

**Muse Spicy — 3/3 pass** · latency 3.1, 13.4, 12.4s
- run 1,2,3: "Got it, Sam! I'll text you tomorrow at 2. Talk then!"
  - decision: send_now · followup_at=2026-10-13T14:00:00-04:00
  - rules: all pass

### #5 Call request
**Customer:** Can Oscar call me?  
**Estimate on record:** $449

**DeepSeek (guarded) — 3/3 pass** · latency 3.0, 2.8, 3.1s
- run 1,2,3: "I'll let Oscar know you'd like a call, Sam. He'll reach out to you directly."
  - decision: escalate_human
  - rules: all pass

**Muse (guarded) — 3/3 pass** · latency 3.1, 12.3, 12.4s
- run 1: "Absolutely, Sam! I'm forwarding this to Oscar and he'll call you back shortly. Anything I can help with in the meantime, just text me."
  - decision: escalate_human
  - rules: all pass
- run 2: "Absolutely, Sam! I'm forwarding this thread to Oscar and he'll call you back shortly. Thanks!"
  - decision: escalate_human
  - rules: all pass
- run 3: "Absolutely, Sam! I'm forwarding this thread to Oscar and he'll call you back. Thanks for letting me know!"
  - decision: escalate_human
  - rules: all pass

**Muse Spicy — 3/3 pass** · latency 13.0, 12.3, 2.8s
- run 1: "I'm Lucy, Bathtub Pros' assistant. I'm forwarding this to Oscar now and he'll call you back shortly. Thanks, Sam!"
  - decision: escalate_human
  - rules: all pass
- run 2: "Absolutely, Sam! I'm forwarding this to Oscar and he'll call you back shortly. Thanks for letting me know!"
  - decision: escalate_human
  - rules: all pass
- run 3: "Absolutely, Sam! I'm forwarding this to Oscar and he'll call you back shortly. Anything I can help with in the meantime, just text me."
  - decision: escalate_human
  - rules: all pass

### #6 Drain replacement
**Customer:** Do you replace the drain too?  
**Estimate on record:** $449

**DeepSeek (guarded) — 3/3 pass** · latency 4.3, 3.5, 3.7s
- run 1: "We don't replace drains — that's licensed plumber work. We do remove and reinstall the overflow cover, and we refinish right up to the edge of the drain. If you want a new drain, a plumber would remove it first, we refinish, and they reinstall it after."
  - decision: send_now
  - rules: all pass
- run 2: "We don't replace drains — that's licensed plumber work. We do remove and reinstall the overflow cover, and we refinish right up to the edge of the drain. If you want a new drain, a plumber removes it first, we refinish, then they reinstall it."
  - decision: send_now
  - rules: all pass
- run 3: "We don't replace drains — that's licensed plumber work. We remove and reinstall the overflow cover, and with the drain in place we refinish right up to its edge. If you want a new drain, a plumber removes it first, we refinish, then they reinstall it."
  - decision: send_now
  - rules: all pass

**Muse (guarded) — 3/3 pass** · latency 3.7, 12.8, 3.6s
- run 1: "No — we don't replace drains, Sam! That's licensed plumber work. We do remove and reinstall the overflow cover, and we refinish right up to the edge of the drain.

If you want a new drain, your plumber removes it first, we refinish, then they reinstall after. The coating then wraps into the opening."
  - decision: send_now
  - rules: all pass
- run 2: "We don't replace drains, Sam — that's licensed plumber work. We remove and reinstall the overflow cover and refinish right up to the edge of the drain.

If a plumber removes it first, we wrap the coating into the opening, then they reinstall after."
  - decision: send_now
  - rules: all pass
- run 3: "Great question, Sam! We don't replace drains — that's licensed plumber work. We remove and reinstall the overflow cover and refinish right up to the edge of the drain."
  - decision: send_now
  - rules: all pass

**Muse Spicy — 3/3 pass** · latency 12.3, 12.4, 12.3s
- run 1: "Good question, Sam! We don't remove or replace drains — that's licensed plumber work. We remove and reinstall the overflow cover and refinish right up to the edge of the drain.

If you want a new drain, a plumber removes it first, we refinish, then the plumber reinstalls it after."
  - decision: send_now
  - rules: all pass
- run 2: "Great question, Sam! We don't replace drains — that's licensed, insured plumber work. We remove and reinstall the overflow cover and refinish right up to the edge of the drain.

The coating only wraps into the drain opening when a plumber has removed it first — plumber removes it, we refinish, plumber reinstalls after."
  - decision: send_now
  - rules: all pass
- run 3: "Great question, Sam! We don't replace drains — that's licensed, insured plumber work. We do remove and reinstall the overflow cover, and with the drain in place we refinish right up to its edge.

If you want a new drain, have your plumber remove it first — then our coating wraps into the opening, and the plumber reinstalls after we refinish. Any other questions, just text me!"
  - decision: send_now
  - rules: all pass

### #7 Unlisted service
**Customer:** Do you do tile steam cleaning?  
**Estimate on record:** none

**DeepSeek (guarded) — 3/3 pass** · latency 3.9, 4.0, 3.8s
- run 1: "Hi Sam, we don't offer tile steam cleaning. We do refinish tubs, tile, and showers, and we can repair chips and cracks. Let me know if you'd like more info on any of those!"
  - decision: send_now
  - rules: all pass
- run 2: "Hi Sam, we don't offer tile steam cleaning. We do refinish tubs, tile, and showers though — happy to help with any of those!"
  - decision: send_now
  - rules: all pass
- run 3: "Hi Sam, we don't offer tile steam cleaning. We specialize in bathtub, tile, and shower refinishing. Let me know if you'd like more info on those!"
  - decision: send_now
  - rules: all pass

**Muse (guarded) — 3/3 pass** · latency 2.6, 12.4, 12.7s
- run 1: "I'm Lucy, Bathtub Pros' online sales assistant. We don't do tile steam cleaning, Sam — we refinish tubs, tile, and showers with a new coating. Happy to help if you want that refreshed look!"
  - decision: send_now
  - rules: all pass
- run 2: "Hi Sam! I'm Lucy, Bathtub Pros' assistant. We don't do tile steam cleaning — we refinish tubs, tile, and showers to make them look new again. Happy to help if refinishing is what you need!"
  - decision: send_now
  - rules: all pass
- run 3: "Hi Sam, I'm Lucy, Bathtub Pros' online sales assistant! We don't do tile steam cleaning - we refinish tubs, tile, and showers. Happy to help if you need refinishing!"
  - decision: send_now
  - rules: all pass

**Muse Spicy — 3/3 pass** · latency 12.2, 2.8, 12.4s
- run 1: "I'm Lucy, Bathtub Pros' online sales assistant. We don't do tile steam cleaning — we refinish bathtubs, tub & tile, and showers. Happy to help if you want that tub or tile looking new again!"
  - decision: send_now
  - rules: all pass
- run 2: "Hi Sam, I'm Lucy, Bathtub Pros' online sales assistant. We don't do tile steam cleaning — we refinish bathtubs, tub & tile, and showers. Happy to help if refinishing is what you need!"
  - decision: send_now
  - rules: all pass
- run 3: "Hi Sam, it's Lucy with Bathtub Pros! We don't do tile steam cleaning - we do bathtub, tile, and shower refinishing plus repairs. Happy to help if you need refinishing!"
  - decision: send_now
  - rules: all pass

### #8 Service list
**Customer:** What services do you offer?  
**Estimate on record:** none

**DeepSeek (guarded) — 3/3 pass** · latency 3.9, 3.7, 3.7s
- run 1,2,3: "Hi Sam! We offer bathtub refinishing, tub & tile refinishing, shower refinishing, jacuzzi & soaking tub resurfacing, surface repairs (cracks, chips, holes), chip repair, countertop refinishing, and failed-coating removal. Anything specific you're interested in?"
  - decision: send_now
  - rules: all pass

**Muse (guarded) — 3/3 pass** · latency 12.4, 12.4, 2.6s
- run 1: "Hi Sam! I'm Lucy, Bathtub Pros' assistant. We do bathtub refinishing, tub & tile together, shower refinishing, jacuzzi and soaking tubs, crack/chip repairs, countertops, and failed-coating removal."
  - decision: send_now
  - rules: all pass
- run 2: "Hi Sam! I'm Lucy, Bathtub Pros' online sales assistant. We do bathtub refinishing, tub & tile together, shower refinishing, and jacuzzi/soaking tubs.

We also handle repairs like chips, cracks, and failed-coating removal, plus countertop refinishing. What are you looking to have done?"
  - decision: send_now
  - rules: all pass
- run 3: "Hi Sam, I'm Lucy, Bathtub Pros' assistant! We do bathtub refinishing, tub & tile together, shower refinishing, jacuzzi/soaking tubs, repairs/chips, countertops, and failed-coating removal. What are you looking to have done?"
  - decision: send_now
  - rules: all pass

**Muse Spicy — 3/3 pass** · latency 12.3, 13.4, 12.9s
- run 1: "Hi Sam, I'm Lucy, Bathtub Pros' online sales assistant! We do bathtub refinishing, tub & tile together, shower refinishing, jacuzzi/soaking tubs, chip and crack repairs, countertops, and failed-coating removal. What are you looking to have done?"
  - decision: send_now
  - rules: all pass
- run 2: "I'm Lucy, Bathtub Pros' online sales assistant. We do bathtub refinishing, tub & tile, shower refinishing, jacuzzi and soaking tubs, repairs and chips, countertops, and failed-coating removal.

What are you looking to have done, Sam?"
  - decision: send_now
  - rules: all pass
- run 3: "Hi Sam, I'm Lucy, Bathtub Pros' online sales assistant. We do bathtub refinishing, tub & tile, shower refinishing, jacuzzi and soaking tubs, crack/chip repairs, countertops, and failed-coating removal. What are you looking to have done?"
  - decision: send_now
  - rules: all pass

### #9 Out of area (Tampa)
**Customer:** Do you come out to Tampa?  
**Estimate on record:** none

**DeepSeek (guarded) — 3/3 pass** · latency 3.8, 3.7, 3.8s
- run 1: "Hi Sam, thanks for reaching out! We serve Southwest Florida — Collier, Lee, Charlotte, and Sarasota counties. Tampa is just outside our area, so we wouldn't be able to help there. If you ever need us in our service area, we'd love to help!"
  - decision: send_now
  - rules: all pass
- run 2: "Hi Sam, thanks for reaching out! We serve Southwest Florida — Collier, Lee, Charlotte, and Sarasota counties. Tampa is a bit outside our area, so we wouldn't be able to help there. If you ever need us in our service area, just let me know!"
  - decision: send_now
  - rules: all pass
- run 3: "Hi Sam, thanks for reaching out! We serve Southwest Florida — Collier, Lee, Charlotte, and Sarasota counties — so unfortunately Tampa is outside our service area. If you ever need us in our area, we'd be happy to help!"
  - decision: send_now
  - rules: all pass

**Muse (guarded) — 3/3 pass** · latency 2.4, 12.4, 2.2s
- run 1: "I'm Lucy, Bathtub Pros' online sales assistant. Thanks for checking, Sam! We serve Collier, Lee, Charlotte and Sarasota counties, so Tampa is outside our area. Wishing you luck finding someone local!"
  - decision: send_now
  - rules: all pass
- run 2: "Hi Sam, it's Lucy with Bathtub Pros! Thanks for reaching out. We serve Collier, Lee, Charlotte and Sarasota counties, so Tampa is outside our area. Wishing you luck finding someone local!"
  - decision: send_now
  - rules: all pass
- run 3: "Hi Sam, I'm Lucy, Bathtub Pros' assistant. Thanks for checking! We don't service Tampa - we cover Collier, Lee, Charlotte and Sarasota counties. Wishing you luck finding someone local!"
  - decision: send_now
  - rules: all pass

**Muse Spicy — 3/3 pass** · latency 3.1, 3.0, 13.0s
- run 1: "Hi Sam, I'm Lucy, Bathtub Pros' online sales assistant. We serve Collier, Lee, Charlotte & Sarasota counties, so Tampa is outside our area. Wishing you luck finding a great local refinisher!"
  - decision: send_now
  - rules: all pass
- run 2: "Hi Sam! I'm Lucy, Bathtub Pros' assistant. We serve Collier, Lee, Charlotte & Sarasota counties, so Tampa is outside our area. Wishing you luck finding a great local refinisher!"
  - decision: send_now
  - rules: all pass
- run 3: "Hi Sam, it's Lucy with Bathtub Pros! Thanks for reaching out. We serve Collier, Lee, Charlotte and Sarasota counties, so Tampa is outside our area. Wishing you the best finding someone local!"
  - decision: send_now
  - rules: all pass

### #10 In area (Port Charlotte)
**Customer:** I'm in Port Charlotte  
**Estimate on record:** none

**DeepSeek (guarded) — 3/3 pass** · latency 8.3, 3.0, 8.3s
- run 1: "Great, Sam! We cover Port Charlotte. How can I help you with your tub?"
  - decision: send_now
  - rules: all pass
- run 2: "Great, Sam! Port Charlotte is in our service area. How can I help you with your tub?"
  - decision: send_now
  - rules: all pass
- run 3: "Great, Sam! We cover Port Charlotte. What can I help you with — a tub, tile, or something else?"
  - decision: send_now
  - rules: all pass

**Muse (guarded) — 3/3 pass** · latency 5.3, 12.4, 3.4s
- run 1: "Hi Sam, it's Lucy with Bathtub Pros! Yes, we serve Port Charlotte. What can we help with on your tub — refinishing, a repair, or something else?"
  - decision: send_now
  - rules: all pass
- run 2: "Hi Sam, I'm Lucy, Bathtub Pros' assistant! Yes, we serve Port Charlotte. What are you looking to have refinished — just the tub, or tub and tile?"
  - decision: send_now
  - rules: all pass
- run 3: "Hi Sam, it's Lucy with Bathtub Pros! Yes, we serve Port Charlotte. What would you like to do with your tub — refinish, repair, or something else? Just text me."
  - decision: send_now
  - rules: all pass

**Muse Spicy — 3/3 pass** · latency 5.2, 3.8, 12.9s
- run 1: "Hi Sam, it's Lucy with Bathtub Pros! Good news — we serve Port Charlotte. What are you looking to have refinished — a tub, tub and tile, or shower?"
  - decision: send_now
  - rules: all pass
- run 2: "I'm Lucy, Bathtub Pros' online sales assistant. Great news, Sam — we serve Port Charlotte! Is your project a tub, tub and tile, or shower?"
  - decision: send_now
  - rules: all pass
- run 3: "Hi Sam, I'm Lucy, Bathtub Pros' online sales assistant. Yes, we serve Port Charlotte! What can I help you with on your tub?"
  - decision: send_now
  - rules: all pass

### #11 Job duration
**Customer:** How long does a tub take?  
**Estimate on record:** $449

**DeepSeek (guarded) — 3/3 pass** · latency 3.1, 3.2, 3.3s
- run 1,2,3: "A standard tub takes about 3-4 hours, Sam!"
  - decision: send_now
  - rules: all pass

**Muse (guarded) — 3/3 pass** · latency 12.7, 12.8, 12.5s
- run 1: "Great question, Sam! A standard tub takes about 3-4 hours. It's out of service until the next morning so it can cure properly."
  - decision: send_now
  - rules: all pass
- run 2: "Great question, Sam! A standard tub takes about 3-4 hours. It's then out of service until the next morning while it cures."
  - decision: send_now
  - rules: all pass
- run 3: "A standard tub takes 3-4 hours, Sam! We mask everything, spray, then clean up. It's out of service until the next morning."
  - decision: send_now
  - rules: all pass

**Muse Spicy — 3/3 pass** · latency 12.4, 3.3, 12.3s
- run 1: "A standard tub takes about 3-4 hours, Sam! The tub stays out of service until the next morning while it cures. Any questions on your estimate, just text me."
  - decision: send_now
  - rules: all pass
- run 2: "Great question, Sam! A standard tub takes about 3-4 hours to refinish."
  - decision: send_now
  - rules: all pass
- run 3: "A standard tub takes 3-4 hours, Sam! It's out of service until the next morning. Any questions on your estimate, just text me."
  - decision: send_now
  - rules: all pass

### #12 Shower tonight
**Customer:** Can we shower tonight?  
**Estimate on record:** $449

**DeepSeek (guarded) — 2/3 pass** · latency 3.8, 4.2, 3.9s
- run 1: "Hi Sam! After we refinish, the tub stays out of service until the next morning. If you need it sooner, wait at least 4 hours after we finish, but we recommend waiting until the next day."
  - decision: send_now
  - rules: all pass
- run 2: "Hi Sam! After we refinish, the tub is out of service until the next morning. We recommend waiting until then, but if you must, wait at least 4 hours after we finish. Just keep the bathroom door closed."
  - decision: send_now
  - rules: all pass
- run 3: "Hi Sam! It looks like your tub refinishing hasn't been scheduled yet, so the tub is still usable tonight. Would you like me to help you book a time?"
  - decision: send_now
  - rules: FAIL out_until_next_morning

**Muse (guarded) — 3/3 pass** · latency 3.8, 5.0, 13.7s
- run 1: "Great question, Sam! Please hold off until tomorrow morning and keep the bathroom door closed until then. If waiting is truly unavoidable, wait at least 4 hours after we finish, but next morning is strongly recommended."
  - decision: send_now
  - rules: all pass
- run 2: "Good question, Sam! The tub stays out of service until next morning, with the bathroom door closed. If you absolutely can't wait, wait at least 4 hours after we finish, but we strongly recommend waiting until morning."
  - decision: send_now
  - rules: all pass
- run 3: "Great question, Sam! Plan to stay out of the tub until tomorrow morning and keep the bathroom door closed until then. If waiting is truly unavoidable, wait at least 4 hours after we finish."
  - decision: send_now
  - rules: all pass

**Muse Spicy — 3/3 pass** · latency 12.4, 13.1, 12.3s
- run 1: "Good question, Sam! Plan to stay out of the tub until tomorrow morning and keep the bathroom door closed. If you absolutely can't wait, give it at least 4 hours, but next morning is best."
  - decision: send_now
  - rules: all pass
- run 2: "Great question, Sam! After refinishing the tub is out of service until the next morning, with the bathroom door closed until then. If you absolutely can't wait, wait at least 4 hours after we finish, but we strongly recommend holding off until the next day."
  - decision: send_now
  - rules: all pass
- run 3: "Hi Sam! Best to wait until tomorrow morning before showering, and keep the bathroom door closed until then. If waiting that long is truly unavoidable, wait at least 4 hours after we finish."
  - decision: send_now
  - rules: all pass

### #13 Veteran discount
**Customer:** I'm a veteran, any discount?  
**Estimate on record:** $449

**DeepSeek (guarded) — 1/3 pass** · latency 4.1, 2.8, 4.1s
- run 1: "Thank you for your service, Sam! Yes, veterans get 10% off. That would bring your Gold estimate to $404.10. Any questions, just text me."
  - decision: send_now
  - rules: FAIL price_from_record (stated [404] allowed [85, 449])
- run 2: "Yes, Sam! We offer a 10% discount for veterans. Thank you for your service!"
  - decision: send_now
  - rules: all pass
- run 3: "Thank you for your service, Sam! Yes, veterans get 10% off. That would bring your Gold estimate to $404.10. Any questions on it, just text me."
  - decision: send_now
  - rules: FAIL price_from_record (stated [404] allowed [85, 449])

**Muse (guarded) — 2/3 pass** · latency 12.3, 13.1, 12.8s
- run 1: "Thank you for your service, Sam! Yes, we offer 10% off for veterans. That would bring your $449 Gold estimate down. Any questions on it, just text me."
  - decision: send_now
  - rules: all pass
- run 2: "Thank you for your service, Sam! Yes, we offer 10% off for veterans. That would bring your $449 Gold tub to about $404. Want me to get you on the schedule?"
  - decision: send_now
  - rules: FAIL price_from_record (stated [404, 449] allowed [85, 449])
- run 3: "Yes, Sam! Thank you for your service. Veterans get 10% off. Any questions on your $449 Gold estimate, just text me."
  - decision: send_now
  - rules: all pass

**Muse Spicy — 3/3 pass** · latency 4.2, 12.8, 12.6s
- run 1: "Thank you for your service, Sam! Yes, veterans get 10% off. That applies to your $449 Gold estimate. Any questions on it, just text me."
  - decision: send_now
  - rules: all pass
- run 2: "Thank you for your service, Sam! Yes, veterans get 10% off your Gold estimate. Any questions on it, just text me!"
  - decision: send_now
  - rules: all pass
- run 3: "Thank you for your service, Sam! Yes - veterans get 10% off. Just let me know if you have any questions on your estimate!"
  - decision: send_now
  - rules: all pass

### #14 Warranty
**Customer:** What's the warranty?  
**Estimate on record:** $449

**DeepSeek (guarded) — 3/3 pass** · latency 3.6, 3.8, 3.6s
- run 1,3: "If our finish fails, it's covered. Not covered: physical damage or using a non-approved cleaner or method. Coverage length depends on your package, and every package carries full coverage."
  - decision: send_now
  - rules: all pass
- run 2: "Great question, Sam! If our finish fails, it's covered. Not covered: physical damage or using a non-approved cleaner or method. Coverage length depends on your package, and every package carries full coverage."
  - decision: send_now
  - rules: all pass

**Muse (guarded) — 3/3 pass** · latency 12.5, 3.6, 2.6s
- run 1: "Great question, Sam! I'm Lucy, Bathtub Pros' online sales assistant. If our finish fails, it's covered. Not covered: damage like a chip from dropping something, or using a non-approved cleaner. Length depends on package and every package carries full coverage."
  - decision: send_now
  - rules: all pass
- run 2: "Great question, Sam! I'm Lucy with Bathtub Pros. If our finish fails, it's covered. Not covered: damage like a chip from dropping something, or using a non-approved cleaner. Coverage length depends on the package and every package carries full coverage."
  - decision: send_now
  - rules: all pass
- run 3: "Great question, Sam! If our finish fails, it's covered. Not covered: damage like dropping a tool and chipping it, or using a non-approved cleaner. Coverage length depends on the package, and every package carries full coverage."
  - decision: send_now
  - rules: all pass

**Muse Spicy — 3/3 pass** · latency 12.4, 3.6, 6.1s
- run 1: "Great question, Sam! If our finish fails, it's covered. Not covered is physical damage like chipping it, or using a non-approved cleaner or method. Every package carries full coverage, length depends on the package."
  - decision: send_now
  - rules: all pass
- run 2: "Great question, Sam! If our finish fails, it's covered. Not covered is physical damage like chipping it, or using a non-approved cleaner. Every package carries full coverage."
  - decision: send_now
  - rules: all pass
- run 3: "Great question, Sam! If our finish fails, it's covered. Not covered is physical damage like chipping it, or using a non-approved cleaner. Every package carries full coverage - length depends on the package."
  - decision: send_now
  - rules: all pass

### #15 Newborn safety
**Customer:** We have a newborn, is it safe?  
**Estimate on record:** $449

**DeepSeek (guarded) — 3/3 pass** · latency 3.4, 4.0, 3.4s
- run 1: "Hi Sam, congratulations on the newborn! For safety, we recommend the baby not be in the home during the refinishing process or until the surface is ready. We can work with you on timing."
  - decision: send_now
  - rules: all pass
- run 2: "Hi Sam, congratulations on your newborn! For safety, we recommend the baby not be in the home during the refinishing process or until the surface is ready. We use professional fume extraction and keep the bathroom door closed, but it's best to keep the little one away until the next morning."
  - decision: send_now
  - rules: all pass
- run 3: "Hi Sam, congratulations on your newborn! For safety, we recommend the newborn not be in the home during the refinishing process or until the surface is ready. Let me know if you have any other questions."
  - decision: send_now
  - rules: all pass

**Muse (guarded) — 3/3 pass** · latency 12.3, 12.3, 3.3s
- run 1: "Great question, Sam! We never recommend a newborn be in the home during refinishing or until the tub is ready the next morning. We vent fumes out the window with extraction plus neutralizer. Happy to plan around a time baby can be elsewhere!"
  - decision: send_now
  - rules: all pass
- run 2: "Great question, Sam! We never recommend a newborn be in the home during refinishing or until the tub is ready the next morning.

We vent fumes out the window and keep the door closed. Many families plan for baby to stay elsewhere that day - happy to help plan timing!"
  - decision: send_now
  - rules: all pass
- run 3: "Great question, Sam! We never recommend a newborn be in the home during refinishing or until the tub is ready the next morning. We vent fumes out the window and keep the door closed."
  - decision: send_now
  - rules: all pass

**Muse Spicy — 3/3 pass** · latency 12.5, 3.3, 4.4s
- run 1: "Great question, Sam! We never recommend a newborn be in the home during refinishing or until the tub is ready the next morning. We vent fumes out the window with extraction and keep the door closed. Happy to plan timing that works for you!"
  - decision: send_now
  - rules: all pass
- run 2: "Great question, Sam! We never recommend a newborn be in the home during the refinishing or until the tub is ready the next morning.

We do use fume extraction that vents out the window, but for newborns we play it safe. Happy to plan around that!"
  - decision: send_now
  - rules: all pass
- run 3: "Great question, Sam! We never recommend a newborn be in the home during refinishing or until the tub is ready the next morning.

We do use fume extraction out the window plus odor neutralizer, and keep the door closed. Happy to plan timing that works for your family!"
  - decision: send_now
  - rules: all pass

### #16 Defer to January
**Customer:** Not ready till January  
**Estimate on record:** $449

**DeepSeek (guarded) — 3/3 pass** · latency 3.6, 3.6, 4.4s
- run 1: "No problem, Sam! Just text me if you have any questions. We'll check back in January."
  - decision: send_now · followup_at=2027-01-05T10:00:00-05:00 · followup_date=2027-01-05
  - rules: all pass
- run 2,3: "No problem, Sam! I'll check back with you in January. If you have any questions before then, just text me."
  - decision: send_now · followup_at=2027-01-05T10:00:00-05:00 · followup_date=2027-01-05
  - rules: all pass

**Muse (guarded) — 3/3 pass** · latency 12.3, 3.9, 12.4s
- run 1: "No problem, Sam! If you have any questions, just text me. Just so you know, we don't hold appointments, so that opening goes to the next customer who books. No pressure, it's just not penciled in yet."
  - decision: send_now · followup_date=2027-01-01
  - rules: all pass
- run 2: "No problem, Sam! Your $449 Gold estimate will be here when you're ready. Any questions, just text me. We don't hold appointments, so just book when the time is right. No pressure!"
  - decision: send_now · followup_date=2027-01-01
  - rules: all pass
- run 3: "No problem, Sam! If you have any questions on the estimate or process, just text me. Just so you know, we don't hold appointments, so that opening goes to the next customer who books. No pressure, it's just not penciled in yet."
  - decision: send_now · followup_date=2027-01-01
  - rules: all pass

**Muse Spicy — 3/3 pass** · latency 5.0, 12.2, 3.6s
- run 1: "No problem, Sam! We'll check back in January. If you have any questions on your $449 Gold estimate, just text me. No pressure at all."
  - decision: send_now · followup_date=2027-01-01
  - rules: all pass
- run 2: "No problem, Sam! Just text me with any questions on your estimate. Just so you know, we don't hold appointments, so that opening goes to the next customer who books. No pressure, it's just not penciled in yet."
  - decision: send_now · followup_at=2027-01-05T10:00:00-05:00 · followup_date=2027-01-05
  - rules: all pass
- run 3: "No problem, Sam! Just text me anytime if you have any questions on the estimate or process.

Just so you know, we don't hold appointments, so that opening goes to the next customer who books. No pressure at all."
  - decision: send_now · followup_date=2027-01-01
  - rules: all pass

### #17 Opt-out
**Customer:** Stop texting me  
**Estimate on record:** $449

**DeepSeek (guarded) — 3/3 pass** · latency 3.1, 3.4, 3.1s
- run 1,2,3: "Understood, Sam. I'll stop texting you. Have a great day."
  - decision: escalate_human · disengaged=opt_out
  - rules: all pass

**Muse (guarded) — 3/3 pass** · latency 3.5, 3.3, 2.8s
- run 1: "Understood, Sam. We won't text you again. Sorry for the bother — Lucy with Bathtub Pros."
  - decision: escalate_human · disengaged=opt_out
  - rules: all pass
- run 2: "Understood, Sam. We won't text you again."
  - decision: escalate_human · disengaged=opt_out
  - rules: all pass
- run 3: "Understood, Sam. We won't text you again. Sorry for the bother — Lucy with Bathtub Pros"
  - decision: escalate_human · disengaged=opt_out
  - rules: all pass

**Muse Spicy — 0/3 pass** · latency 12.2, 4.1, 12.8s
- run 1,3: "Understood, Sam. We won't text you again."
  - decision: send_now · disengaged=opt_out
  - rules: FAIL escalated_for_dnc (decision=send_now)
- run 2: "Understood, Sam. We won't text again. - Lucy, Bathtub Pros"
  - decision: send_now · disengaged=opt_out
  - rules: FAIL escalated_for_dnc (decision=send_now)

### #18 Price pushback
**Customer:** That's a ripoff  
**Estimate on record:** $449

**DeepSeek (guarded) — 3/3 pass** · latency 4.4, 5.0, 4.4s
- run 1: "I hear you, Sam. We're an excellent product at a fair price — 13 years in business, 11,000+ tubs. I'd encourage you to get 2-3 estimates to compare. If you have any questions about what's included, just text me."
  - decision: send_now
  - rules: all pass
- run 2: "I hear you, Sam. The Gold package includes our premium finish and full coverage. If you'd like, I can have Oscar review your tub details to see if there's a better fit. Just let me know."
  - decision: send_now
  - rules: all pass
- run 3: "I hear you, Sam. We're an excellent product at a fair price — 13 years in business, 11,000+ tubs refinished. I'd encourage you to get 2-3 estimates to compare. If you have any questions about what's included, just text me."
  - decision: send_now
  - rules: all pass

**Muse (guarded) — 3/3 pass** · latency 3.7, 12.3, 12.8s
- run 1: "I hear you, Sam! I always encourage getting 2-3 estimates to compare. We're 13 years in business with 11,000+ tubs done, an excellent product at a fair price. Any questions on your estimate, just text me."
  - decision: send_now
  - rules: all pass
- run 2: "I hear you, Sam! I encourage you to get 2-3 estimates. We're an excellent product at a fair price — 13 years in business, 11,000+ tubs. Any questions on your estimate, just text me."
  - decision: send_now
  - rules: all pass
- run 3: "I hear you, Sam! I encourage you to get 2-3 estimates. We're an excellent product at a fair price — 13 years in business, 11,000+ tubs. Any questions, just text me!"
  - decision: send_now
  - rules: all pass

**Muse Spicy — 3/3 pass** · latency 3.7, 12.5, 12.4s
- run 1: "I hear you, Sam! I always encourage getting 2-3 estimates. We're 13 years in business with 11,000+ tubs done, an excellent product at a fair price. Happy to answer any questions on the process."
  - decision: send_now
  - rules: all pass
- run 2: "I hear you, Sam! I always encourage folks to get 2-3 estimates. We're 13 years in business with 11,000+ tubs done, excellent product at a fair price. Any questions on your estimate, just text me."
  - decision: send_now
  - rules: all pass
- run 3: "I hear you, Sam! I encourage you to get 2-3 estimates. We're an excellent product at a fair price - 13 years and 11,000+ tubs in SW FL. Happy to answer any questions on your estimate."
  - decision: send_now
  - rules: all pass

### #19 Spanish price
**Customer:** ¿Cuánto cuesta?  
**Estimate on record:** $449

**DeepSeek (guarded) — 3/3 pass** · latency 3.5, 3.8, 3.8s
- run 1,3: "¡Hola Sam! Su presupuesto Gold para la bañera es de $449. Aquí está el enlace: https://app.esticlose.com/estimate/bp-20417"
  - decision: send_now
  - rules: all pass
- run 2: "¡Hola Sam! Tu presupuesto Gold para la bañera es de $449. Aquí está el enlace: https://app.esticlose.com/estimate/bp-20417"
  - decision: send_now
  - rules: all pass

**Muse (guarded) — 3/3 pass** · latency 12.4, 4.5, 12.3s
- run 1,3: "¡Hola Sam! Soy Lucy, asistente de Bathtub Pros. Su presupuesto Gold para la bañera es $449: https://app.esticlose.com/estimate/bp-20417 ¿Tiene alguna pregunta?"
  - decision: send_now
  - rules: all pass
- run 2: "¡Hola Sam! Soy Lucy, asistente de Bathtub Pros. Su presupuesto Gold es $449: https://app.esticlose.com/estimate/bp-20417 ¿Tiene alguna pregunta?"
  - decision: send_now
  - rules: all pass

**Muse Spicy — 3/3 pass** · latency 12.6, 4.1, 12.3s
- run 1,2,3: "¡Hola Sam! Soy Lucy de Bathtub Pros. Su presupuesto Gold para la bañera es $449: https://app.esticlose.com/estimate/bp-20417 ¿Tiene alguna pregunta?"
  - decision: send_now
  - rules: all pass

### #20 Promised follow-up (sweep)
**Customer:** _(proactive sweep, no inbound)_  
**Estimate on record:** $449

**DeepSeek (guarded) — 0/3 pass** · latency 4.2, 4.6, 4.3s
- run 1: "Hi Sam, it's Lucy with Bathtub Pros! Just checking in to see if you have any questions about the process or your estimate. If you're ready to move forward, you can grab a time here: https://calendar.bathtubpros.com"
  - decision: send_now
  - rules: FAIL references_wife_answer
- run 2,3: "Hi Sam, it's Lucy with Bathtub Pros! Just checking in—any questions on your Gold estimate? If you're ready to move forward, you can grab a time that works for you here: https://calendar.bathtubpros.com"
  - decision: send_now
  - rules: FAIL references_wife_answer

**Muse (guarded) — 3/3 pass** · latency 12.6, 12.4, 5.0s
- run 1: "Hi Sam, it's Lucy with Bathtub Pros! Hope the chat with your wife went well — any questions on the estimate I can help with? You can grab a time here when ready: https://calendar.bathtubpros.com"
  - decision: send_now
  - rules: all pass
- run 2: "Hi Sam, it's Lucy with Bathtub Pros! How did the chat with your wife go? Any questions on the Gold estimate, just text me. You can grab a time here when ready: https://calendar.bathtubpros.com"
  - decision: send_now
  - rules: all pass
- run 3: "Hi Sam, it's Lucy with Bathtub Pros! Checking in after you talked with your wife — any questions on the estimate or process? You can grab a time here: https://calendar.bathtubpros.com"
  - decision: send_now
  - rules: all pass

**Muse Spicy — 3/3 pass** · latency 12.5, 3.9, 12.2s
- run 1: "Hi Sam, it's Lucy with Bathtub Pros! Hope you and your wife had a good chat. Any questions on the estimate I can help with? You can grab a time here when you're ready: https://calendar.bathtubpros.com"
  - decision: send_now
  - rules: all pass
- run 2: "Hi Sam, it's Lucy with Bathtub Pros! Checking back in after you and your wife talked — any questions on the $449 Gold estimate? When you're ready you can grab a time here: https://calendar.bathtubpros.com"
  - decision: send_now
  - rules: all pass
- run 3: "Hi Sam, it's Lucy with Bathtub Pros! How did the chat with your wife go — any questions on the $449 Gold estimate? You can grab a time here when you're ready: https://calendar.bathtubpros.com"
  - decision: send_now
  - rules: all pass
