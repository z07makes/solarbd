# SolarThik — Pilot & Seed One-Pager

**A hybrid solar decision layer for Bangladesh's grid-connected homes and SMEs — software and financing-first, hardware-agnostic, always in support of the grid, never positioned as a replacement for it.**

*This version (Aug 2, 2026) replaces an earlier draft whose cold-storage and residential figures were built on placeholder assumptions that didn't survive contact with real cost and market data. Every number below has been checked against sourced 2026 pricing, a live audit, or a rerun model — not carried forward from an earlier draft.*

## The problem
Bangladesh's June 2026 tariff hike (16.68%), 8–12 hours of daily load-shedding in parts of the country, and a new mandatory net-metering circular for larger buildings have made solar+battery economically obvious — but IEEFA names **lender distrust of feasibility numbers**, not upfront cost, as the actual barrier to adoption. Every existing calculator in the market is run by the company selling the hardware. Nobody independent is producing underwriting-grade numbers.

## What's built and verified, today
- A hybrid dispatch engine (solar/battery/grid switching logic) in both Python and JavaScript, cross-validated against each other line-by-line — 22/22 regression tests pass, and the two independent implementations agree numerically on every tested scenario.
- A lender/integrator portal backend with real, server-side JWT-scoped access control, tested end-to-end (five auth/scoping cases, all correct) — replacing an earlier client-side-only pattern that leaked the full customer dataset to any authenticated viewer regardless of role.
- Segment-specific EMI-coverage modeling for residential, poultry, and cold storage — each now checked against sourced, current market data, not placeholder assumptions.

## The honest numbers, segment by segment

**Poultry: 177% coverage**, on a correctly-sized 3.0kW solar + 5kWh battery system — verified by running the real dispatch engine, not estimated. This is better than an earlier draft's figure, because that figure compared a bigger system's EMI against a smaller system's simulated output. Fixed by simulating the same system the financing actually pays for.

**Cold storage: 131% coverage from solar alone**, no battery required for this number to hold. A large battery for peak-hour bill arbitrage does **not** clear its own honestly-financed cost at real 2026 battery pricing (Tk27,000–37,000/kWh for a system at this scale — verified against multiple independent 2026 industry sources, not the smaller-battery placeholder this project used earlier). Every battery size we tested, from 100kWh to 2,000kWh, is a net monthly loss once its own financing cost is included, at every price point in that range. **The real case for a battery here is resilience, not bill savings**: the Bangladesh Cold Storage Association reports facilities pay 30–40% more in operating costs from diesel generators during load-shedding. That's a real, current, sourced number — but it's a different value stream than arbitrage, and we haven't built a way to quantify it into an EMI-coverage figure yet. We're not going to invent one.

**Residential: real customer economics still look solid (110%+ coverage on typical BERC-slab billing), but the company-level payback story needs a caveat.** An earlier internal model claimed adding residential to the business "reverses" the company's 10-year payback problem even in a conservative growth scenario. Rerun with a real customer-acquisition-cost benchmark (SolarSquare's India referral-commission rate, the closest real comp we could find) instead of a Tk4,000 guess, that specific claim doesn't hold — the conservative growth case no longer clears 10-year payback with residential included. Base and optimistic growth cases still do, at meaningfully reduced but still real magnitude.

## What we're not going to do
Overstate any of this. Every figure above has a citation or a rerun script behind it, in the repo, checkable by anyone. Where we don't have a real number (cold storage's exact resilience value; a Bangladesh-specific, not India-proxy, residential CAC), we say so instead of estimating past it.

## The ask
**A joint pilot: 10–20 installed systems (poultry and/or cold storage prioritized), over roughly 6 months.**

What we bring: the dispatch engine, honestly-verified EMI-feasibility modeling, and a monitoring/risk-scoring layer your own hardware and installation business doesn't currently have.

What we need: access to real installed systems and their telemetry, and (where relevant) an introduction to a financing partner already comfortable underwriting your hardware. For cold storage specifically: a real vendor quote for battery storage at the 500kWh+ scale would replace our best current estimate with a fact, and is probably the single highest-value thing a partner could hand us.

**Alternative framing, if capital rather than a hardware partnership is the right conversation:** a seed round sized to fund the team and customer acquisition, not the systems themselves — those are financed through existing banks/NBFI/IDCOL channels under a packager model, not on our balance sheet. Exact sizing is being revisited now that the residential customer-acquisition-cost assumption has changed materially; we'd rather give a real number than repeat the old one.

## Why now
The regulatory tailwind is real: SREDA's own financing eligibility list names "solar cold storage" as a qualifying hybrid category for green-refinance terms alongside other solar+storage hybrid systems — real evidence that battery-inclusive systems can access the same concessional financing as solar-only ones, not just an assumption. Fakir Technologies has entered the Bangladesh BESS market directly (their "ZERO" line, Sungrow-partnered) since our last review — the trust-layer gap this project fills is getting more urgent, not less, as more hardware players enter without an independent feasibility function attached.

---
*Contact: [name / email / phone] · Repository, validation suite, and every source cited above available on request.*
