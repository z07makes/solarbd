"""
Cross-checks the new dispatch_engine.py against the verified dispatch-engine.js
by running IDENTICAL scenarios through each (independently implemented on
each side -- deliberately not sharing setup code with validate.py, since the
whole point is to catch drift between two separate implementations) and
diffing the results numerically.

Run: python3 cross_check_js_python.py
"""
import json
import subprocess
import sys

import dispatch_engine as de


def run_poultry_test_f():
    cfg = dict(
        battery_capacity_kwh=2.4, battery_max_rate_kw=1.6, tariff_mode=de.TariffMode.COMMERCIAL_FLAT,
        resilience_charge_target_frac=0.95, resilience_charge_hour=11, resilience_charge_cutoff_hour=19,
    )
    engine = de.HybridDispatchEngine(cfg, 2.4 * 0.5)
    steps_per_hour, dt = 12, 1 / 12

    def solar_for(h):
        return de.solar_shape(h, 1.36)

    for h in range(24):
        for _ in range(steps_per_hour):
            engine.step(de.Reading(hour=h, solar_available_kw=solar_for(h), load_kw=1.35, grid_available=True), dt)
    engine.reset_period()
    for h in range(24):
        for _ in range(steps_per_hour):
            engine.step(de.Reading(hour=h, solar_available_kw=solar_for(h), load_kw=1.35, grid_available=True), dt)
    return engine.scaled_period_savings(30.4)


def run_cold_storage(batt_cap, batt_rate):
    cfg = dict(
        battery_capacity_kwh=batt_cap, battery_max_rate_kw=batt_rate, tariff_mode=de.TariffMode.TIME_OF_USE,
        peak_hard_floor_frac=0.05, charge_from_grid_offpeak=True,
    )
    engine = de.HybridDispatchEngine(cfg, 0)
    solar_by_hour = de.build_solar_profile(100 * 4.3 * 0.8)
    load = 3000 * 800 / 8760
    steps_per_hour, dt = 12, 1 / 12
    for day in range(2):
        for h in range(24):
            for _ in range(steps_per_hour):
                engine.step(de.Reading(hour=h, solar_available_kw=solar_by_hour[h], load_kw=load, grid_available=True), dt)
        if day == 0:
            engine.reset_period()
    return engine.scaled_period_savings(30.4)


def run_forecast_reserve():
    engine = de.HybridDispatchEngine(dict(battery_capacity_kwh=10, battery_max_rate_kw=5, tariff_mode=de.TariffMode.RESIDENTIAL_SLAB))
    no_forecast = engine.active_reserve_frac
    with_forecast = engine.set_generation_forecast(0.45 * 10, 10)
    engine.clear_generation_forecast()
    after_clear = engine.active_reserve_frac
    return dict(noForecast=no_forecast, withForecast=with_forecast, afterClear=after_clear)


def run_validate_reading_sanity():
    bad = de.Reading(hour=25, solar_available_kw=-2, load_kw=float("nan"), grid_available=True, battery_soc_kwh=999)
    cleaned, faults = de.validate_reading(bad, battery_capacity_kwh=10, source_id="test")
    return dict(
        cleaned=dict(
            hour=cleaned.hour, solarAvailableKw=cleaned.solar_available_kw, loadKw=cleaned.load_kw,
            gridAvailable=cleaned.grid_available, batterySocKwh=cleaned.battery_soc_kwh,
        ),
        faults=faults,
    )


py_results = dict(
    poultryTestF=run_poultry_test_f(),
    coldStorage0=run_cold_storage(0, 0),
    coldStorage500=run_cold_storage(500, 150),
    coldStorage1000=run_cold_storage(1000, 250),
    coldStorage1500=run_cold_storage(1500, 300),
    forecastReserve=run_forecast_reserve(),
    slabBilling800=de.slab_bill(800),
    validateReadingSanity=run_validate_reading_sanity(),
)

proc = subprocess.run(["node", "js_scenarios.js"], capture_output=True, text=True)
if proc.returncode != 0:
    print("JS RUN FAILED:")
    print(proc.stderr)
    sys.exit(1)
js_results = json.loads(proc.stdout)


def close(a, b, tol=1e-6):
    if isinstance(a, dict) and isinstance(b, dict):
        return set(a.keys()) == set(b.keys()) and all(close(a[k], b[k], tol) for k in a)
    if isinstance(a, list) and isinstance(b, list):
        return a == b
    if isinstance(a, bool) or isinstance(b, bool):
        return a == b
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return abs(a - b) <= tol * max(1.0, abs(a), abs(b))
    return a == b


print(f"{'scenario':<24}{'python':>18}{'javascript':>18}   match")
print("-" * 72)
all_ok = True
for key in py_results:
    p, j = py_results[key], js_results[key]
    ok = close(p, j)
    all_ok = all_ok and ok
    p_disp = f"{p:,.4f}" if isinstance(p, (int, float)) and not isinstance(p, bool) else str(p)[:18]
    j_disp = f"{j:,.4f}" if isinstance(j, (int, float)) and not isinstance(j, bool) else str(j)[:18]
    print(f"{key:<24}{p_disp:>18}{j_disp:>18}   {'OK' if ok else 'MISMATCH'}")

print()
if all_ok:
    print("ALL SCENARIOS MATCH -- dispatch_engine.py and dispatch-engine.js agree numerically.")
else:
    print("MISMATCH DETECTED -- ports have drifted, see above.")
sys.exit(0 if all_ok else 1)
