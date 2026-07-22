"""
SME-specific financial models: poultry broiler shed + cold storage facility.
Built on the same tariff/EMI engine as the residential/commercial calculator,
with load profiles grounded in sourced engineering data (see inline notes).
All assumptions are labeled; nothing here is invented without a stated basis.
"""

# ---------- shared EMI engine (same as HTML calculator, verified earlier) ----------
def calc_emi(principal, apr_pct, years):
    r = (apr_pct / 100) / 12
    n = round(years * 12)
    if n <= 0:
        return 0
    if r == 0:
        return principal / n
    p = (1 + r) ** n
    return principal * r * p / (p - 1)

PEAK_SUN = {"dry": 5.2, "average": 4.3, "monsoon": 3.3}
DERATE = 0.8
DAYS = 30.4

def gen_units(kw, sun_hrs):
    return kw * sun_hrs * DAYS * DERATE

# =====================================================================
# POULTRY MODEL — 2,000-bird broiler shed (mid-point of BD's documented
# 500-2,500 bird typical commercial farm size)
# =====================================================================
# Load basis (sourced): Nigerian 500-2,000 bird commercial data shows peak
# simultaneous load of 2,000-3,000W during brooding (heat lamps+fans+lights
# together), dropping to 800-1,500W continuous outside brooding.
# A broiler cycle is ~35-42 days grow-out + ~10-14 days cleanout/downtime,
# giving roughly 6-7 flock cycles/year (standard industry knowledge).
# Brooding = first ~14 days of each cycle (heat lamps needed).
BROODING_LOAD_KW = 2.5      # midpoint of 2.0-3.0kW sourced range
NORMAL_LOAD_KW = 1.15       # midpoint of 0.8-1.5kW sourced range
HEAT_EVENT_LOAD_KW = 2.1    # modeled: max ventilation running during a heatwave
                            # (derived from CFM/kg engineering ratios showing summer
                            # peak ventilation is roughly double winter minimum -
                            # this figure is MY estimate scaled off sourced ratios,
                            # not a directly-sourced wattage, flagged accordingly)
BROODING_DAYS_PER_CYCLE = 14
GROWOUT_DAYS_PER_CYCLE = 28
CLEANOUT_DAYS = 10
CYCLE_DAYS = BROODING_DAYS_PER_CYCLE + GROWOUT_DAYS_PER_CYCLE + CLEANOUT_DAYS  # 52 days
CYCLES_PER_YEAR = 365 / CYCLE_DAYS

# Monthly energy: blend of brooding + normal grow-out days (heat-event days
# modeled separately as a stress-test, not baked into "normal" monthly kWh)
brooding_frac = BROODING_DAYS_PER_CYCLE / CYCLE_DAYS
growout_frac = GROWOUT_DAYS_PER_CYCLE / CYCLE_DAYS
cleanout_frac = CLEANOUT_DAYS / CYCLE_DAYS  # minimal load during cleanout, assume ~0.3kW (lighting/cleaning)
CLEANOUT_LOAD_KW = 0.3

avg_load_kw = (brooding_frac * BROODING_LOAD_KW +
               growout_frac * NORMAL_LOAD_KW +
               cleanout_frac * CLEANOUT_LOAD_KW)
monthly_kwh_poultry = avg_load_kw * 24 * DAYS

print("=== POULTRY: 2,000-bird broiler shed ===")
print(f"Cycle length: {CYCLE_DAYS} days -> {CYCLES_PER_YEAR:.1f} flocks/year")
print(f"Blended average load: {avg_load_kw:.2f} kW")
print(f"Modeled monthly consumption: {monthly_kwh_poultry:.0f} kWh")

# System sizing: solar sized to cover the NORMAL continuous load through
# daylight hours + charge a battery big enough to ride through an evening/
# night outage at HEAT-EVENT load (the reliability-first design principle
# from Sprint 1 - size for the worst case, not the average).
POULTRY_SOLAR_KW = 3.0
POULTRY_BATTERY_KWH = 10.0   # sized so HEAT_EVENT_LOAD_KW (2.1kW) can run ~4.5-5h on battery alone
hours_of_backup_at_heat_load = POULTRY_BATTERY_KWH / HEAT_EVENT_LOAD_KW
print(f"Proposed system: {POULTRY_SOLAR_KW}kW solar + {POULTRY_BATTERY_KWH}kWh battery")
print(f"-> battery alone rides through {hours_of_backup_at_heat_load:.1f}h of a heat-event-level outage")

