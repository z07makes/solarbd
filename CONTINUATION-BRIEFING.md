# SolarThik — Continuation Briefing (session ending Aug 2, 2026)

**Purpose:** hand off to a fresh conversation without re-reading this session's full transcript. Read this, then verify against the live repo directly — this doc explains *why* things are the way they are; the repo itself is the source of truth for *what currently exists*.

**Relationship to SOLARTHIK-MASTER-REPOSITORY.md** (the older, much longer document, if it gets uploaded to the new chat too): that document predates this session and is now stale in several places it discusses at length — specifically its cold-storage (349%), poultry (107.5%), and residential-payback narrative. This briefing and the current repo state supersede it on those points. Everything else in that document (project identity, positioning, prior sessions' reasoning) is still accurate background.

## What actually happened this session, and why

1. **`dispatch_engine.py` never existed anywhere** — not in any prior upload, not in the repo. Authored it fresh as a faithful Python port of the verified `dispatch-engine.js`, then proved the two agree by running identical scenarios through both and diffing numerically (not just trusting the transcription). 22/22 regression tests pass in `engine/validate.py`.

2. **Lender portal security fix**: built `portal/portal-server.js` (JWT-scoped server-side access control) and tested it end-to-end for real — no token, wrong password, integrator-scoped view, lender full view, tampered token, all five behave correctly.

3. **Poultry finding (good news):** the documented Tk4,487 EMI and Tk4,824 savings figure came from two *different-sized* systems — the EMI priced a 3.0kW/5kWh system, the savings simulated a smaller 1.36kW/2.4kWh one. Fixed by simulating the system the EMI actually finances: real result Tk7,950/mo, **177% coverage**, not 107.5%.

4. **Cold storage finding (the opposite direction, and the important one):** the 349% figure baked a 1500kWh battery into the savings side without ever pricing that battery into the EMI. Researched real 2026 battery cost at this scale (Tk27,000–37,000/kWh, sourced from multiple independent industry reports — meaningfully *higher* than this project's Tk25,000/kWh placeholder, not lower). Ran the actual engine across a full 0–2000kWh sweep at real cost: **every battery size is a net loss on pure arbitrage, at every price point in that range.** The honest, fully-consistent headline is solar-only: **131% coverage, Tk100,602/mo, no battery-cost issue.** A battery's real case here is resilience (Bangladesh Cold Storage Association: 30–40% higher opex from diesel gensets during outages, sourced) — real, but not quantified into a coverage number, because that would be inventing precision that isn't there yet.

5. **Residential finding (the most consequential one):** the earlier claim that adding residential "reverses" the company's 10-year payback problem — specifically that even the *conservative* growth scenario clears — rested on a Tk4,000 placeholder CAC. Reran with a real comp (SolarSquare India's referral-commission rate, ~Tk14,190 for a 5.5kW system): **the conservative case no longer pays back in 10 years.** Base and Optimistic still do, at 38–46% lower Year-10 magnitude. This affects the whole-company thesis, not one segment — flag it before it's repeated in front of a lender or investor.

6. **Fixed a real bug live**: the corrected `demos/solarthik-platform-prototype.html` initially referenced `engine/dispatch-engine.js` externally (to avoid duplicating the engine source) — this broke immediately when the file was opened standalone (confirmed via a user screenshot: `Uncaught ReferenceError: buildSolarProfile is not defined`). This exact failure mode had already been diagnosed and fixed once before, in an earlier session, with the opposite conclusion (inline it). Reverted to inlining. Lesson, stated plainly so it doesn't get relearned a third time: **any HTML file in this project that depends on the dispatch engine must inline it, full stop** — these files get opened standalone far more often than they get opened alongside a cloned repo.

## Current repo structure (verify directly, this may already be stale by the time you read it)

```
README.md
SolarThik-Pilot-Seed-OnePager.md   -- rewritten this session, honest numbers, no overclaiming
demos/
  solarthik-demo.html               -- UNCHANGED, still the old naive calculator, not touched this session
  solarthik-platform-prototype.html -- fixed: real engine inlined, honest cold-storage/poultry numbers
engine/
  dispatch_engine.py, dispatch-engine.js, validate.py, cross_check_js_python.py, js_scenarios.js
models/
  (original 5: tam_sam, cost_to_capture, capture_payback, mitigation_calc, sme_calc)
  + cold_storage_financing_audit.py, poultry_sizing_audit.py, real_numbers_research.py,
    residential_payback.py, residential_payback_updated.py
portal/
  portal-server.js, lender-portal-client-fix.js, package.json
reports/
  (original: 2 PDFs, solarthik-deep-dive.md)
  + COLD-STORAGE-FINANCING-FINDING.md, POULTRY-SIZING-FINDING.md,
    RESEARCH-BATTERY-COST-AND-RESIDENTIAL-SAM-CAC.md, RESIDENTIAL-CAC-PAYBACK-REVERSAL-FINDING.md
```

## Working norms established this session (keep doing these)

- **GitHub access**: no persistent credential mechanism exists for claude.ai chat sessions (checked — no MCP connector for GitHub either). The user pastes a fine-grained PAT in chat when a push is needed. Use it for that push only, then immediately reset the git remote back to the plain `https://github.com/z07makes/solarbd.git` URL regardless of whether the push succeeded. Never store it in memory or any file. Verify every push by cloning fresh and unauthenticated afterward — don't just trust the push output.
- **Real numbers over placeholders**: this session's highest-value work was replacing assumed figures with sourced ones (web search + live computation), even when the result was unfavorable. Keep doing this rather than defending existing numbers.
- **Verify by running, not by reading**: every fix in this session was checked by extracting the actual code and executing it — for HTML, that means pulling the script out and running it in Node with a document-call check, not just eyeballing the diff.
- The user does not want repeated security caveats once a workflow is established — state operational facts (e.g., "need the token to push") plainly, without re-relitigating.

## What's actually next (highest leverage first)

1. **A real battery vendor quote at 500kWh+ scale** (Fakir Technologies' "ZERO" line, Huawei, SAV Digital Power are all real, active Bangladesh suppliers per this session's research) — replaces the best current estimate with a fact, and is the single highest-value open item.
2. **A real, Bangladesh-specific residential CAC** — the India-proxy figure is better than the old placeholder but still a proxy; only an actual pilot fixes this properly.
3. **Cold storage's resilience value** stays qualitative until there's real outage-frequency/duration data to quantify it against — don't invent a number to fill the gap.
4. Older, still-open items from before this session: VFD retrofit costing is unsourced; the cold-storage facility-count discrepancy (400 vs. 365 facilities) is unresolved; `demos/solarthik-demo.html` still doesn't use the real engine at all.
5. Pilot outreach, fundraising conversations: still the user's own field work, not something a chat session can substitute for.
