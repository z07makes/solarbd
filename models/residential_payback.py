"""
Sprint D-extended: adds residential to capture_payback.py's poultry +
cold-storage payback model, using the SAME s_curve_capture() logistic shape,
team-cost schedule, and "true sustained payback" definition -- so this is
additive to the existing model, not a competing methodology.

ORIGINAL VERSION -- reproduces the earlier session's placeholder-CAC result
exactly, as a baseline. See residential_payback_updated.py in this same
delivery for what changes once the real, researched CAC figure replaces the
Tk4,000 placeholder.
"""
import math

SAM_POULTRY, SAM_COLDSTORAGE, SAM_RESIDENTIAL = 55_000, 310, 500_000

POULTRY_SYSTEM_VALUE, POULTRY_FEE_PCT, POULTRY_MONITORING_MO = 470_000, 0.04, 250
CS_SYSTEM_VALUE, CS_FEE_PCT, CS_MONITORING_MO = 24_800_000, 0.04, 12_000
RES_SYSTEM_VALUE, RES_FEE_PCT, RES_MONITORING_MO, RES_CAC = 450_000, 0.04, 150, 4_000


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

print(f"{'Scenario':<14}{'w/o residential (orig.)':<26}{'w/ residential (this run)':<28}{'Delta':<12}")
for name, p in scenarios.items():
    cum_poultry_prev = cum_cs_prev = cum_res_prev = 0
    cum_revenue = cum_cost = 0
    net_history, net_history_no_res = [], []
    cum_revenue_no_res = cum_cost_no_res = 0

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
        year_revenue_no_res = poultry_rev + cs_rev

        if year <= 2: team_cost = 500_000 * 12
        elif year <= 5: team_cost = 500_000 * 12 * 3.5
        else: team_cost = 500_000 * 12 * 8
        cac_cost = new_poultry * 10_000 + new_cs * 350_000
        cac_cost_res = new_res * RES_CAC
        year_cost = team_cost + cac_cost + cac_cost_res
        year_cost_no_res = team_cost + cac_cost

        cum_revenue += year_revenue; cum_cost += year_cost
        cum_revenue_no_res += year_revenue_no_res; cum_cost_no_res += year_cost_no_res
        net_history.append(cum_revenue - cum_cost)
        net_history_no_res.append(cum_revenue_no_res - cum_cost_no_res)
        cum_poultry_prev, cum_cs_prev, cum_res_prev = poultry_cust, cs_cust, res_cust

    def sustained_payback(hist):
        for i in range(len(hist)):
            if all(v >= 0 for v in hist[i:]):
                return i + 1
        return None

    pb_with = sustained_payback(net_history)
    pb_without = sustained_payback(net_history_no_res)
    pb_with_s = f"Yr{pb_with}" if pb_with else "not in 10yr"
    pb_without_s = f"Yr{pb_without}" if pb_without else "not in 10yr"
    delta_yr10 = net_history[-1] - net_history_no_res[-1]
    print(f"{name:<14}{pb_without_s+' | Yr10 Tk'+format(net_history_no_res[-1]/1e6,'.0f')+'M':<26}"
          f"{pb_with_s+' | Yr10 Tk'+format(net_history[-1]/1e6,'.0f')+'M':<28}"
          f"+Tk{delta_yr10/1e6:.0f}M")
    print(f"  Year-10 residential customers: {res_cust:,.0f} ({res_cust/SAM_RESIDENTIAL:.1%} of the {SAM_RESIDENTIAL:,} SAM placeholder)")