# Cost (using the same Tk/watt bands as the calculator, but poultry sheds
# add a smaller inverter/BOS premium per kW since it's a small system —
# using the same 70-120 Tk/watt band, mid-point 95 to reflect small-system
# premium)
POULTRY_COST_PER_WATT = 95
poultry_total_cost = POULTRY_SOLAR_KW * 1000 * POULTRY_COST_PER_WATT
# battery cost separately - LiFePO4 typically runs higher per kWh than the
# panel cost/watt figure covers; using a illustrative Tk 25,000/kWh (flagged
# as an estimate - varies hugely by brand/import duty)
BATTERY_COST_PER_KWH = 25000
battery_cost = POULTRY_BATTERY_KWH * BATTERY_COST_PER_KWH
poultry_total_cost_with_battery = poultry_total_cost + battery_cost
print(f"System cost: solar Tk{poultry_total_cost:,.0f} + battery Tk{battery_cost:,.0f} = Tk{poultry_total_cost_with_battery:,.0f}")

# Assume commercial flat tariff (15.36 Tk/unit) as the default connection
# type for a poultry shed - FLAGGED: actual agricultural/commercial tariff
# classification should be verified per-DISCO, this is the closest
# confirmed rate we have.
COM_RATE = 15.36
gen_avg = gen_units(POULTRY_SOLAR_KW, PEAK_SUN["average"])
gen_dry = gen_units(POULTRY_SOLAR_KW, PEAK_SUN["dry"])
gen_monsoon = gen_units(POULTRY_SOLAR_KW, PEAK_SUN["monsoon"])
self_use_avg = min(gen_avg, monthly_kwh_poultry)
self_use_dry = min(gen_dry, monthly_kwh_poultry)
self_use_monsoon = min(gen_monsoon, monthly_kwh_poultry)
savings_avg = self_use_avg * COM_RATE
savings_dry = self_use_dry * COM_RATE
savings_monsoon = self_use_monsoon * COM_RATE
print(f"Generation avg/dry/monsoon: {gen_avg:.0f}/{gen_dry:.0f}/{gen_monsoon:.0f} kWh")
print(f"Savings avg/dry/monsoon: Tk{savings_avg:,.0f}/{savings_dry:,.0f}/{savings_monsoon:,.0f}")

# EMI at same default terms as before (15% down, 6yr, 11% APR)
down_pct, tenure, rate = 15, 6, 11
principal = poultry_total_cost_with_battery * (1 - down_pct/100)
emi = calc_emi(principal, rate, tenure)
print(f"Principal: Tk{principal:,.0f} | EMI: Tk{emi:,.0f}/mo")
print(f"Net avg: {savings_avg-emi:+,.0f} | Net dry: {savings_dry-emi:+,.0f} | Net monsoon: {savings_monsoon-emi:+,.0f}")
annual_savings_est = (savings_avg * 12)  # rough, refine with monthly curve below
payback = poultry_total_cost_with_battery / annual_savings_est if annual_savings_est>0 else float('inf')
print(f"Simple payback (rough): {payback:.1f} years")

print("\n" + "="*60)
print("POULTRY: reframing around avoided-loss, not bill savings")
print("="*60)
# Broiler market weight ~2.2kg (standard), farm-gate price volatile
# Tk120-230/kg over 2026 (sourced range) - using Tk180/kg as a conservative
# mid-point, clearly flagged as volatile, not fixed.
BIRD_COUNT = 2000
MARKET_WEIGHT_KG = 2.2
FARMGATE_PRICE_LOW, FARMGATE_PRICE_MID, FARMGATE_PRICE_HIGH = 120, 180, 230

