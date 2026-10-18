# CampusFin AI Roadmap — Status at Phase 4

- **Phase 1:** deterministic financial engine and reproducible Amina scenario — complete and backend tested.
- **Phase 2:** editable funding/obligations, SQLite persistence, Financial Horizon and Scenario Lab — complete in source; backend tested; complete browser build not independently verified.
- **Phase 3:** conditional rescue simulations, honest no-plan Funding Gap Summary, simulated equal-budget TransferTruth, editable request drafts, audit history — complete in source; backend tested.
- **Phase 4:** Gemini 3.8 Flash REST function-call orchestration, read-only tool registry, financial figure provenance cards, server-side denied AI mutations, capped model call budgets, offline guidance, audit of agent calls and user ledger edits, additional security tests — complete in source and backend tested. Real Gemini API needs a developer-supplied key; no live Gemini request has been verified in this environment.
- **Phase 5:** npm install + production build on Windows, 390px/1440px browser QA, usability and accessibility checks, mandatory technical documentation, presentation deck, security self-assessment, captured execution evidence and submission — pending.

**Important:** Phase 4's AI has only Tier 0 read-only tools. Tier 1 drafts and student-led record edits are handled via explicit UI controls. The localhost prototype does not have account authentication, general-purpose user authorization, KYC, live accounts, sending or payment capabilities. Do not publish the backend publicly.

## Phase 4 WOW / Photo-Enhanced update

The existing Phase 4 project was extended with the premium Innovation Studio:
EssentialGuard + reserve-aware RescueSolver, Crisis Time Machine, Decision X-Ray,
Chaos Lab, and FX Shock sensitivity testing. Nine existing Pexels photo placements
and source credits remain. Full details: `docs/WOW_FEATURES.md`.

Backend: 53 tests passed. Frontend: JSX transpilation and CSS parse passed, but
full Vite build/browser QA remain to be completed on Windows.
