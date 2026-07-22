"""
Sprint A: quantifying mitigation levers against the poultry & cold storage
gaps found in Sprint 2. Reuses the verified engine from sme_calc.py.
"""
def calc_emi(principal, apr_pct, years):
    r = (apr_pct/100)/12
    n = round(years*12)
    if n<=0: return 0
    if r==0: return principal/n
    p=(1+r)**n
    return principal*r*p/(p-1)

PEAK_SUN = {"dry":5.2,"average":4.3,"monsoon":3.3}
DERATE=0.8; DAYS=30.4
def gen_units(kw,sun): return kw*sun*DAYS*DERATE
COM_RATE=15.36

print("="*70)
print("POULTRY — stacking mitigations one at a time, 2,000-bird shed")
print("="*70)
# Baseline (from Sprint 2)
base_cost=535000
base_monthly_kwh=985
sun=PEAK_SUN["average"]

def run_poultry(cost, monthly_kwh, kw_solar, down_pct, tenure, rate, label):
    principal=cost*(1-down_pct/100)
    emi=calc_emi(principal, rate, tenure)
    gen=gen_units(kw_solar, sun)
    self_use=min(gen, monthly_kwh)
    savings=self_use*COM_RATE
    print(f"{label:55s} EMI=Tk{emi:7,.0f}  Savings=Tk{savings:6,.0f}  Net={savings-emi:+8,.0f}")
    return emi, savings

print("\n-- Lever 0: baseline (commercial personal-loan terms, 15% down/6yr/11%) --")
run_poultry(535000, 985, 3.0, 15, 6, 11, "Baseline")

print("\n-- Lever 1: ONLY switch financing to BB green refinance (agri-linked, 3%, 8yr, 10% down) --")
run_poultry(535000, 985, 3.0, 10, 8, 3, "Green refinance only")

print("\n-- Lever 2: ONLY retrofit to EC fans first (cuts fan-share of load ~50%,")
print("   fans are ~70% of the 985kWh baseline per sourced load breakdown) --")
fan_share=0.70
new_monthly_kwh = base_monthly_kwh*(1-fan_share*0.50)  # 50% cut applied to the fan portion only
print(f"   New monthly consumption after EC retrofit: {new_monthly_kwh:.0f} kWh (was {base_monthly_kwh})")
run_poultry(535000, new_monthly_kwh, 3.0, 15, 6, 11, "EC fans only (financing unchanged)")

print("\n-- Lever 3: COMBINED — EC fans + green refinance + right-sized critical-load battery --")
# right-sizing: only back up the fan circuit (~1.2kW heat-event, not 2.1kW whole-shed) for 4h -> ~5kWh not 10kWh
smaller_battery_kwh=5.0
battery_cost = smaller_battery_kwh*25000
solar_cost = 3.0*1000*95
combined_cost = solar_cost + battery_cost
ec_fan_premium = 1.75*  (0.0)  # placeholder, computed below properly
print(f"   Combined system cost (solar Tk{solar_cost:,.0f} + right-sized {smaller_battery_kwh}kWh battery Tk{battery_cost:,.0f}) = Tk{combined_cost:,.0f}")
# EC fan capex premium: fans are a small line item (a few hundred dollars per fan, a few fans per shed)
# — modeled as a modest incremental Tk15,000 addition, clearly flagged as illustrative
ec_capex_addon = 15000
combined_cost_with_ec = combined_cost + ec_capex_addon
emi_c, sav_c = run_poultry(combined_cost_with_ec, new_monthly_kwh, 3.0, 10, 8, 3,
                            "EC fans + green refinance + right-sized battery")
print(f"\n   -> Net swings from Tk-3,837/month (baseline) to Tk{sav_c-emi_c:+,.0f}/month (combined)")
print(f"   -> Battery still only rides ~{smaller_battery_kwh/1.2:.1f}h of critical-fan-only heat-event load")
print(f"      (down from whole-shed 4.8h — a deliberate trade: less total backup, but bill-savings now clears)")

