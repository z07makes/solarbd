# SolarThik — Market Penetration & Path to Scale
### A deep-dive strategy memo: who we're fighting, how comparable startups actually won, and what it takes to build this into a category leader

*Prepared July 2026, grounded in public data gathered this month. Every figure below is either sourced (noted inline) or explicitly flagged as a modeled estimate. Treat this as a strategy working document, not a fundraising deck — pressure-test every number against real quotes, filings, and term sheets before it goes in front of an investor or lender.*

---

## 1. Executive summary

The honest version, before the detail: **the market opportunity is real and the field is wide open, but the money is the hard part, not the idea.**

- Bangladesh's rooftop/distributed solar market is fragmented — no single firm holds more than 10% share — and the largest named incumbent, Rahimafrooz Renewable Energy, runs on roughly **$6.4M in annual revenue**, as a side division inside a 70-year-old battery-and-retail conglomerate, not a focused, funded growth company. That is a genuinely weak field to enter against.
- The exact playbook we're proposing — software- and financing-led rooftop solar, unseating fragmented local installers — has already been run once, in India, by **SolarSquare**: founded 2015, roughly $500M in reported valuation as of May 2026, ~50,000 homes, $104M annualized revenue. It took about a decade, with the last 18 months doing the heavy lifting.
- Bangladesh's own venture ecosystem has produced exactly **one** unicorn (bKash, ~$1B via Ant Financial in 2018) in its entire history, and startup funding nationally has been *shrinking* — from a 2021 peak down to roughly $42M (2024) and ~$124M (2025), concentrated in fewer, later-stage deals. This is the real constraint on "billion-dollar," not the market.
- The path that's actually walkable: start narrow and asset-light (as discussed previously), use Bangladesh's own new bank-backed startup capital pool for early fuel, prove the model the way SolarSquare and M-KOPA did (data before capital-intensity), and treat regional expansion as part of the plan rather than a stretch goal — nobody has reached this scale from a single mid-sized South Asian market alone.

---

## 2. The market we're actually entering

**Total market size.** Estimates vary by research house (this itself is a signal of how under-covered this market is):

| Source | Metric | 2026 | Forecast | CAGR |
|---|---|---|---|---|
| MarkWide Research | Market value (USD) | $2.1B | $8.24B by 2035 | 16.4% |
| Mordor Intelligence | Installed capacity | 1.57 GW | 2.79 GW by 2031 | 12.2% |

Both agree on the direction and the double-digit growth rate; they disagree on absolute size because one is pricing the value chain in dollars and the other is counting installed hardware — a reminder to build our own bottom-up model rather than quoting either number as gospel.

**A rough household TAM, built from public inputs (not a specific market report — shown so the logic is checkable):**
- Population: ~177.8M (2026, UN-based estimates)
- At an approximate 4.1–4.3 people per household → **~41–43M households**
- At 99.5% grid electrification (2023 figure, likely similar or higher today) → nearly all of those households are grid-connected, tariff-paying customers
- Residential use is 56% of national electricity consumption, against 25,700+ MW of installed generation capacity — a large, currently almost entirely grid-supplied base

**The real serviceable segment is much narrower than "42 million households,"** and that's a feature, not a bug — it's exactly the group we identified before: households and businesses in the steep tariff slabs (Tk 15–17.35/unit), and the newly-created compliance segment (buildings ≥1,000 sq ft or ≥10kW load expansions now legally required to install net-metered solar). That compliance segment alone is a forced-adoption pipeline with no real Bangladeshi precedent — it didn't exist as a market until the December 2025 circular.

**What this means:** the total addressable pie is worth low single-digit billions of dollars and growing at ~12–16% a year, most of the growth is still ahead (2026 is described as "moderately fragmented" with sub-10% leaders), and a meaningful slice of near-term demand is now *compliance-driven* rather than needing to be persuaded from scratch — which is a much better starting position than the "convince a skeptical customer" market most solar startups have had to fight.

---

## 3. Who we're actually fighting: a competitor autopsy

The dozen-plus names from the earlier scan (Rahimafrooz, Solaric, Omera, Ensys, Energypac, Fakir Technologies, and others) look intimidating as a list. They look very different once you check what each of them actually *is*.