full_flock_value_mid = BIRD_COUNT * MARKET_WEIGHT_KG * FARMGATE_PRICE_MID
for mortality_pct in [0.10, 0.15, 0.25, 0.50]:
    birds_lost = BIRD_COUNT * mortality_pct
    loss_value = birds_lost * MARKET_WEIGHT_KG * FARMGATE_PRICE_MID
    months_of_emi_covered = loss_value / emi
    print(f"{mortality_pct*100:.0f}% mortality event ({birds_lost:.0f} birds): "
          f"Tk{loss_value:,.0f} lost -> covers {months_of_emi_covered:.1f} months of EMI")

print(f"\nFull flock value at risk (2,000 birds, Tk180/kg): Tk{full_flock_value_mid:,.0f}")
print(f"That's {full_flock_value_mid/emi:.0f} months of EMI in ONE flock, if a total loss event happened at market weight")
print("Documented reference case: a Narayanganj farmer reported 500+ birds dead")
print("from heatstroke in two sheds during load-shedding, April 2024 (The Business Standard)")

# =====================================================================
# COLD STORAGE MODEL — 3,000-tonne potato facility (mid-size, matches
# the "Project Profile Bangladesh" investment example used for cross-check)
# =====================================================================
print("\n" + "="*60)
print("COLD STORAGE: 3,000-tonne potato facility")
print("="*60)
STORAGE_TONNES = 3000
# Energy intensity: 560-700 kWh/tonne/year is the "efficient" benchmark
# (Rinac industry source). BD facilities are largely older ammonia plants,
# not VFD-optimized - using 800 kWh/tonne/year as a "typical, not yet
# efficient" estimate, ABOVE the efficient benchmark, clearly flagged.
KWH_PER_TONNE_YEAR = 800
annual_kwh_coldstorage = STORAGE_TONNES * KWH_PER_TONNE_YEAR
monthly_kwh_coldstorage = annual_kwh_coldstorage / 12
avg_load_kw_coldstorage = annual_kwh_coldstorage / 8760  # kW, spread over full year continuous
print(f"Annual consumption: {annual_kwh_coldstorage:,.0f} kWh ({monthly_kwh_coldstorage:,.0f} kWh/month avg)")
print(f"Average continuous load: {avg_load_kw_coldstorage:.1f} kW (runs ~18-24h/day per BD sources)")

# Real sourced tariff: Tk 13.62/unit peak, Tk 9.62/unit off-peak (BCSA, 2025)
# Assume ~5h/day peak window (evening), ~19h/day off-peak, to build a
# blended rate - this split is MY assumption, tariff figures are sourced.
PEAK_RATE, OFFPEAK_RATE = 13.62, 9.62
peak_hours_frac, offpeak_hours_frac = 5/24, 19/24
blended_rate = peak_hours_frac*PEAK_RATE + offpeak_hours_frac*OFFPEAK_RATE
print(f"Blended tariff (5h peak/19h off-peak assumption): Tk{blended_rate:.2f}/unit")
current_annual_bill = annual_kwh_coldstorage * blended_rate
print(f"Estimated current annual electricity bill: Tk{current_annual_bill:,.0f}")

# Solar+battery can only realistically offset the DAYTIME portion of a
# near-continuous industrial load - this is the key honest constraint for
# this segment (unlike poultry/residential, cold storage runs 24h so solar
# can only ever cover part of it without a very large, costly battery).
COLDSTORAGE_SOLAR_KW = 100  # illustrative - roof/land-constrained industrial system
gen_avg_cs = gen_units(COLDSTORAGE_SOLAR_KW, PEAK_SUN["average"])
gen_dry_cs = gen_units(COLDSTORAGE_SOLAR_KW, PEAK_SUN["dry"])
gen_monsoon_cs = gen_units(COLDSTORAGE_SOLAR_KW, PEAK_SUN["monsoon"])
# Self-use capped at monthly consumption (won't exceed, given monthly load >> generation here)
self_use_avg_cs = min(gen_avg_cs, monthly_kwh_coldstorage)
# Solar generation displaces DAYTIME grid draw, which for cold storage is
# mostly off-peak-rate hours (daytime isn't necessarily "peak" under a
# peak=evening tariff) - so value it at the off-peak rate, conservatively.
savings_avg_cs = self_use_avg_cs * OFFPEAK_RATE
pct_of_bill_offset = (self_use_avg_cs*12) / annual_kwh_coldstorage * 100
print(f"\n100kW solar generation (avg month): {gen_avg_cs:,.0f} kWh")
print(f"-> offsets {pct_of_bill_offset:.1f}% of the facility's total annual consumption")
print(f"Monthly savings (valued at off-peak rate, conservative): Tk{savings_avg_cs:,.0f}")

