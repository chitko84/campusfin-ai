# FinTechathon 2026 — Submission Readiness Checklist
**Deadline in team materials:** 20 October 2026, 23:59 Beijing/Malaysia time (UTC+8). Verify submission portal time and any organizer update before submitting.

## Essential according to direct organizer clarification shared with team
- [ ] Technical documentation — initial draft: `docs/TECHNICAL_DOCUMENTATION.md` (and `submission/Technical_Documentation.docx/pdf`)
- [ ] Presentation deck ≤10 minutes — initial draft: `submission/CampusFin_AI_Pitch_Deck.pptx/pdf`
- [ ] Ensure team name, registered member names, university, contact and official links are correct.

## Published checklist potentially requires more than the organizer email
The team’s rulebook research identified source code/README/test cases, security self-assessment and execution evidence in the official checklist, with only the video clearly marked optional. An organizer email reportedly differed. **Treat this as unresolved; verify official instructions and submit additional materials where accepted.**

- [ ] Complete GitHub source link with README and run instructions.
- [ ] Security self-assessment (`docs/SECURITY_SELF_ASSESSMENT.md`), including unimplemented production controls.
- [ ] Execution evidence: genuine automated test outputs, screenshots, logs and demo recording.
- [ ] Optional demonstration video ≤5 minutes, only after required submissions are protected.
- [ ] Verify eligibility and maximum number of registered participants; distinguish registered team from helpers.
- [ ] Test the exact ZIP on Windows using fresh extracted directory.
- [ ] Verify backend test output and frontend Vite production build.
- [ ] Confirm whether live Gemini works, or show labeled offline fallback.
- [ ] Use simulated-data disclaimers and photographer license credits; no real student financial information.
- [ ] Remove `.env`, API keys, `.sqlite3`, `node_modules`, screenshots showing secrets and local virtual environments from source ZIP.
- [ ] Make first submission before deadline, then revise only if portal supports updates.

## Evidence status (as packaged)
- [x] Backend pytest evidence: 72 passing tests captured locally.
- [x] Backend source, synthetic data, tests, docs and reproducible instructions packaged.
- [x] Frontend JSX syntax / transpilation checks captured locally.
- [ ] Full Vite build **not verified in this environment** (npm timed out).
- [ ] Visual browser/device QA **not verified in this environment**.
- [ ] Real Gemini API call **not independently verified in this Phase 5 environment** (user reports it working on Windows).
- [ ] Production auth/regulated compliance **not implemented** (do not claim otherwise).