**Rahimafrooz Renewable Energy Ltd (RREL)** is the most-cited "market leader," and it's worth sitting with what that actually means:
- **Reported annual revenue: $6.4M (2025).** For comparison, that's less than 7% of what SolarSquare in India generates in a single quarter.
- It is a business unit inside **Rahimafrooz Group**, a 70-year-old conglomerate whose core businesses are automotive batteries, tyres, lubricants, generators, and Bangladesh's Agora supermarket chain. Solar is a side vertical, not the reason the company exists.
- Its historical playbook is the **IDCOL-era model**: subsidized microcredit-financed Solar Home Systems (SHS) for *off-grid* rural households — over 52,000 units lifetime, plus roughly 25 MWp of cumulative installed capacity across all its solar work (on-grid and off-grid combined). That is a fundamentally different customer and financing model from grid-tied hybrid systems for *already-connected* households and businesses trying to cut a bill — which is our actual market.
- It has no meaningful software, monitoring, or embedded-finance layer of its own.

**The rest of the named field** — Solaric, Omera, Ensys, Energypac, and the BESS specialists like Fakir Technologies — are EPC (engineering-procurement-construction) and hardware businesses. Their core competency and incentive structure is *selling and installing panels and batteries*. Their "smart monitoring" and "ROI calculators," where they exist, are sales tools built by a party with an obvious conflict of interest, not independent decision-support.

**Utility-scale is a separate arena we're not entering.** Multilateral development banks (ADB, JICA) are pouring meaningful capital into large solar parks — one 100MW Pabna project alone drew $121.55M in ADB/JICA financing — but that game is played by Chinese state-linked EPCs (Huadian, CREC, Alfanar) through BPDB joint ventures. That's a different competitive set, different capital requirements, and not where a startup should be spending energy.

**The structural read:** every named competitor is either (a) a hardware-and-installation business with a channel-conflicted advisory function bolted on, or (b) a legacy off-grid/rural microcredit operator built for a different customer and financing model. **Nobody in the Bangladeshi market is running a focused, funded, software-and-financing-first company the way SolarSquare does in India.** That gap is the opportunity, and it is a genuinely open one — not because the incumbents are incompetent, but because none of them is structurally built to compete on this axis.

---

## 4. The penetration strategy: how we actually win

The instinct to "beat the competitors" implies a zero-sum fight for the same customer. **The sharper play is closer to judo than to a head-on fight.**

**Don't compete with the EPCs — sit above them.** SolarThik's actual product (feasibility, financing, compliance navigation, monitoring) is complementary to installation, not a substitute for it. Every EPC installer currently has to also play bank, educator, and compliance officer — badly, because that's not their core skill and it slows their sales cycle. Position SolarThik as the layer that **feeds them qualified, pre-financed, compliance-cleared customers** in exchange for a share of the deal or a monitoring fee. This turns potential competitors into a distribution channel on day one, while keeping the option to compete directly (or acquire) once there's leverage.

**Sequence the wedges in order of urgency, not order of ambition:**

1. **Compliance concierge first.** The December 2025 mandatory net-metering rule created a segment that *has to* act, on a deadline, with a confusing application process. This is the fastest, lowest-trust-required sale in the entire market right now, and it's the one competitor set (EPCs) is least equipped to also handle well, since it's paperwork and regulatory navigation, not their core skill.
2. **Layer in the vendor-neutral EMI/financing product** once there's a base of compliance customers and a proof point that the feasibility numbers hold up in the real world.
3. **Turn on the monitoring layer** across every installed system, regardless of which EPC did the install. This is where the actual moat starts compounding (next section).
4. **Only then consider EPC or hardware moves** — direct installation, exclusive hardware partnerships, or acquisition of a distressed local EPC for its install crews and BPDB relationships. One market report explicitly noted that "**valuations sit cheapest among domestic EPC specialists**" — a roll-up strategy is a legitimate later-stage option, not a starting one.

