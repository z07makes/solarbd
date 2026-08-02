# Finding: the real residential CAC reverses the conservative-scenario payback claim

**Found:** August 2, 2026, immediately after sourcing the real CAC figure.
**Status:** New. This is the most consequential finding of the three (poultry/cold-storage/this) because it changes a conclusion the project was actively using to justify prioritizing residential.

## What the master doc claimed

Section 3.6: adding residential to the payback model "**reverses** the sobering Session-1 finding" — specifically, the CONSERVATIVE scenario went from never paying back in 10 years (-Tk151M by Yr10) to paying back in **Year 1** (+Tk46M by Yr10). This was called "the single biggest lever on whether this business pays back at all within a normal capital timeframe," resting entirely on a placeholder CAC of Tk4,000/customer.

## What happens with the real CAC

`residential_payback_updated.py` reruns the identical model, same methodology, only the CAC changed — from the Tk4,000 placeholder to Tk14,190 (SolarSquare's India referral-commission benchmark, scaled to SolarThik's own 5.5kW default system size):

| Scenario | At Tk4,000 CAC (placeholder) | At Tk14,190 CAC (real) |
|---|---|---|
| Conservative | Pays back Yr1, +Tk46M by Yr10 | **Does NOT pay back in 10yr, -Tk39M by Yr10** |
| Base | Pays back Yr1, +Tk501M by Yr10 | Pays back Yr1, +Tk270M by Yr10 (46% lower) |
| Optimistic | Pays back Yr1, +Tk1,260M by Yr10 | Pays back Yr1, +Tk775M by Yr10 (38% lower) |

**The conservative-scenario reversal — the specific claim that made residential look like the fix for the whole business's payback problem — does not survive contact with a real CAC figure.** Base and Optimistic still pay back, just at meaningfully reduced magnitude.

## Why this matters more than the other two findings

Poultry and cold storage are segment-level economics — they affect how attractive one product line looks. This affects the **company-level thesis** that residential was the answer to whether SolarThik pays back its own invested capital at all. That thesis was resting on a number that turned out to be roughly 3.5x too low.

## What this doesn't mean

- Base and Optimistic scenarios still work. This isn't "residential doesn't work" — it's "residential doesn't rescue the Conservative case the way it was advertised to."
- The Tk14,190 figure is a referral-commission-only estimate from a comparable market (India), not a Bangladesh-specific, fully-loaded CAC (which would also include marketing spend, sales ops, and onboarding cost — likely higher still). A real Bangladesh pilot would be the only way to get a number better than this.
- The s-curve capture-rate assumptions (ceiling fractions, midpoint years, steepness) are unchanged and equally unvalidated as before — CAC isn't the only placeholder in this model, just the one that was just tested against real data.

## Recommendation

Don't cite the "residential flips the conservative case" claim in investor or lender materials until either (a) a real Bangladesh CAC figure replaces this India-comp estimate, or (b) the pitch is reframed around Base/Optimistic cases specifically rather than "even the conservative case works now."
