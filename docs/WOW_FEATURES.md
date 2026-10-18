# WOW upgrades — engineering and judge evidence

## Selection criteria

We **did not implement all 20 research proposals**. For the deadline and team capacity, five coherent, math-backed interactions outperformed a scattershot backlog of unverified AI features.

| Proposal from the supplied research | Decision | Implementation |
|---|---|---|
| DeadlineShield 2.0 | Existing feature retained | Current date-indexed deterministic engine reused |
| RescueSolver | **Enhanced** | Enumerate options and verify bills + minimum reserve; no OR-Tools claim |
| Crisis Time Machine | **Built** | Four deterministic alternate futures, SVG financial trends |
| EssentialGuard | **Built** | Reserve constraints after bills + rescue verification |
| Decision X-Ray | **Built** | Deterministic scenario comparisons, reason codes, inputs and dates |
| Chaos Lab | **Built** | Seven executable assertions and read-only judge interface |
| FX Shock Absorber | **Built** | -20% to +20% fictional FX sensitivity |
| TransferTruth 2.0 | Existing feature retained | Equal sender-budget quote math; no live integrations |
| FamilyBridge 2.0 | Existing feature retained | Editable, approved local draft; no external sharing |
| Contradiction Hunter, Proof-to-Plan | Postponed | Would require robust file security/extraction and reconciliation |
| Agent Debate | Postponed | Two models talking to each other is not a deterministic audit |
| AidPath / ScamShield | Postponed | Verified policy content not yet assembled |
| TrustLedger replay | Postponed | Local audit exists; full event sourcing not implemented |
| LanguageBridge | Postponed | Correct multilingual numeric invariants need testing |

## Scenario definitions and accounting

- The core engine uses **string → Decimal** arithmetic and never asks Gemini to calculate totals.
- The EssentialGuard reserve is a *minimum after-obligation cash target*; it is not added as a future bill. It exposes the risk of meeting tuition obligations while retaining too little for essentials.
- **A conditionally feasible simulation is not a confirmed funding solution.** Additional family money and tuition extension still require actual consent, availability, and delivery.
- The Crisis Time Machine compares the earliest declared funding arrivals with latest arrivals, missing family funding, and a deterministic 5% USD/MYR decline. It does not assign likelihoods.
- The Decision X-Ray compares two deterministic projections under differing funding dates and shows **machine-readable reason codes**. It cannot validate whether the real family can pay or whether a university will approve deferral.
- Chaos Lab tests are run **only on click**, based on `demo_data.json`, independent of current user edits. A score of 7/7 means these seven fixture assertions passed, not that the financial system is safe for real money.
- FX Shock tests a range; it does not predict exchange rates or access providers.

## New endpoints

| Endpoint | Request | Returns |
|---|---|---|
| `POST /api/wow/essential-guard` | `scenario`, `arrival_overrides`, `essential_reserve_myr` | Per-obligation reserve checks |
| `POST /api/wow/rescue-solver` | Same + `capabilities` | Original rescue response + safety-checked candidates |
| `POST /api/wow/decision-xray` | `scenario`, `arrival_overrides` | Causal input changes, dates, compared figures |
| `POST /api/wow/time-machine` | `scenario`, `essential_reserve_myr` | Four read-only futures + chart points |
| `POST /api/wow/fx-shock` | `scenario`, `arrival_overrides`, `percent_change` | FX stress test and resulting tuition risk |
| `POST /api/wow/chaos-lab` | `{}` | Seven executed assertions and real pass/fail results |

All endpoints accept only synthetic records, and **none persist financial changes**. `chaos-lab` may write one audit entry describing the test run.

## Creative-design differentiation

This interface uses CampusFin Horizon's editorial fintech system: a student-life Pexels photo banner, deep teal/cobalt, warm off-white, generous financial typography, clean labeled risk states and restrained transitions. Creative interaction is **calculation-backed**: a living funding timeline, future sparkline comparisons, an essential-living safety floor, input-level causality and an adversarial testing arena. It intentionally avoids unverifiable 'first ever' novelty claims or a decorative chatbot.

**Do not claim:** independent security certification, statistically calibrated risk prediction, an actual optimal-solver algorithm, live FX prices, launched product, or award guarantee.
