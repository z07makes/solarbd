"""
Real-numbers research pass: cold storage battery cost + residential SAM/CAC.
Every figure below is sourced from live web search on 2026-08-02, not
carried over from the placeholder assumptions in the original models.
"""

print("="*78)
print("PART 1 -- COLD STORAGE: real battery cost at 1500kWh scale")
print("="*78)

# Sourced: multiple independent 2026 BESS pricing guides converge on
# Commercial & Industrial (100kWh-10MWh) tier = $200-350/kWh installed
# (CNTE, BSLBATT, AnengJi). Container-specific (1-2MWh, the closest match
# to our 1500kWh system): $195-235/kWh ex-works China, $255-295/kWh
# installed North America/Europe (CNTE container pricing note).
# Bangladesh-specific adjustment: zero import duty on BESS equipment was
# announced June 2026 (Bluesun/SREDA-adjacent reporting) -- this should
# keep landed BD cost closer to ex-works China than installed NA/EU,
# though local EPC/logistics still adds some premium over pure ex-works.
USD_TO_BDT = 123.3  # Xe mid-market, verified live today

battery_low_usd = 220   # near ex-works China + light BD logistics premium
battery_mid_usd = 250   # working midpoint
battery_high_usd = 300  # toward installed-market pricing, conservative

for label, usd in [("Low estimate", battery_low_usd), ("Working midpoint", battery_mid_usd), ("High estimate", battery_high_usd)]:
    tk = usd * USD_TO_BDT
    print(f"{label}: ${usd}/kWh -> Tk{tk:,.0f}/kWh")

print(f"\nOriginal placeholder assumption (from the earlier session, sized for a")
print(f"small residential/poultry battery): Tk25,000/kWh (${25000/USD_TO_BDT:.0f}/kWh)")
print("Verdict: the placeholder was NOT too high for this scale, as I'd assumed --")
print("it sits at or BELOW the real C&I-tier range. If anything it's optimistic.")

print("\n" + "-"*78)
print("Recomputed cold-storage EMI at the REAL, researched battery cost")
print("-"*78)

def calc_emi(principal, apr_pct, years):
    r = (apr_pct/100)/12
    n = round(years*12)
    if n <= 0: return 0
    if r == 0: return principal/n
    p = (1+r)**n
    return principal*r*p/(p-1)

SOLAR_COST = 100*1000*85  # 100kW @ Tk85/W, unchanged from mitigation_calc.py
BATTERY_KWH = 1500
SAVINGS_1500KWH = 267177  # validated, unchanged

print(f"\nUsing the REAL working-midpoint battery cost (Tk{battery_mid_usd*USD_TO_BDT:,.0f}/kWh):")
battery_cost_real = BATTERY_KWH * battery_mid_usd * USD_TO_BDT
total_cost_real = SOLAR_COST + battery_cost_real
print(f"  Solar Tk{SOLAR_COST:,.0f} + Battery Tk{battery_cost_real:,.0f} = Tk{total_cost_real:,.0f} all-in")

for label, down, years, rate in [
    ("Green-refinance terms (15% down/10yr/5%) -- SREDA confirms 'solar cold storage' IS an eligible IDCOL sub-sector", 0.15, 10, 5),
    ("Standard commercial terms (20% down/7yr/12%)", 0.20, 7, 12),
]:
    principal = total_cost_real*(1-down)
    emi = calc_emi(principal, rate, years)
    coverage = SAVINGS_1500KWH/emi*100
    print(f"\n{label}")
    print(f"  All-in EMI: Tk{emi:,.0f}/mo  ->  coverage {coverage:.1f}%  (vs. headline claim of 349%)")

print("\n" + "-"*78)
print("New, positive finding: SREDA's own financing page lists 'solar cold")
print("storage' explicitly as an eligible IDCOL/green-refinance sub-sector --")
print("alongside other hybrid (solar+storage) categories like telecom BTS hybrid")
print("systems. This is real evidence the BATTERY portion of a solar-cold-storage")
print("system likely qualifies for the SAME concessional terms as the solar")
print("portion -- more optimistic than my earlier 'unconfirmed either way' caveat.")
print("(Source: sreda.gov.bd financing page. Not a line-item Tk/kWh confirmation,")
print("but a real, named-category signal from the regulator that administers this.)")

print("\n" + "="*78)
print("PART 2 -- RESIDENTIAL: SAM")
print("="*78)
print("Confirmed (2022 Bangladesh census, BBS, via Prothom Alo reporting):")
print("  Total households: 41,000,000 (up from 32.1M in 2011)")
print("  Average household size: 4.26 people")
print("  This essentially VALIDATES the earlier placeholder's 41-43M SAM base --")
print("  it was not a guess that needs correcting, it was already right.")
print()
print("What's still a real placeholder: what FRACTION of 41M is realistically an")
print("early addressable segment. One real data point: a May 2026 PDB tariff-slab")
print("restructuring proposal noted it would affect 35% of consumers, of which 23")
print("points are 'lower middle class, under 200 units/month' -- implying roughly")
print("12% of residential consumers use MORE than 200 units/month nationally.")
print("That's the roughest possible proxy for 'has a bill worth acting on' -- not")
print("a clean slab-distribution table, and I could not find one. Applying it:")
sam_household_base = 41_000_000
higher_consumption_share = 0.12
implied_upper_bound = sam_household_base * higher_consumption_share
print(f"  41M households x ~12% (>200 units/mo, rough proxy) = ~{implied_upper_bound:,.0f} households")
print(f"  Original placeholder SAM: 500,000 households = {500_000/implied_upper_bound*100:.1f}% of this rougher upper bound")
print("  -> 500,000 remains a defensible EARLY-YEARS slice of a much larger")
print("     plausible ceiling, not an overreach. This is the best I can do without")
print("     a real BBS/BERC slab-distribution table, which I could not locate.")

print("\n" + "="*78)
print("PART 3 -- RESIDENTIAL: CAC")
print("="*78)
INR_TO_BDT = 1.29  # Xe/Ria mid-market, verified live today
print("SolarSquare (India, same product category, comparable South Asian income")
print("and labor cost environment) runs its primary acquisition channel through a")
print("named referral-partner program ('SolarPro'): Rs 2,000/kW commission paid,")
print("no other CAC disclosed publicly.")
for kw in [3.0, 5.5, 8.0]:
    commission_inr = 2000 * kw
    commission_tk = commission_inr * INR_TO_BDT
    print(f"  {kw}kW system -> Rs{commission_inr:,.0f} referral commission -> Tk{commission_tk:,.0f}")
print(f"\nOriginal placeholder CAC: Tk4,000/customer.")
print("Even at the SMALLEST typical system size, the referral commission ALONE")
print("(before any marketing spend, sales ops, or onboarding cost) already exceeds")
print("the Tk4,000 placeholder for anything above a ~3.1kW system. Direction: same")
print("as poultry/cold storage pattern -- reconciling with real data moves cost up,")
print("not down. Global fintech CAC benchmarks ($1,450+ for SMB) aren't directly")
print("transferable (BD digital ad/labor costs are much lower), so they're not used")
print("as the anchor here -- the India solar-specific referral model is the better")
print("comp since it's the same product, adjacent market, similar income level.")