**Why incumbents can't just copy this quickly:**
- **Channel conflict.** An EPC that starts telling customers "here's the honest, sometimes-unflattering feasibility number" undercuts its own sales team's incentive to close deals on optimistic assumptions.
- **Balance sheet and org structure.** A financing product needs a different risk function, different hires, and different capital than a hardware business — Rahimafrooz Group's core competence is trading and retail, not underwriting.
- **No software culture.** Building and maintaining an IoT monitoring layer and a live feasibility engine is a technology company's job. None of the named competitors is organized, staffed, or funded like one.

---

## 5. The playbook already exists — three companies that cracked comparable markets

This is not a novel category. It's been run to real scale at least twice, and the lessons transfer directly.

### 5.1 SolarSquare (India) — the closest blueprint, almost a direct template

| | |
|---|---|
| Founded | 2015, Mumbai |
| What it does | Designs, installs, finances, and monitors rooftop solar for homes, housing societies, and enterprises — explicitly positioned against a "fragmented market... dominated by small local installers" |
| Scale (2026) | ~50,000 households, ~400 housing societies, 29 cities / 9 states, 150MW+ installed |
| Revenue | Annualized run-rate over ₹10B (~$104M) |
| Funding | Reported total raised in the $60–115M range across sources (figures vary by data provider); Series A ~$12M at ~$48M valuation (Nov 2022) → Series B $40M at ~$200M valuation (Dec 2024) → Series C reportedly ~$55–60M at ~$450–500M valuation (May 2026, not fully confirmed closed at time of reporting) |
| Investors | Lightspeed Venture Partners, B Capital, Elevation Capital, Rainmatter, Lowercarbon |
| Enterprise clients | Swiggy, Zepto, iD Fresh Food |

**The lesson:** it took ~7 years to get from founding to a real institutional Series A, and the valuation *doubled in the 18 months before this memo was written* — growth in this category is slow to start and can compound hard once the model is proven. Coverage of the round explicitly frames the shift as: *"rooftop solar is now a digital infrastructure decision... beyond hardware, software platforms for sales, design, remote monitoring, and lifecycle management are emerging as key differentiators."* That is precisely our thesis, already being rewarded by growth-stage capital, one border away.

### 5.2 Sun King / Greenlight Planet (Africa & Asia) — the long game and what capital-intensity really looks like

Founded 2007. Rebranded from Greenlight Planet to Sun King in 2022 alongside a $260M Series D led by General Atlantic's BeyondNetZero. Total funding to date: **$547M across 20 rounds**. As of early 2026, it announced a further $150M specifically to expand its pay-as-you-go model into Ethiopia. ~1,850 employees.

**The lesson:** this is the honest ceiling on how capital-intensive "financing + hardware for people who can't pay upfront" gets at true scale — and it took **almost two decades**. The sector as a whole (Sun King, M-KOPA, d.light, Bboxx, Zola, Engie Energy Access, Lumos) has absorbed roughly $2.3B in cumulative funding for ~72% of the category. That's the real size of the global bet on this model, spread across the seven best-funded players, over 15+ years. Anyone underwriting a "billion-dollar startup" plan should underwrite this timeline, not a three-year one.

### 5.3 M-KOPA (Kenya / East Africa) — the data-as-underwriting model

Already covered in depth previously: 5M+ customers, $1.5B+ in credit extended, IoT-linked micro-payments, AI credit-scoring built entirely from payment behavior rather than a credit bureau file.

**The lesson that matters most for us:** M-KOPA's real product was never the solar panel — it was the **proprietary repayment and usage dataset**, which let it underwrite people no bank would touch, and which became more valuable (and harder to replicate) with every customer added. This is the direct analogue to the monitoring-layer moat described in section 4: the data compounds, the hardware doesn't.

### 5.4 bKash (Bangladesh) — proof it's possible here, with an important caveat

Bangladesh's only unicorn to date: reached roughly $1B in valuation after Ant Financial (Alibaba's fintech affiliate) invested in 2018, following earlier backing from IFC (2013) and the Gates Foundation (2014). It's now reported to process **over $2B in transactions monthly**.

