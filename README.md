# CampusFin AI — Phase 5 Competition-Ready Source Package

**Predict. Rescue. Prove.** A transparent local-only student-finance demonstration for FinTechathon 2026, with responsive photo-enhanced UI, Gemini tool-calling, five innovation features, and a new guided judge-presentation mode.

**Start here:** `submission/START_HERE.md` (two-terminal Windows instructions).  
**Judge demo:** Click **Guided demo** in the app. The six-scene tour navigates the real screens and uses live deterministic calculations.  
**Technical documentation:** `docs/TECHNICAL_DOCUMENTATION.md`  
**Security report:** `docs/SECURITY_SELF_ASSESSMENT.md`  
**Editable slide deck:** `submission/CampusFin_AI_Pitch_Deck.pptx`  
**Presentation script:** `submission/PRESENTATION_NOTES.md`  
**Submission checklist:** `submission/SUBMISSION_CHECKLIST.md`  
**Automated evidence:** `evidence/phase5-pytest.txt` and frontend syntax/build attempt reports.

## Phase 5 additions
- Six-scene Guided Judge Demo overlay with responsive accessibility improvements, presenter cues, and navigation among real application pages.
- Stronger Decimal input validation: malformed and extremely large numeric values are rejected instead of triggering unhandled Decimal errors.
- 9 additional automated backend security/input tests (72 total passed).
- A full presentation/technical documentation/security/evidence handoff bundle.
- Original Phase 4 WOW Edition, photo placements, scenario-aware Gemini, Financial Horizon, RescueSolver, EssentialGuard, Decision X-Ray, Crisis Time Machine, FX Shock, Chaos Lab and TransferTruth are retained.

## Verification honesty
- **Verified:** 72 backend pytest passes; updated frontend JSX source transpilation; relative import checks; no secrets/runtime DB in distributable; docs and slide output.
- **Not verified here:** npm-dependent Vite build and real graphical-browser QA (npm installation timed out); live Gemini request for this exact Phase 5 build. The user reported their previous Phase 4 build was functioning on Windows. Run local checks before submitting.
- **Not implemented:** authenticated accounts, regulated financial advice, live FX quotes, bank integrations, payments, email dispatch, real financial data handling, continuous monitoring.

> This ZIP is the complete source project, not a patch. Use a **new folder**, install dependencies, set `GEMINI_API_KEY` in the backend terminal if needed, and keep API on `127.0.0.1`.
