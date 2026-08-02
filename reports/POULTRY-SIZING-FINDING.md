# Finding: Poultry's EMI and simulated system size don't match (good-news direction)

**Found:** August 2, 2026, alongside the lender-portal rebuild.
**Status:** New. Unlike the cold-storage finding, this one resolves favorably either way.

## The issue

The documented EMI (Tk4,487/mo) and the documented savings (Tk4,824/mo, 107.5% coverage) trace to two different-sized systems:

- **Tk4,487 EMI** matches, to the dollar, a **3.0kW solar + 5kWh battery** system at green-refinance terms — `mitigation_calc.py`'s "Lever 3: COMBINED" scenario.
- **Tk4,824 savings** comes from the dispatch engine's actual validated Test F configuration — a much smaller **1.36kW solar + 2.4kWh battery** system.

## What this means

Opposite of cold storage: there, the savings assumed a bigger battery than the EMI paid for. Here, the EMI paid for a bigger system than what's actually being simulated. Reconciling either direction improves the number:

| Reconciliation | Result |
|---|---|
| Size-match the EMI down to the real 1.36kW/2.4kWh system | **157–241% coverage** (financing-term dependent) |
| Size-match the savings up — run the 3.0kW/5kWh system for real | Tk7,950/mo savings, **177%** against its own Tk4,487 EMI |

Full computation in `models/poultry_sizing_audit.py`.

## Recommendation

Decide which system is actually being sold — the small Test-F-style unit or the larger mitigation-lever unit — and use that system's own physics and its own EMI together. Either choice beats the currently-quoted 107.5%.
