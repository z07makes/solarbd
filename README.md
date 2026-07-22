# SolarThik — Hybrid Solar Decision Layer for Bangladesh

**Core principle, stated up front because it's easy to drift from: SolarThik is a support layer on top of the grid connection — solar + battery + smart switching — not a replacement for it.** Every model, mockup, and dispatch-logic decision in this repo should be checked against that before it's extended.

Working strategy repo, not a fundraising deck. Figures throughout are sourced where noted and clearly flagged as modeled/illustrative where not — see each document's own methodology section before using anything customer- or investor-facing.

## What's in here

### `/demos` — interactive HTML prototypes
- **`solarthik-demo.html`** — the original pitch demo: overview, the smart EMI-vs-savings calculator (real BD tariff slabs), a live hybrid switching dashboard, market benchmark (Pakistan/India/Kenya vs. Bangladesh), and positioning/roadmap.
- **`solarthik-platform-prototype.html`** — the software/data layer prototype: a live telemetry→daily→monthly→risk-score pipeline simulation, a customer app mockup (segment-specific: residential/poultry/cold storage), and a lender/integrator portfolio portal with the generation-vs-repayment correlation chart.

### `/reports` — research and financial analysis
- **`solarthik-deep-dive.md`** — market penetration strategy: competitor autopsy (Rahimafrooz and the wider BD field), international case studies (SolarSquare, Sun King, M-KOPA, bKash), and what "billion-dollar scale" actually requires.
- **`SolarThik_Part1_SME_Market_Financial_Case.pdf`** — SME market analysis (poultry, cold storage; "waste processing" was tested and honestly dropped, see the doc) plus load-profile-grounded financial models for both segments and a residential/commercial baseline.
- **`SolarThik_Part2_Mitigation_Sizing_Cost_Payback.pdf`** — mitigation strategy (Bangladesh Bank's green refinance scheme is the biggest lever, not solar engineering), TAM/SAM sizing, cost to capture the market, and a realistic (not fantasy) capture-rate and payback model. **Includes a transparent note on a payback-calculation bug that was caught and fixed before this version** — worth reading as a methodology note, not just a result.

### `/models` — the actual calculation scripts behind the PDFs
Python, not spreadsheets, so the logic is auditable and rerunnable: `sme_calc.py` (poultry + cold storage load/financial models), `tam_sam.py` (market sizing), `cost_to_capture.py` (team cost, CAC by channel), `mitigation_calc.py` (green-refinance and efficiency-retrofit stacking), `capture_payback.py` (the S-curve capture model with the corrected payback logic).

## Known open items
- Cold storage facility count has two conflicting sourced figures (400/6M tonnes vs. 365/3.2M tonnes) — Part 2 uses the more recent one and flags the correction; Part 1 has not yet been re-issued with it.
- VFD retrofit *savings* are sourced; VFD retrofit *cost* is not — needs a real vendor quote before it's used in any customer-facing number.
- The ETP/textile-effluent segment was flagged as a promising fourth vertical but was never given its own research pass — treat it as a lead, not a validated segment.
- Software architecture (data schema + app layer) has a working prototype in `/demos` but no formal spec document yet.

## Working principle for whoever picks this up next
Every mitigation, financial model, and app mockup in here should keep the grid as the default, expected state — solar/battery involvement is always a conditional exception (arbitrage or outage), never the steady-state goal. If a future change makes the pitch read like "go off-grid" or like SolarThik becoming a lender/EPC/installer outright, that's drift — pull it back toward packager/enabler, per the positioning work in the deep-dive report.
