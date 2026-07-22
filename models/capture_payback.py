"""
Sprint D: realistic capture-rate trajectory -> SolarThik's own revenue ->
TRUE sustained payback on the company's own invested capital.

Growth-curve shape: S-curve (logistic), informed by SolarSquare's real
trajectory (~10 years to ~50,000 households, acceleration concentrated in
the final ~18 months) -- not linear growth.
"""
import math

SAM_POULTRY = 55_000
SAM_COLDSTORAGE = 310

POULTRY_SYSTEM_VALUE = 470_000
POULTRY_ORIGINATION_FEE_PCT = 0.04
POULTRY_MONITORING_FEE_MO = 250

CS_SYSTEM_VALUE = 24_800_000
CS_ORIGINATION_FEE_PCT = 0.04
CS_MONITORING_FEE_MO = 12_000

def s_curve_capture(year, sam, y1_2_target, ceiling_fraction, midpoint_year, steepness):
    if year <= 2:
        return y1_2_target * (year / 2)
    ceiling = sam * ceiling_fraction
    x = steepness * (year - midpoint_year)
    logistic = ceiling / (1 + math.exp(-x))
    return max(y1_2_target, logistic)

scenarios = {
    "CONSERVATIVE": dict(poultry_ceiling=0.10, cs_ceiling=0.15, mid=7, steep=0.55),
    "BASE":         dict(poultry_ceiling=0.18, cs_ceiling=0.28, mid=6.5, steep=0.65),
    "OPTIMISTIC":   dict(poultry_ceiling=0.28, cs_ceiling=0.40, mid=6, steep=0.75),
}

all_results = {}
for name, p in scenarios.items():
    print(f"\n{'='*88}\n{name} SCENARIO\n{'='*88}")
    print(f"{'Yr':<4}{'Poultry':<10}{'ColdStor':<10}{'YrRevenue(Tk)':<16}{'YrCost(Tk)':<14}{'CumNet(Tk)':<16}")
    cum_poultry_prev, cum_cs_prev = 0, 0
    cum_revenue, cum_cost = 0, 0
    net_history = []
    row_data = []
    for year in range(1, 11):
        poultry_cust = s_curve_capture(year, SAM_POULTRY, 1200, p['poultry_ceiling'], p['mid'], p['steep'])
        cs_cust = s_curve_capture(year, SAM_COLDSTORAGE, 15, p['cs_ceiling'], p['mid'], p['steep'])
        new_poultry = max(0, poultry_cust - cum_poultry_prev)
        new_cs = max(0, cs_cust - cum_cs_prev)

        poultry_rev = new_poultry * POULTRY_SYSTEM_VALUE * POULTRY_ORIGINATION_FEE_PCT + poultry_cust * POULTRY_MONITORING_FEE_MO * 12
        cs_rev = new_cs * CS_SYSTEM_VALUE * CS_ORIGINATION_FEE_PCT + cs_cust * CS_MONITORING_FEE_MO * 12
        year_revenue = poultry_rev + cs_rev

        if year <= 2: team_cost = 500_000 * 12
        elif year <= 5: team_cost = 500_000 * 12 * 3.5
        else: team_cost = 500_000 * 12 * 8
        cac_cost = new_poultry * 10_000 + new_cs * 350_000
        year_cost = team_cost + cac_cost

        cum_revenue += year_revenue
        cum_cost += year_cost
        net_cum = cum_revenue - cum_cost
        net_history.append(net_cum)
        row_data.append((year, poultry_cust, cs_cust))
        print(f"{year:<4}{poultry_cust:<10,.0f}{cs_cust:<10,.0f}{year_revenue:<16,.0f}{year_cost:<14,.0f}{net_cum:<16,.0f}")
        cum_poultry_prev, cum_cs_prev = poultry_cust, cs_cust

    # TRUE sustained payback: earliest year after which cumulative net stays >= 0 for ALL remaining years
    sustained_payback = None
    for i in range(len(net_history)):
        if all(v >= 0 for v in net_history[i:]):
            sustained_payback = i + 1
            break
    trough = min(net_history)
    trough_year = net_history.index(trough) + 1

    print(f"\n  Trough (worst cumulative net): Tk{trough:,.0f} in Year {trough_year}")
    print(f"  TRUE sustained payback: {'Year ' + str(sustained_payback) if sustained_payback else 'NOT reached within 10-year horizon'}")
    print(f"  Year-10: {poultry_cust:,.0f} poultry ({poultry_cust/SAM_POULTRY:.1%} of SAM), "
          f"{cs_cust:,.0f} cold storage ({cs_cust/SAM_COLDSTORAGE:.1%} of SAM)")
    print(f"  10-yr cumulative revenue: Tk{cum_revenue:,.0f} (~${cum_revenue/122/1e6:.2f}M)")
    print(f"  10-yr cumulative cost:    Tk{cum_cost:,.0f} (~${cum_cost/122/1e6:.2f}M)")

    all_results[name] = dict(payback=sustained_payback, trough=trough, trough_year=trough_year,
                              final_poultry=poultry_cust, final_cs=cs_cust,
                              cum_revenue=cum_revenue, cum_cost=cum_cost)

print(f"\n{'='*88}\nSUMMARY\n{'='*88}")
for name, r in all_results.items():
    pb = f"Year {r['payback']}" if r['payback'] else "not within 10yr"
    print(f"{name:14s}: trough Tk{r['trough']/1e6:.0f}M (Yr{r['trough_year']}) | sustained payback: {pb} | "
          f"Yr10 rev Tk{r['cum_revenue']/1e9:.2f}B | Yr10 custs {r['final_poultry']+r['final_cs']:,.0f}")
