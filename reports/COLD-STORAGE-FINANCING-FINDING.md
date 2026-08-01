# Finding: Cold storage's "349%" coverage figure doesn't reconcile with its own EMI

**Found:** August 1, 2026, during dispatch-engine.py reconstruction and cross-validation.
**Status:** New, unresolved, not previously caught in any prior session.
**Severity:** High — this is a headline, investor/lender-facing number.

---

## The issue

Every version of the platform prototype uses the same EMI (**Tk76,632/month**) for cold storage against two different savings figures:

- **0 kWh battery:** Tk100,602/mo saved → **131% coverage**
- **1,500 kWh battery:** Tk267,177/mo saved → **349% coverage**

`cold_storage_financing_audit.py` (delivered alongside this note) confirms Tk76,632 is exactly what a **100kW, Tk8.5M solar-only system** costs at green-refinance terms (15% down, 10yr, 5% APR — the same terms already used in `mitigation_calc.py`). The 1,500kWh/300kW battery that the 349% figure depends on **was never added to that loan** — at the project's own established cost assumption (Tk25,000/kWh, the same figure that correctly gets rolled into poultry's EMI in `sme_calc.py`), that battery alone costs **Tk37.5M — more than 4x the solar system, and more than the Tk24.8M "average facility" value used elsewhere in the same lender portal for this exact segment.**

The 131% figure needs no correction — there's no battery in that scenario, so the existing EMI is already internally consistent. The 349% figure is the one that doesn't hold up.

## What the honestly-financed number actually looks like

| Financing assumption | All-in EMI (solar + 1,500kWh battery) | Coverage (vs. Tk267,177 savings) |
|---|---|---|
| Green-refinance terms on everything | Tk414,716/mo | **64.4%** |
| Standard commercial terms on everything | Tk649,621/mo | **41.1%** |
| Blended (solar green, battery commercial) | Tk606,214/mo | **44.1%** |

And the marginal picture is the more important part: **every 500kWh of added battery costs about Tk112,700/month more in EMI than it returns in arbitrage savings**, at every step from 0→1,500kWh. Under this cost assumption and this specific TOU rate spread (Tk13.62 peak / Tk9.62 off-peak), bigger batteries make the *coverage ratio* worse, not better, once financed honestly — the opposite of what the headline figure implies.

## Caveats — this is not a closed case

- **Tk25,000/kWh is a small-battery assumption.** It was set for poultry's 2.4–10kWh battery. A 1,500kWh utility-scale battery plausibly costs meaningfully less per kWh once BOS/inverter/labor cost amortizes — a real vendor quote at this scale would move every number above, and this audit doesn't have one.
- **This is arbitrage-only.** It excludes resilience/spoilage-avoidance value, which `sme_calc.py` separately argues can be large for cold storage and doesn't depend on the TOU spread at all. A big battery may still be justified on *that* basis even where arbitrage alone doesn't clear the EMI.
- **Battery green-refinance eligibility is unconfirmed.** Whether Bangladesh's green-refinance window covers storage the same way it covers panels isn't established either way in anything reviewed so far — a real research item, not an assumption either direction should rest on.
- This is scenario modelling with stated assumptions, not financial or investment advice.

## Recommended next step

Before this figure goes in front of another lender or investor, someone needs to decide (with real vendor pricing, not the Tk25,000/kWh placeholder) whether:
1. The EMI gets recomputed to reflect the true all-in cost, or
2. The battery gets right-sized to something a Tk76,632 loan can actually support, or
3. The pitch leans on resilience/spoilage-avoidance value instead of arbitrage to justify the larger battery.

All three are legitimate; none has been chosen yet.