cs_cost_per_watt = 85  # larger system, some economy of scale vs residential/poultry bands
cs_total_cost = COLDSTORAGE_SOLAR_KW*1000*cs_cost_per_watt
cs_down, cs_tenure, cs_rate = 20, 7, 12
cs_principal = cs_total_cost*(1-cs_down/100)
cs_emi = calc_emi(cs_principal, cs_rate, cs_tenure)
print(f"System cost (solar only, no battery - see note): Tk{cs_total_cost:,.0f}")
print(f"EMI (20% down, 7yr, 12%): Tk{cs_emi:,.0f}/mo | Monthly savings: Tk{savings_avg_cs:,.0f} | Net: {savings_avg_cs-cs_emi:+,.0f}")

print("\n" + "="*60)
print("COLD STORAGE: sensitivity + the real value driver")
print("="*60)
# Sensitivity: conservative vs roof-maximized system size
for kw in [100, 250, 400]:
    gen = gen_units(kw, PEAK_SUN["average"])
    pct = (gen*12) / annual_kwh_coldstorage * 100
    print(f"{kw}kW system -> {gen:,.0f} kWh/mo avg -> offsets {pct:.1f}% of annual load")
print("-> Even a large, roof-maximized system only dents a fraction of the load,")
print("   because compressors run 18-24h/day - a load with no strong day/night")
print("   shape, unlike poultry or residential. Pure kWh-offset is the wrong pitch here.")

# Peak-shaving value: what if a battery is used to avoid ONLY the peak-rate
# hours (5h/day @ Tk13.62), sourced from solar/battery instead, vs off-peak
# rate the grid would otherwise charge for that energy anyway overnight
peak_kwh_per_day = avg_load_kw_coldstorage * 5  # continuous load x 5 peak hours
peak_shave_daily_value = peak_kwh_per_day * (PEAK_RATE - OFFPEAK_RATE)
peak_shave_monthly_value = peak_shave_daily_value * DAYS
print(f"\nPeak-shaving only (shift {peak_kwh_per_day:.0f} kWh/day out of peak-rate hours):")
print(f"Value = rate spread (Tk{PEAK_RATE-OFFPEAK_RATE:.2f}/unit) x volume = Tk{peak_shave_monthly_value:,.0f}/month")
print("-> This is a battery-dispatch/software optimization problem, separate from")
print("   solar generation - the 'smart switching' layer earns its keep here even")
print("   in a segment where solar offset alone is weak.")

# Avoided-spoilage-loss framing, scaled from the real 2023 documented case:
# a 10,000-tonne facility lost Tk1.5-2 crore from reduced capacity during
# sustained power cuts (The Daily Star, June 2023). Scaling linearly to our
# 3,000-tonne example (a simplification - real losses aren't perfectly linear,
# flagged):
DOCUMENTED_LOSS_LOW, DOCUMENTED_LOSS_HIGH = 15_000_000, 20_000_000  # Tk1.5-2 crore
DOCUMENTED_FACILITY_SIZE = 10000
scaled_loss_low = DOCUMENTED_LOSS_LOW * (STORAGE_TONNES/DOCUMENTED_FACILITY_SIZE)
scaled_loss_high = DOCUMENTED_LOSS_HIGH * (STORAGE_TONNES/DOCUMENTED_FACILITY_SIZE)
print(f"\nDocumented case (Daily Star, 2023): a 10,000-tonne facility lost Tk1.5-2 crore")
print(f"from a single sustained power-cut event's impact on stored-potato capacity/quality.")
print(f"Scaled (linearly, illustratively) to our 3,000-tonne facility: Tk{scaled_loss_low:,.0f}-{scaled_loss_high:,.0f}")
print(f"-> covers {scaled_loss_low/cs_emi:.0f}-{scaled_loss_high/cs_emi:.0f} months of the solar EMI in a single avoided event")
