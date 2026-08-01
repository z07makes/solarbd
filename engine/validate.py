"""
SolarThik dispatch engine validation suite (Python).

This is a NEW file. No validate.py was available anywhere in this
conversation or in the live repo (github.com/z07makes/solarbd, checked
2026-08-01) to recover -- see dispatch_engine.py's provenance note. This
suite tests dispatch_engine.py against every figure this project has
previously documented and verified (SOLARTHIK-MASTER-REPOSITORY.md and its
userMemories), plus the project's own stated design principles.

Run: python3 validate.py
"""
import dispatch_engine as de

PASS, FAIL = [], []


def check(name, condition, detail=""):
    if condition:
        PASS.append(name)
        print(f"  PASS  {name}" + (f"   ({detail})" if detail else ""))
    else:
        FAIL.append(name)
        print(f"  FAIL  {name}" + (f"   ({detail})" if detail else ""))


def approx(a, b, tol=1.0):
    return abs(a - b) <= tol


print("=" * 76)
print("TEST 1 -- Residential slab billing, manual cross-check")
print("=" * 76)
expected = 50 * 4.63 + 150 * 7.50 + 100 * 9.10 + 100 * 9.62 + 200 * 15.01 + 200 * 17.35
actual = de.slab_bill(800)
check("slab_bill(800) matches manual band-by-band arithmetic", approx(actual, expected, 0.01),
      f"engine={actual:.2f}, manual={expected:.2f}")

print("\n" + "=" * 76)
print("TEST 2 -- Slab billing is non-linear (core project principle)")
print("=" * 76)
one_day_kwh = 800 / 30.4
naive_scaled = de.slab_bill(one_day_kwh) * 30.4
correct_scaled = de.slab_bill(one_day_kwh * 30.4)
check("scaling a Tk figure by day-count differs from scaling kWh then billing",
      abs(naive_scaled - correct_scaled) > 1.0,
      f"naive=Tk{naive_scaled:.2f} vs correct=Tk{correct_scaled:.2f}, diff=Tk{abs(naive_scaled - correct_scaled):.2f}")

print("\n" + "=" * 76)
print("TEST 3 -- Poultry: exact reproduction of the documented Test F figure")
print("=" * 76)


def run_poultry():
    cfg = dict(
        battery_capacity_kwh=2.4, battery_max_rate_kw=1.6, tariff_mode=de.TariffMode.COMMERCIAL_FLAT,
        resilience_charge_target_frac=0.95, resilience_charge_hour=11, resilience_charge_cutoff_hour=19,
    )
    engine = de.HybridDispatchEngine(cfg, 2.4 * 0.5)  # 50% SOC start -- exact Test F methodology
    dt = 1 / 12
    solar = lambda h: de.solar_shape(h, 1.36)
    for h in range(24):  # 1 priming day
        for _ in range(12):
            engine.step(de.Reading(hour=h, solar_available_kw=solar(h), load_kw=1.35, grid_available=True), dt)
    engine.reset_period()
    for h in range(24):  # measured day
        for _ in range(12):
            engine.step(de.Reading(hour=h, solar_available_kw=solar(h), load_kw=1.35, grid_available=True), dt)
    return engine.scaled_period_savings(30.4)


poultry_savings = run_poultry()
poultry_emi = 4487
poultry_coverage = poultry_savings / poultry_emi * 100
check("poultry monthly savings ~ documented Tk4,824", approx(poultry_savings, 4824, 5.0), f"got Tk{poultry_savings:,.2f}")
check("poultry coverage ~ documented 107.5%", approx(poultry_coverage, 107.5, 0.2), f"got {poultry_coverage:.2f}%")

print("\n" + "=" * 76)
print("TEST 4 -- Cold storage: TOU arbitrage ceiling across battery sizes")
print("=" * 76)


def run_cold_storage(batt_kwh, batt_rate_kw):
    cfg = dict(
        battery_capacity_kwh=batt_kwh, battery_max_rate_kw=batt_rate_kw, tariff_mode=de.TariffMode.TIME_OF_USE,
        peak_hard_floor_frac=0.05, charge_from_grid_offpeak=True,
    )
    engine = de.HybridDispatchEngine(cfg, 0)
    solar_by_hour = de.build_solar_profile(100 * 4.3 * 0.8)
    load = 3000 * 800 / 8760
    dt = 1 / 12
    for day in range(2):
        for h in range(24):
            for _ in range(12):
                engine.step(de.Reading(hour=h, solar_available_kw=solar_by_hour[h], load_kw=load, grid_available=True), dt)
        if day == 0:
            engine.reset_period()
    return engine.scaled_period_savings(30.4)


for batt, rate, expected_savings in [(0, 0, 100602), (500, 150, 158362), (1000, 250, 216122), (1500, 300, 267177)]:
    savings = run_cold_storage(batt, rate)
    check(f"cold storage @ {batt}kWh battery ~ documented Tk{expected_savings:,}",
          approx(savings, expected_savings, 500), f"got Tk{savings:,.2f}")

ceiling = run_cold_storage(1500, 300) - run_cold_storage(0, 0)
check("battery-attributable ceiling ~ documented Tk166,575 (274*5*(13.62-9.62)*30.4)",
      approx(ceiling, 166575, 500), f"got Tk{ceiling:,.2f}")

