"""
Same model as residential_payback.py, same methodology, one change: RES_CAC
is swept across the real, researched range from
RESEARCH-BATTERY-COST-AND-RESIDENTIAL-SAM-CAC.md (SolarSquare's India
referral-commission benchmark, Rs2,000/kW) instead of the Tk4,000 placeholder.
"""
import math

SAM_POULTRY, SAM_COLDSTORAGE, SAM_RESIDENTIAL = 55_000, 310, 500_000
POULTRY_SYSTEM_VALUE, POULTRY_FEE_PCT, POULTRY_MONITORING_MO = 470_000, 0.04, 250
CS_SYSTEM_VALUE, CS_FEE_PCT, CS_MONITORING_MO = 24_800_000, 0.04, 12_000
RES_SYSTEM_VALUE, RES_FEE_PCT, RES_MONITORING_MO = 450_000, 0.04, 150

CAC_SCENARIOS = {
    "Tk4,000 (original placeholder)": 4_000,
    "Tk7,740 (3.0kW referral commission)": 7_740,
    "Tk14,190 (5.5kW -- SolarThik's own default system size)": 14_190,
    "Tk20,640 (8.0kW referral commission)": 20_640,
}


def s_curve_capture(year, sam, y1_2_target, ceiling_fraction, midpoint_year, steepness):
    if year <= 2:
        return y1_2_target * (year / 2)
    ceiling = sam * ceiling_fraction
    x = steepness * (year - midpoint_year)
    logistic = ceiling / (1 + math.exp(-x))
    return max(y1_2_target, logistic)


scenarios = {
    "CONSERVATIVE": dict(poultry_ceiling=0.10, cs_ceiling=0.15, res_ceiling=0.02, mid=7, steep=0.55),
    "BASE":         dict(poultry_ceiling=0.18, cs_ceiling=0.28, res_ceiling=0.05, mid=6.5, steep=0.65),
    "OPTIMISTIC":   dict(poultry_ceiling=0.28, cs_ceiling=0.40, res_ceiling=0.10, mid=6, steep=0.75),
}


def run(res_cac):
    results = {}
    for name, p in scenarios.items():
        cum_poultry_prev = cum_cs_prev = cum_res_prev = 0
        cum_revenue = cum_cost = 0
        net_history = []

        for year in range(1, 11):
            poultry_cust = s_curve_capture(year, SAM_POULTRY, 1200, p['poultry_ceiling'], p['mid'], p['steep'])
            cs_cust = s_curve_capture(year, SAM_COLDSTORAGE, 15, p['cs_ceiling'], p['mid'], p['steep'])
            res_cust = s_curve_capture(year, SAM_RESIDENTIAL, 3000, p['res_ceiling'], p['mid'], p['steep'])

            new_poultry = max(0, poultry_cust - cum_poultry_prev)
            new_cs = max(0, cs_cust - cum_cs_prev)
            new_res = max(0, res_cust - cum_res_prev)

            poultry_rev = new_poultry * POULTRY_SYSTEM_VALUE * POULTRY_FEE_PCT + poultry_cust * POULTRY_MONITORING_MO * 12
            cs_rev = new_cs * CS_SYSTEM_VALUE * CS_FEE_PCT + cs_cust * CS_MONITORING_MO * 12
            res_rev = new_res * RES_SYSTEM_VALUE * RES_FEE_PCT + res_cust * RES_MONITORING_MO * 12
            year_revenue = poultry_rev + cs_rev + res_rev

            if year <= 2: team_cost = 500_000 * 12
            elif year <= 5: team_cost = 500_000 * 12 * 3.5
            else: team_cost = 500_000 * 12 * 8
            cac_cost = new_poultry * 10_000 + new_cs * 350_000 + new_res * res_cac
            year_cost = team_cost + cac_cost

            cum_revenue += year_revenue
            cum_cost += year_cost
            net_history.append(cum_revenue - cum_cost)
            cum_poultry_prev, cum_cs_prev, cum_res_prev = poultry_cust, cs_cust, res_cust

        def sustained_payback(hist):
            for i in range(len(hist)):
                if all(v >= 0 for v in hist[i:]):
                    return i + 1
            return None

        results[name] = dict(payback=sustained_payback(net_history), yr10=net_history[-1])
    return results


print(f"{'CAC scenario':<58}{'CONSERVATIVE':<22}{'BASE':<22}{'OPTIMISTIC':<22}")
print("-" * 124)
for label, cac in CAC_SCENARIOS.items():
    r = run(cac)
    row = label.ljust(58)
    for scen in ["CONSERVATIVE", "BASE", "OPTIMISTIC"]:
        pb = f"Yr{r[scen]['payback']}" if r[scen]['payback'] else "not in 10yr"
        row += f"{pb+' Tk'+format(r[scen]['yr10']/1e6,'.0f')+'M':<22}"
    print(row)

print("\n" + "=" * 78)
print("READ: does the real CAC change the headline conclusion?")
print("=" * 78)
baseline = run(4_000)
real = run(14_190)
for scen in ["CONSERVATIVE", "BASE", "OPTIMISTIC"]:
    b, r = baseline[scen], real[scen]
    same_verdict = (b['payback'] is not None) == (r['payback'] is not None)
    print(f"{scen}: at Tk4,000 CAC -> {'pays back' if b['payback'] else 'does NOT pay back'} in 10yr "
          f"(Yr10 Tk{b['yr10']/1e6:.0f}M). At real Tk14,190 CAC -> "
          f"{'pays back' if r['payback'] else 'does NOT pay back'} in 10yr (Yr10 Tk{r['yr10']/1e6:.0f}M). "
          f"{'Same conclusion, lower magnitude.' if same_verdict else 'CONCLUSION FLIPS.'}")
