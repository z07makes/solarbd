# Real numbers: cold-storage battery cost and residential SAM/CAC

**Compiled:** August 2, 2026, via live web research (not training-data recall — battery pricing, exchange rates, and Bangladesh policy all move too fast for that). Every figure below has a source; every calculation was run live in `real_numbers_research.py` alongside this file.

---

## 1. Cold storage battery cost — the placeholder was optimistic, not pessimistic

The earlier finding (`COLD-STORAGE-FINANCING-FINDING.md`) flagged Tk25,000/kWh as "likely too high for utility scale." **That hedge was wrong.** Real 2026 pricing data across multiple independent industry sources (CNTE, BSLBATT, AnengJi Power) converges on:

- **Commercial & Industrial tier (100kWh–10MWh — where a 1,500kWh system sits):** $200–350/kWh installed
- **1–2MWh containerized systems specifically:** $195–235/kWh ex-works China, $255–295/kWh installed in North America/Europe

Bangladesh announced **zero import duty on solar modules, inverters, batteries, and BESS equipment** in June 2026, which should keep landed Bangladesh cost closer to the ex-works-China end than the installed-NA/EU end — but there's still local EPC, logistics, and integration cost on top of ex-works pricing.

**Working estimate: Tk27,000–37,000/kWh (US$220–300/kWh at today's ৳123.3/USD), midpoint ~Tk30,800/kWh** — meaningfully *higher* than the Tk25,000/kWh this project has been using, not lower.

### Recomputed cold-storage coverage, at the real cost

| Financing | All-in EMI (solar + 1,500kWh battery) | Coverage vs. Tk267,177/mo savings |
|---|---|---|
| Green-refinance terms (15%/10yr/5%) | Tk493,490/mo | **54.1%** |
| Standard commercial terms (20%/7yr/12%) | Tk773,013/mo | **34.6%** |

Versus the headline claim of 349%. This is a *worse* picture than the previous finding reported (41–64%), because the real battery cost turned out higher than assumed, not lower.

### One genuinely good-news finding

SREDA's own financing page (sreda.gov.bd) lists **"solar cold storage"** explicitly as an eligible IDCOL/green-refinance sub-sector, in the same category list as other hybrid solar+storage systems (e.g., telecom BTS hybrid solutions). This is real evidence — not certainty, but a real regulatory signal — that the **battery portion of a solar-cold-storage system likely qualifies for the same concessional terms as the solar portion**, rather than needing separate, harsher commercial financing. That's more optimistic than the prior finding's "unconfirmed either way" caveat.

### What's still not resolved

- No line-item Tk/kWh confirmation for battery storage specifically under IDCOL terms — only a named-category signal.
- All C&I battery pricing above is global; Bangladesh-specific vendor quotes (Fakir Technologies' "ZERO" BESS line, Huawei, SAV Digital Power, or Rahimafrooz's expanding BESS offering — all real, active suppliers in Bangladesh's market right now per `models/poultry_sizing_audit.py`'s sibling research) would be the actual next step, not another web estimate.
- Fakir Technologies Ltd. has emerged as a real, locally-manufactured BESS competitor (their "ZERO" brand, Sungrow-partnered, already running a 1MW installation at Fakir Fashion's own facility) — this is new competitive intelligence not reflected anywhere in the existing project research, worth folding into the market-benchmark materials.

---

## 2. Residential SAM — the placeholder was already right

Confirmed via the 2022 Bangladesh census (Bangladesh Bureau of Statistics): **41,000,000 total households**, average size 4.26 people. This matches the ~41–43M figure the project was already using — it wasn't a guess needing correction.

The real open question was never the national household count; it's what *fraction* of 41M is a realistic early-years addressable segment. The best available public proxy: a May 2026 PDB tariff-slab restructuring proposal noted impact on "35% of consumers, of which 23 points are lower-middle-class, under 200 units/month" — implying roughly **12% of residential consumers use more than 200 units/month** nationally (a rough proxy for "has a bill worth acting on," not a clean slab-distribution table, which doesn't appear to be published anywhere accessible).

Applying that: 41M × ~12% ≈ **4.9M households** as a rough plausible ceiling. The existing placeholder of 500,000 households is about 10% of that ceiling — a defensible early-years slice, not an overreach.

---

## 3. Residential CAC — also higher than the placeholder, same direction as cold storage and poultry

SolarSquare (India — same product, comparable South Asian income/labor environment) runs its main acquisition channel through a named referral program ("SolarPro"): **Rs 2,000/kW commission**, no other CAC publicly disclosed.

| System size | Referral commission alone |
|---|---|
| 3.0 kW | Tk7,740 |
| 5.5 kW | Tk14,190 |
| 8.0 kW | Tk20,640 |

The existing placeholder was **Tk4,000/customer**. Even the smallest typical system's referral commission *alone* — before any marketing spend, sales ops, or onboarding cost — already exceeds it. Global fintech CAC benchmarks ($1,450+ for SMB in the US/EU) aren't used here since Bangladesh's digital ad and labor costs are much lower and not comparable; the India solar-specific referral model is the better comp because it's the same product in an adjacent, income-comparable market.

**Direction, across all three findings now (poultry, cold storage, residential CAC): reconciling placeholder assumptions with real data has moved costs up, not down, in every case except poultry's system-size mismatch.** This is worth taking seriously as a pattern, not three unrelated coincidences.

---

## Caveats that apply to all of the above

- Global BESS pricing and Bangladesh-specific vendor quotes are not the same thing. Getting an actual quote from Fakir Technologies, Huawei, or SAV Digital Power for a 1,500kWh system would replace an estimate with a fact.
- The residential SAM "12% of consumers" figure is a rough proxy from a single news article about a specific tariff proposal, not a published slab-distribution census. Treat it as directional, not authoritative.
- The SolarSquare CAC comp is a single data point (their referral commission rate) from one channel; SolarSquare's *total*, fully-loaded CAC (including marketing, sales, onboarding) is not publicly disclosed and is almost certainly higher than the referral commission alone.
- None of this is financial advice — it's sourced scenario modelling with assumptions stated so they can be replaced with real quotes.
