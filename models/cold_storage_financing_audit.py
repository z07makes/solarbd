"""
Cold storage — battery cost / EMI consistency audit.

QUESTION: SEGMENTS.coldstorage's EMI (Tk76,632/month) is used, unchanged,
against BOTH the 0kWh-battery savings figure (Tk100,602 -> 131%) AND the
1500kWh-battery savings figure (Tk267,177 -> 349%) throughout every version
of the platform prototype. Does Tk76,632 actually finance a system that
includes a 1500kWh battery, or only the solar?

METHOD: reconstruct which system size + financing terms produce exactly
Tk76,632/month (using the project's own calc_emi formula, unchanged from
sme_calc.py/mitigation_calc.py/the HTML calculators), then check whether
adding the 1500kWh battery's own cost -- at the project's own established
Tk25,000/kWh assumption (dispatch-engine.js's BATTERY_COST_PER_KWH, also
used to correctly cost poultry's battery into ITS EMI in sme_calc.py) --
changes that answer.
"""

BATTERY_COST_PER_KWH = 25000
SOLAR_COST = 100 * 1000 * 85  # 100kW @ Tk85/W -- sme_calc.py / mitigation_calc.py
CURRENT_EMI = 76632
DOCUMENTED_SAVINGS = {0: 100602, 500: 158362, 1000: 216122, 1500: 267177}


def calc_emi(principal, apr_pct, years):
    r = (apr_pct / 100) / 12
    n = round(years * 12)
    if n <= 0:
        return 0
    if r == 0:
        return principal / n
    p = (1 + r) ** n
    return principal * r * p / (p - 1)


print("=" * 78)
print("STEP 1 -- what system does the current Tk76,632 EMI actually finance?")
print("=" * 78)
solar_only_principal = SOLAR_COST * 0.85
solar_only_emi = calc_emi(solar_only_principal, 5, 10)  # green-refinance terms, mitigation_calc.py's cold-storage lever
print(f"100kW solar-ONLY system (Tk{SOLAR_COST:,.0f}), 15% down / 10yr / 5% APR (green refinance):")
print(f"  -> recomputed EMI = Tk{solar_only_emi:,.0f}/mo")
print(f"  -> EMI used everywhere in the demo for this segment: Tk{CURRENT_EMI:,.0f}/mo")
match = abs(solar_only_emi - CURRENT_EMI) < 300
print(f"  -> {'MATCHES' if match else 'does NOT match'} -- confirms the Tk76,632 EMI is SOLAR-ONLY,")
print(f"     the battery's own cost was never added to it.")

print("\n" + "=" * 78)
print("STEP 2 -- what happens once each battery size's OWN cost is honestly financed")
print("=" * 78)
print("(same 15%-down / 10yr / 5%-APR terms applied to the FULL solar+battery cost)\n")
print(f"{'Battery':>9} {'Battery cost':>15} {'All-in EMI':>13} {'Sim. savings':>14} {'Coverage':>9}   Marginal vs previous size")
print("-" * 100)
prev_emi = None
prev_savings = None
for batt_kwh in [0, 500, 1000, 1500]:
    battery_cost = batt_kwh * BATTERY_COST_PER_KWH
    total_cost = SOLAR_COST + battery_cost
    principal = total_cost * 0.85
    emi = calc_emi(principal, 5, 10)
    savings = DOCUMENTED_SAVINGS[batt_kwh]
    coverage = savings / emi * 100
    marginal = ""
    if prev_emi is not None:
        d_emi = emi - prev_emi
        d_savings = savings - prev_savings
        verdict = "net gain" if d_savings > d_emi else "net LOSS"
        marginal = f"+Tk{d_emi:,.0f} EMI for +Tk{d_savings:,.0f} savings -> {verdict} of Tk{abs(d_savings - d_emi):,.0f}/mo"
    print(f"{batt_kwh:>7}kWh {battery_cost:>15,.0f} {emi:>13,.0f} {savings:>14,.0f} {coverage:>8.1f}%   {marginal}")
    prev_emi, prev_savings = emi, savings

print("\n" + "=" * 78)
print("STEP 3 -- the headline '349%' figure under alternate financing assumptions")
print("=" * 78)
total_cost_1500 = SOLAR_COST + 1500 * BATTERY_COST_PER_KWH
print(f"All-in system cost at 1500kWh: Tk{total_cost_1500:,.0f} (solar Tk{SOLAR_COST:,.0f} + battery Tk{1500*BATTERY_COST_PER_KWH:,.0f})\n")
for label, down, years, rate in [
    ("Green-refinance terms on everything (15% down / 10yr / 5%)", 0.15, 10, 5),
    ("Standard commercial terms on everything (20% down / 7yr / 12%)", 0.20, 7, 12),
]:
    principal = total_cost_1500 * (1 - down)
    emi = calc_emi(principal, rate, years)
    coverage = DOCUMENTED_SAVINGS[1500] / emi * 100
    print(f"{label}")
    print(f"  -> all-in EMI Tk{emi:,.0f}/mo  ->  coverage {coverage:.1f}%   (headline claim: 349%)\n")

battery_principal = (1500 * BATTERY_COST_PER_KWH) * 0.80
battery_emi = calc_emi(battery_principal, 12, 7)
blended_emi = solar_only_emi + battery_emi
blended_coverage = DOCUMENTED_SAVINGS[1500] / blended_emi * 100
print("Blended (solar keeps green-refinance terms as today; battery financed at standard")
print("commercial terms, since battery-storage eligibility for the green window is unconfirmed):")
print(f"  -> Tk{solar_only_emi:,.0f} (solar) + Tk{battery_emi:,.0f} (battery) = Tk{blended_emi:,.0f}/mo")
print(f"  -> coverage {blended_coverage:.1f}%   (headline claim: 349%)")

print("\n" + "=" * 78)
print("CAVEATS -- read before treating any of this as final")
print("=" * 78)
print("- Tk25,000/kWh was set for a small residential/poultry battery. A 1500kWh")
print("  UTILITY-SCALE battery very plausibly costs meaningfully less per kWh")
print("  (BOS/inverter/labor cost amortizes across more capacity) -- a real vendor")
print("  quote at THIS scale would change every number above and should be sourced")
print("  before any of this is treated as final. This audit does not have one.")
print("- This is a pure ARBITRAGE-economics lens. It excludes resilience/outage-")
print("  avoidance value (avoided spoilage), which sme_calc.py separately argues")
print("  can be very large for cold storage and doesn't depend on the TOU spread")
print("  at all -- a large battery may still be justified on THAT basis even where")
print("  arbitrage alone doesn't clear an honestly-financed EMI.")
print("- Whether battery storage itself qualifies for the same green-refinance")
print("  window as solar panels in Bangladesh is not confirmed either way in")
print("  anything reviewed so far in this project -- flagged as a research item,")
print("  not assumed.")
print("- This is scenario modelling with stated, swappable assumptions -- not")
print("  financial or investment advice.")
