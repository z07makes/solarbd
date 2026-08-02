import dispatch_engine as de

def calc_emi(principal, apr_pct, years):
    r = (apr_pct/100)/12
    n = round(years*12)
    if n <= 0: return 0
    if r == 0: return principal/n
    p = (1+r)**n
    return principal*r*p/(p-1)

print("="*76)
print("Which system does the Tk4,487 poultry EMI actually price?")
print("="*76)

# Candidate: mitigation_calc.py's "Lever 3: COMBINED" -- 3.0kW solar + 5kWh
# right-sized battery + EC-fan capex, at green-refinance terms
solar_3kw = 3.0*1000*95
battery_5kwh = 5.0*25000
ec_addon = 15000
total_3kw5kwh = solar_3kw + battery_5kwh + ec_addon
emi_3kw5kwh = calc_emi(total_3kw5kwh*0.90, 3, 8)
print(f"3.0kW solar + 5kWh battery + EC fans, green-refinance (10%/8yr/3%):")
print(f"  cost Tk{total_3kw5kwh:,.0f} -> EMI Tk{emi_3kw5kwh:,.0f}/mo  (documented: Tk4,487) "
      f"{'MATCH' if abs(emi_3kw5kwh-4487)<10 else 'no match'}")

# But the dispatch engine's validated Test F config -- the one that actually
# PRODUCES the Tk4,824 savings figure -- uses a much smaller system
solar_actual = 1.36*1000*95
battery_actual = 2.4*25000
total_actual = solar_actual + battery_actual
emi_actual_green = calc_emi(total_actual*0.90, 3, 8)
emi_actual_comm = calc_emi(total_actual*0.85, 11, 6)
print(f"\nBut Test F's actual simulated config is 1.36kW solar + 2.4kWh battery:")
print(f"  cost Tk{total_actual:,.0f} -> EMI at green terms: Tk{emi_actual_green:,.0f}/mo")
print(f"  cost Tk{total_actual:,.0f} -> EMI at standard commercial terms: Tk{emi_actual_comm:,.0f}/mo")

print("\n" + "="*76)
print("Reconciled coverage, using the EMI that actually matches the simulated system")
print("="*76)
savings = 4823.64  # validated, see validate.py
print(f"Currently shown: Tk{savings:,.2f} savings / Tk4,487 EMI (size-MISMATCHED) = {savings/4487*100:.1f}%")
print(f"Size-matched, green terms:      Tk{savings:,.2f} / Tk{emi_actual_green:,.0f} = {savings/emi_actual_green*100:.1f}%")
print(f"Size-matched, commercial terms: Tk{savings:,.2f} / Tk{emi_actual_comm:,.0f} = {savings/emi_actual_comm*100:.1f}%")

print("\n" + "="*76)
print("Other direction: what would the LARGER 3.0kW/5kWh system actually save,")
print("run for real through the engine (not assumed)?")
print("="*76)

cfg = dict(battery_capacity_kwh=5.0, battery_max_rate_kw=5.0*(1.6/2.4),
           tariff_mode=de.TariffMode.COMMERCIAL_FLAT,
           resilience_charge_target_frac=0.95, resilience_charge_hour=11, resilience_charge_cutoff_hour=19)
engine = de.HybridDispatchEngine(cfg, 5.0*0.5)
dt = 1/12
solar = lambda h: de.solar_shape(h, 3.0)
for h in range(24):
    for _ in range(12):
        engine.step(de.Reading(hour=h, solar_available_kw=solar(h), load_kw=1.35, grid_available=True), dt)
engine.reset_period()
for h in range(24):
    for _ in range(12):
        engine.step(de.Reading(hour=h, solar_available_kw=solar(h), load_kw=1.35, grid_available=True), dt)
savings_3kw5kwh = engine.scaled_period_savings(30.4)
print(f"3.0kW/5kWh system, simulated for real: Tk{savings_3kw5kwh:,.2f}/mo savings")
print(f"Coverage vs its own correctly-matched Tk{emi_3kw5kwh:,.0f} EMI: {savings_3kw5kwh/emi_3kw5kwh*100:.1f}%")
