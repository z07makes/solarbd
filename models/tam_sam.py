"""
Sprint B: TAM / SAM sizing for poultry + cold storage specifically.
SOM (realistic capture) is deliberately left for Sprint D, which needs
growth-curve reasoning, not just a market-size number.
"""
FX = 122  # illustrative Tk/USD, flagged - verify current rate before external use

print("="*70)
print("POULTRY — TAM / SAM")
print("="*70)
TOTAL_FARMS = 100_000          # sourced range (60k broiler/23k layer/13k Sonali); older sources ~150k
SYSTEM_COST_LOW = 410_000      # mitigated (EC fans + green refinance-eligible + right-sized battery)
SYSTEM_COST_HIGH = 535_000     # baseline (whole-shed backup, unmitigated)

tam_low = TOTAL_FARMS * SYSTEM_COST_LOW
tam_high = TOTAL_FARMS * SYSTEM_COST_HIGH
print(f"TAM (all 100,000 commercial farms, full system value):")
print(f"  Tk {tam_low/1e9:.1f}B - Tk {tam_high/1e9:.1f}B  (${tam_low/FX/1e6:.0f}M - ${tam_high/FX/1e6:.0f}M)")

# SAM: exclude farms too small/informal to be grid-tied+bankable. No clean
# BD-specific size-distribution source exists - using a flagged, reasoned
# filter: contract-farmed/integrator-linked (17-19%) are the most immediately
# reachable and creditworthy; independents need individual assessment.
# Treating SAM conservatively as ~55% of TAM (integrator-linked + the better-
# capitalized share of independents) - EXPLICITLY an estimate, not sourced.
SAM_FRACTION = 0.55
sam_low, sam_high = tam_low*SAM_FRACTION, tam_high*SAM_FRACTION
sam_farms = TOTAL_FARMS*SAM_FRACTION
print(f"\nSAM (grid-tied, bankable-scale farms - ESTIMATED at {SAM_FRACTION:.0%} of TAM, not sourced):")
print(f"  ~{sam_farms:,.0f} farms -> Tk {sam_low/1e9:.1f}B - Tk {sam_high/1e9:.1f}B (${sam_low/FX/1e6:.0f}M-${sam_high/FX/1e6:.0f}M)")

print(f"\nGeographic beachhead check: 53.3% Dhaka division / 24% Gazipur alone")
print(f"  -> Gazipur-only SAM: ~{sam_farms*0.24:,.0f} farms -> Tk {sam_low*0.24/1e9:.2f}B (${sam_low*0.24/FX/1e6:.0f}M)")
print(f"  -> Dhaka-division SAM: ~{sam_farms*0.533:,.0f} farms -> Tk {sam_low*0.533/1e9:.2f}B (${sam_low*0.533/FX/1e6:.0f}M)")

print("\n" + "="*70)
print("COLD STORAGE — TAM / SAM")
print("="*70)
# Updated to more recent (2025) figure: 365 facilities, 32 lakh tonnes (3.2M MT)
# combined capacity - supersedes the older 400-facility/6M-MT figure used in
# Part 1; both are shown for transparency.
FACILITIES_2025 = 365
CAPACITY_2025_MT = 3_200_000
avg_tonnage = CAPACITY_2025_MT / FACILITIES_2025
print(f"Facility count (2025 source): {FACILITIES_2025}, avg tonnage: {avg_tonnage:,.0f} MT")
print(f"(Older 2024 source cited 400 facilities / 6M MT -- shown for range, not used as primary)")

# Cost scaling from the Sprint 2 model (100kW/Tk8.5M @ 3,000MT), scaled
# roughly linearly with tonnage - an approximation, flagged, since real
# system size depends on roof area/footprint more than tonnage precisely.
COST_PER_TONNE_BASIS = 8_500_000 / 3000  # Tk per tonne of storage, from the 100kW example
facility_cost_avg = avg_tonnage * COST_PER_TONNE_BASIS
tam_cs = FACILITIES_2025 * facility_cost_avg
print(f"\nModeled system cost at average facility size: Tk {facility_cost_avg/1e6:.1f}M/facility")
print(f"TAM (all {FACILITIES_2025} facilities, solar-only system value): Tk {tam_cs/1e9:.1f}B (${tam_cs/FX/1e6:.0f}M)")
print("NOTE: VFD/efficiency-retrofit TAM is NOT included above - sourced")
print("      savings (10-35%) are solid, but no reliable BD-specific VFD")
print("      capex figure was found; needs real vendor quotes before costing.")

# SAM: ~300/365 (~82%) are loan-distressed per Sprint 1/2 research - meaning
# they need PACKAGED financing (not cash-purchase) to be reachable, which is
# our model anyway, so this doesn't shrink SAM - but facilities that are
# ALREADY in default/insolvency proceedings would not be creditworthy even
# for referral. No clean source on how many of the 300 are that far gone -
# treating SAM as 100% of TAM here (all are grid-connected, all are the
# right customer type) MINUS a flagged 15% for facilities too distressed to
# finance at all (an estimate, not sourced).
sam_cs = tam_cs * 0.85
print(f"\nSAM (excl. ~15% assumed too financially distressed to finance - ESTIMATE): Tk {sam_cs/1e9:.1f}B (${sam_cs/FX/1e6:.0f}M)")

print("\n" + "="*70)
print("COMBINED TWO-SEGMENT MARKET SIZE (solar-only system value, hardware+financing)")
print("="*70)
print(f"Poultry TAM:      Tk {tam_low/1e9:.1f}-{tam_high/1e9:.1f}B")
print(f"Cold storage TAM: Tk {tam_cs/1e9:.1f}B")
print(f"Combined TAM:     Tk {(tam_low+tam_cs)/1e9:.1f}-{(tam_high+tam_cs)/1e9:.1f}B (${(tam_low+tam_cs)/FX/1e6:.0f}M-${(tam_high+tam_cs)/FX/1e6:.0f}M)")