print("\n" + "="*70)
print("Poultry — EC fans' DIRECT bill effect (independent of solar)")
print("="*70)
bill_before = 985*COM_RATE
bill_after = 640*COM_RATE
print(f"Bill before EC retrofit (985 kWh): Tk{bill_before:,.0f}/month")
print(f"Bill after EC retrofit (640 kWh):  Tk{bill_after:,.0f}/month")
print(f"Direct saving from efficiency alone, no solar involved: Tk{bill_before-bill_after:,.0f}/month")

print("\n" + "="*70)
print("COLD STORAGE — stacking mitigations, 3,000-tonne facility")
print("="*70)
annual_kwh=2_400_000
PEAK_RATE, OFFPEAK_RATE = 13.62, 9.62

def cs_scenario(kw_solar, vfd_cut_pct, down, tenure, rate, cost_per_watt, label):
    load_after_vfd = annual_kwh*(1-vfd_cut_pct)
    monthly_kwh = load_after_vfd/12
    gen = gen_units(kw_solar, PEAK_SUN["average"])
    self_use = min(gen, monthly_kwh)
    savings = self_use*OFFPEAK_RATE
    cost = kw_solar*1000*cost_per_watt
    principal = cost*(1-down/100)
    emi = calc_emi(principal, rate, tenure)
    print(f"{label}")
    print(f"   Annual load after VFD: {load_after_vfd:,.0f} kWh | System: {kw_solar}kW @ Tk{cost_per_watt}/W = Tk{cost:,.0f}")
    print(f"   EMI=Tk{emi:,.0f}  Solar savings=Tk{savings:,.0f}  Net(solar only)={savings-emi:+,.0f}")
    return emi, savings, monthly_kwh

print("\n-- Baseline (100kW, commercial terms 20%/7yr/12%, no VFD) --")
cs_scenario(100, 0.0, 20, 7, 12, 85, "Baseline")

print("\n-- Lever 1: green refinance only (5%, 10yr, 15% down) --")
cs_scenario(100, 0.0, 15, 10, 5, 85, "Green refinance only")

print("\n-- Lever 2: VFD retrofit only (20% cut, mid-point of sourced 10-35% range) --")
emi2, sav2, mkwh2 = cs_scenario(100, 0.20, 20, 7, 12, 85, "VFD retrofit only")

print("\n-- Lever 3: COMBINED — VFD + green refinance + peak-shaving battery added --")
emi3, sav3, mkwh3 = cs_scenario(100, 0.20, 15, 10, 5, 85, "VFD + green refinance")
# peak-shaving value recomputed on the POST-VFD load
avg_load_kw_after_vfd = (mkwh3*12)/8760
peak_kwh_day = avg_load_kw_after_vfd*5
peak_shave_month = peak_kwh_day*(PEAK_RATE-OFFPEAK_RATE)*DAYS
print(f"   + peak-shaving value on reduced load: Tk{peak_shave_month:,.0f}/month")
total_value = sav3 + peak_shave_month
print(f"   TOTAL monthly value (solar offset + peak-shaving) = Tk{total_value:,.0f}")
print(f"   vs EMI Tk{emi3:,.0f}  ->  Net = Tk{total_value-emi3:+,.0f}/month")

print("\n-- VFD direct bill effect, independent of solar --")
bill_before_cs = annual_kwh/12 * ((5/24)*PEAK_RATE + (19/24)*OFFPEAK_RATE)
bill_after_cs = (annual_kwh*0.8)/12 * ((5/24)*PEAK_RATE + (19/24)*OFFPEAK_RATE)
print(f"Monthly bill before VFD: Tk{bill_before_cs:,.0f}")
print(f"Monthly bill after VFD (20% cut): Tk{bill_after_cs:,.0f}")
print(f"Direct saving from VFD alone: Tk{bill_before_cs-bill_after_cs:,.0f}/month")