**The caveat that matters:** bKash's TAM is "every financial transaction in a country of 178 million people" — a platform-infrastructure play. Solar is a real, growing, underserved market, but it is not that. The lesson to take from bKash isn't "solar can be as big as bKash" — it's **what kind of institutional capital is willing to write large Bangladesh checks, and why**: IFC and the Gates Foundation came in early on a *financial inclusion* thesis, not a "solar" thesis. That's a useful reframe — pitch this as embedded climate-finance/financial-inclusion infrastructure, not as a solar installer, when it's time to raise from that tier of investor.

### Side-by-side

| | SolarSquare | Sun King | M-KOPA | bKash |
|---|---|---|---|---|
| Years to significant scale | ~10 | ~18 | ~13 | ~5 (with IFC/Gates backing from year 1) |
| Core moat | Software + financing vs. fragmented installers | Distribution network + financing depth | Proprietary payment/credit data | Agent network + mobile money infrastructure |
| Capital raised | ~$60–115M+ | $547M | Undisclosed, but backed by $1.5B+ in credit extended | ~$1B+ valuation on strategic + development-finance capital |
| Most transferable lesson for us | Nearly the exact model — replicate directly | Patience; this category rewards distribution and time, not speed | Monitoring data *is* the underwriting engine | Development-finance capital cares about inclusion narratives, not just IRR |

---

## 6. What "billion dollar" actually requires — the math

Take SolarSquare's own numbers as the most defensible real-world reference point, since it's the closest business model in the most comparable region: **~$104M in annual revenue supporting a reported ~$450–500M valuation** — roughly a **4.5–5x revenue multiple**. That's a realistic planning multiple for this category at growth stage, more useful than a generic SaaS or fintech multiple pulled from a different sector.

**Rough (illustrative, not verified) unit economics**, using the numbers from the calculator built earlier:
- Average system + financing package: ~Tk 400,000–500,000
- If SolarThik earns an origination/referral fee of 3–5% on financed volume, plus a recurring monitoring fee (illustratively Tk 300–600/month per active system):
 - Year-one revenue per customer: roughly Tk 15,000–25,000 (~$125–210)
 - **Reaching something in the neighborhood of a $100M annual revenue run-rate — SolarSquare's current scale — would require somewhere on the order of several hundred thousand active customers on the platform.**

That is a large number in absolute terms, but it's a small single-digit percentage of the ~41–43M household TAM, and it's roughly the same order of magnitude SolarSquare reached in ~50,000 *fully installed* households plus a much larger financed/monitored base — reinforcing that this is directionally achievable over a decade-scale horizon, not a fantasy.

**What actually moves the multiple, based on the comps above:**
- **Recurring, data-generating revenue** (monitoring, SaaS-style fees) is valued far more richly than one-time installation margin — this is the single biggest argument for prioritizing the monitoring layer even when it looks like the least urgent piece early on.
- **A financial-inclusion or embedded-finance narrative** unlocks a different, deeper pool of capital (development finance institutions, impact-oriented growth funds) than a "solar installer" narrative does — bKash and Sun King both benefited from this framing.
- **Regional footprint** is close to a prerequisite at this stage of company, not a bonus. Pathao's own scale-up included expansion into Nepal. Sun King and M-KOPA are both explicitly multi-country. A Bangladesh-only plan likely caps out well below the comps above; a Bangladesh-plus-adjacent-market plan (Nepal, or eventually Pakistan, both of which share the tariff-pain/financing-gap dynamics researched earlier) is a more fundable story at Series B and beyond.

---

## 7. The execution roadmap: what actually needs to be done

**Team, in rough hiring order:**
1. Founding team covering (a) BD regulatory/government relations — BERC, SREDA, DESCO/BPDB — and (b) product/software for the feasibility engine and monitoring platform
2. Credit/risk hire as soon as the financing-packager motion starts, even before any lending license is contemplated — this person builds the feasibility-scoring model that becomes the actual product
3. BD/partnerships lead to sign the first 2–3 EPC "channel" relationships and the first bank/NBFI referral relationship
4. Field operations/installer-QA function — since quality risk sits with partner EPCs under the packager model, someone has to own it anyway