print("\n" + "=" * 76)
print("TEST 5 -- Forecast-aware reserve")
print("=" * 76)
engine = de.HybridDispatchEngine(dict(battery_capacity_kwh=10, battery_max_rate_kw=5, tariff_mode=de.TariffMode.RESIDENTIAL_SLAB))
no_forecast = engine.active_reserve_frac
check("default reserve is 15.0% with no forecast set", approx(no_forecast * 100, 15.0, 0.01), f"got {no_forecast * 100:.2f}%")

with_forecast = engine.set_generation_forecast(0.45 * 10, 10)
check("reserve rises to ~23.2-23.3% at a 45%-of-baseline forecast",
      23.0 <= with_forecast * 100 <= 23.5, f"got {with_forecast * 100:.2f}%")

engine.clear_generation_forecast()
after_clear = engine.active_reserve_frac
check("reserve reverts exactly to 15.0% once the forecast feed is cleared",
      approx(after_clear, 0.15, 1e-9), f"got {after_clear * 100:.4f}%")

print("\n" + "=" * 76)
print("TEST 6 -- Input validation clips garbage readings")
print("=" * 76)
bad = de.Reading(hour=25, solar_available_kw=-2, load_kw=float("nan"), grid_available=True, battery_soc_kwh=999)
cleaned, faults = de.validate_reading(bad, battery_capacity_kwh=10, source_id="test")
check("negative solar clipped to 0", cleaned.solar_available_kw == 0)
check("non-finite load clipped to 0", cleaned.load_kw == 0)
check("out-of-range hour normalized into 0-23", 0 <= cleaned.hour <= 23)
check("out-of-range SOC clamped to battery capacity", cleaned.battery_soc_kwh == 10)
check("all four faults reported", len(faults) == 4, f"faults={faults}")

print("\n" + "=" * 76)
print("TEST 7 -- Telemetry watchdog: silence is not zero")
print("=" * 76)
wd = de.TelemetryWatchdog(max_staleness_s=30.0)
check("watchdog starts NEVER_SEEN before any reading", wd.status(_now=0) == de.FeedStatus.NEVER_SEEN)
wd.ingest(de.Reading(hour=10, solar_available_kw=1.0, load_kw=1.0, grid_available=True), _now=0)
check("watchdog reports OK right after a fresh reading", wd.status(_now=5) == de.FeedStatus.OK)
check("watchdog reports STALE once max_staleness_s has elapsed", wd.status(_now=40) == de.FeedStatus.STALE)

print("\n" + "=" * 76)
print("TEST 8 -- State persistence round-trip")
print("=" * 76)
cfg7 = dict(battery_capacity_kwh=5, battery_max_rate_kw=2, tariff_mode=de.TariffMode.RESIDENTIAL_SLAB)
solar_by_hour7 = de.build_solar_profile(5.5 * 4.3 * 0.8)
load_by_hour7 = [1.0] * 24
dt7 = 1 / 12

uninterrupted = de.HybridDispatchEngine(cfg7, 0)
for day in range(2):
    for h in range(24):
        for _ in range(12):
            uninterrupted.step(de.Reading(hour=h, solar_available_kw=solar_by_hour7[h], load_kw=load_by_hour7[h], grid_available=True), dt7)
uninterrupted_savings = uninterrupted.scaled_period_savings(30.4)

interrupted = de.HybridDispatchEngine(cfg7, 0)
for h in range(24):
    for _ in range(12):
        interrupted.step(de.Reading(hour=h, solar_available_kw=solar_by_hour7[h], load_kw=load_by_hour7[h], grid_available=True), dt7)
state = interrupted.to_state()
restarted = de.HybridDispatchEngine.from_state(cfg7, state)
for h in range(24):
    for _ in range(12):
        restarted.step(de.Reading(hour=h, solar_available_kw=solar_by_hour7[h], load_kw=load_by_hour7[h], grid_available=True), dt7)
restarted_savings = restarted.scaled_period_savings(30.4)

check("persisted-and-restarted engine matches an uninterrupted run to machine precision",
      abs(uninterrupted_savings - restarted_savings) < 1e-9,
      f"uninterrupted=Tk{uninterrupted_savings:.8f}, restarted=Tk{restarted_savings:.8f}")

print("\n" + "=" * 76)
print("TEST 9 -- Outage-period load is excluded from the savings counterfactual")
print("=" * 76)
cfg9 = dict(battery_capacity_kwh=5, battery_max_rate_kw=2, tariff_mode=de.TariffMode.COMMERCIAL_FLAT)
e_normal = de.HybridDispatchEngine(cfg9, 2.5)
e_outage = de.HybridDispatchEngine(cfg9, 2.5)
for h in range(24):
    for _ in range(12):
        grid_ok = h not in (19, 20, 21)
        e_normal.step(de.Reading(hour=h, solar_available_kw=0, load_kw=1.0, grid_available=True), dt7)
        e_outage.step(de.Reading(hour=h, solar_available_kw=0, load_kw=1.0, grid_available=grid_ok), dt7)
check("outage-hour load never enters the billed total",
      e_outage.period_total_load_kwh < e_normal.period_total_load_kwh,
      f"normal={e_normal.period_total_load_kwh:.2f}kWh billed vs outage-affected={e_outage.period_total_load_kwh:.2f}kWh billed")

print("\n" + "=" * 76)
print(f"SUMMARY: {len(PASS)} passed, {len(FAIL)} failed")
print("=" * 76)
if FAIL:
    print("FAILED:", FAIL)
    raise SystemExit(1)
