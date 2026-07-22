"""
Sprint C: cost of capturing the poultry + cold storage market.
Salary data note: Glassdoor's Bangladesh figures were internally inconsistent
(e.g. one page showing "software engineer = Tk55,000/YEAR", clearly a
monthly/annual mislabel given it's below subsistence). Using the more
internally-consistent BDTechJobs/Payscale-style MONTHLY figures instead,
explicitly flagged.
"""

print("="*70)
print("CORE TEAM — Year 1, monthly cost (Tk)")
print("="*70)
team = {
 "Regulatory/compliance lead (SREDA, BERC, net-metering navigation)": 70_000,
 "BD/partnerships lead (integrators, associations, banks)": 60_000,
 "Credit/risk analyst (feasibility + risk-scoring design)": 80_000,
 "Software engineer x2 (platform/monitoring build)": 100_000,
 "Field ops / installer-QA coordinator": 40_000,
 "Field agents/site assessors x3": 90_000,
 "Founder/ops overhead (shared, below-market draw)": 60_000,
}
total_monthly = sum(team.values())
for role, cost in team.items():
    print(f"  {role:60s} Tk {cost:,}")
print(f"  {'TOTAL monthly team cost':60s} Tk {total_monthly:,}")
print(f"  {'Annual team cost':60s} Tk {total_monthly*12:,} (~${total_monthly*12/122:,.0f})")
print("  (Bangladesh salary benchmarks are noisy/inconsistent across sources -")
print("   these use the more internally-consistent monthly figures found;")
print("   treat as planning-grade, not a verified payroll quote.)")

print("\n" + "="*70)
print("CUSTOMER ACQUISITION COST (CAC) BY CHANNEL")
print("="*70)

# Poultry via integrator: one relationship deal unlocks many farms
integrator_deal_cost = 400_000   # BD lead's time/relationship-building, amortized
farms_per_integrator = 250       # mid-point of "dozens to hundreds" range established in Sprint 1
per_farm_onboarding = 6_000      # site visit + financing-application navigation labor, per farm
cac_integrator_farm = integrator_deal_cost/farms_per_integrator + per_farm_onboarding
print(f"Poultry, integrator-channel: Tk{integrator_deal_cost:,} deal cost / {farms_per_integrator} farms")
print(f"  + Tk{per_farm_onboarding:,}/farm onboarding = CAC Tk{cac_integrator_farm:,.0f}/farm")

# Poultry, independent farmer: field-agent-driven, higher touch
cac_independent_farm = 22_000
print(f"Poultry, independent farmer (no integrator): CAC ~Tk{cac_independent_farm:,}/farm (field-agent model, higher touch)")

# Cold storage: high-ticket enterprise sale
cac_coldstorage = 350_000
avg_cs_deal_value = 24_800_000  # from Sprint B (avg facility system cost)
cac_pct_of_deal = cac_coldstorage/avg_cs_deal_value*100
print(f"Cold storage, direct/association-channel: CAC ~Tk{cac_coldstorage:,}/facility")
print(f"  -> {cac_pct_of_deal:.1f}% of average deal value (Tk{avg_cs_deal_value:,.0f}) - normal for high-ticket B2B (1-5% typical)")

print("\n" + "="*70)
print("COST TO REACH A CREDIBLE FIRST MILESTONE (Year 1-2)")
print("="*70)
# Milestone: 1,500 poultry farms (mostly integrator-channel, some independent)
# + 15 cold storage facilities - a genuinely meaningful proof point, not a
# moonshot (1,500 farms is ~2.7% of the Gazipur-only SAM of ~13,200 farms)
INTEGRATOR_FARMS = 1200
INDEPENDENT_FARMS = 300
CS_FACILITIES = 15

poultry_cac_cost = INTEGRATOR_FARMS*cac_integrator_farm + INDEPENDENT_FARMS*cac_independent_farm
cs_cac_cost = CS_FACILITIES*cac_coldstorage
total_cac_cost = poultry_cac_cost + cs_cac_cost
team_cost_2yr = total_monthly*24

print(f"Target: {INTEGRATOR_FARMS+INDEPENDENT_FARMS:,} poultry farms + {CS_FACILITIES} cold storage facilities in 24 months")
print(f"  Poultry CAC total: Tk{poultry_cac_cost:,.0f}")
print(f"  Cold storage CAC total: Tk{cs_cac_cost:,.0f}")
print(f"  2-year team cost: Tk{team_cost_2yr:,.0f}")
print(f"  TOTAL cost to reach this milestone: Tk{(total_cac_cost+team_cost_2yr):,.0f} "
      f"(~${(total_cac_cost+team_cost_2yr)/122:,.0f})")

print("\nNote: this is OPERATING cost to acquire/serve customers, not a loan book.")
print("Under the packager model, SolarThik is not financing the Tk8.5M-24.8M")
print("systems themselves - that capital comes from banks/NBFI/IDCOL refinance.")
print("This is the actual capital SolarThik itself needs to raise.")