**Capital sequence:**
- **Pre-seed/seed:** Given Bangladesh's own funding contraction (2024: ~$42M across the *entire* national startup ecosystem; 2025: ~$124M across just 12 deals), realistic early capital sources are the new **Bangladesh Bank-backed Start-up Investment Company PLC** (formed December 2025 with Tk 4.25B in paid-up capital from 39 commercial banks, explicitly created to fund the next bKash/Pathao/Chaldal-type company), Startup Bangladesh Limited (the existing government-backed VC fund), and angel/regional pre-seed funds.
- **Series A and beyond:** Target the investor profile that's actually active in this exact category regionally — Lightspeed, B Capital, and Elevation Capital all just underwrote SolarSquare's thesis in India; a Bangladesh company with real usage and repayment data (the M-KOPA lesson) and a regional-expansion story is a legible pitch to the same pool.
- **Development finance, once there's traction:** IFC, and Gates-Foundation-style inclusion-focused capital, are proven to write meaningful Bangladesh checks specifically on a financial-inclusion thesis — this is a later, not first, conversation, but it's worth building the data trail toward it from day one.

**Regulatory and partnership relationships to build immediately:** SREDA (owns the net-metering application process — the compliance wedge lives here), BERC (tariff policy), at least one bank or NBFI willing to pilot referral-based EMI origination, and IDCOL (existing green-financing infrastructure and decades of institutional memory on what has and hasn't worked in solar financing here).

---

## 8. Honest risks

A recent write-up on SolarSquare's own funding round listed its sector's real risk factors plainly: *policy and subsidy uncertainty, execution and installation quality issues, working capital constraints, grid backflow and safety challenges, and customer churn from poor service.* Every one of these applies here, plus some Bangladesh-specific ones:

- **Funding environment risk is real and current.** Bangladesh VC activity has been actively contracting through 2024–2025, and investors are described as "cautious" during the current interim-government period. This is the single biggest variable outside the company's control.
- **Policy risk cuts both ways.** The net-metering mandate is a tailwind today; tariff structures, subsidy policy, and net-metering rules have all changed materially within the last 18 months and could change again.
- **Quality risk is inherited, not controlled**, under a packager model — a bad install by a partner EPC becomes SolarThik's reputational problem even though SolarThik didn't do the work.
- **Currency and import risk.** Hardware remains import-dependent; Taka depreciation raises effective system costs independent of anything the company does.
- **This is a long game.** Every credible comp above took a decade or more. A plan that implicitly assumes a 3–4 year path to billion-dollar scale isn't supported by a single company in this category, anywhere.

---

## 9. Bottom line

The market structure is genuinely favorable — fragmented, under-capitalized incumbents, a fresh regulatory tailwind, and a proven international blueprint one border away in SolarSquare. The honest constraint isn't competitive; it's that Bangladesh's domestic capital pool for this kind of company is thin and currently shrinking, which makes the funding strategy — not the product strategy — the hardest part of this plan. The realistic path: start with the narrow, urgent, low-capital wedge already identified (compliance concierge), build the monitoring/data layer as the real long-term moat rather than a nice-to-have, fund the earliest stage through Bangladesh's own new bank-backed vehicle rather than waiting for foreign VC, and treat regional expansion as core strategy rather than a someday-goal — because no company in any of the four comps above reached this scale from one mid-sized market alone.

---

## Sources & methodology note

Market sizing: MarkWide Research and Mordor Intelligence (Bangladesh solar market reports, 2026 editions). Competitor data: Rahimafrooz Group corporate materials, RocketReach, Ashden Awards case study, MarkWide Research. International comps: TechCrunch, Tracxn, PitchBook, Dealroom, CB Insights, General Atlantic press materials, and prior M-KOPA research. Bangladesh startup ecosystem: Tracxn, The Daily Star, The Financial Express, CGS. Bangladesh macro data: UN population data via StatisticsTimes/Worldometer, Wikipedia's Electricity Sector in Bangladesh (BPDB/BERC-sourced figures). Where sources disagreed (e.g., SolarSquare's total funding, Rahimafrooz's installed capacity), both figures are shown rather than silently picking one. Unit-economic and TAM modeling in Sections 2 and 6 is original illustrative analysis built from these inputs, not a quoted third-party figure — flagged accordingly throughout.
