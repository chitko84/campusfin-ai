# CampusFin AI — Phase 2 handoff

## Completed

1. Updated React experience — app shell, responsive dashboard, Financial Horizon, Scenario Lab, funding and bill editors, ProofCard modal, safe reset and explicit placeholders for unfinished AI features.
2. Python FastAPI API upgraded to persistent demo record CRUD with SQLite; includes validation, finance recompute, proof endpoint and local reset.
3. Existing Phase 1 engine retained. Phase 1 historical-income and projected-cash rules preserved.
4. Backend regression suite **20 passed**; TypeScript JSX parser reports **0 diagnostics**; CSS parser reports **0 errors**.

## Feature acceptance

- [x] Home baseline scenario RM 449 projected after tuition when on-time transfer is assumed
- [x] Delayed transfer causes RM 1,000 shortfall
- [x] Funding add/update/delete API with on-disk persistence
- [x] Bill add/update/delete API with on-disk persistence
- [x] Funding and bills form integration in frontend source
- [x] Scenario switching and temporary date overrides in frontend source
- [x] ProofCard exposed for covered and at-risk calculations
- [x] Local synthetic-data reset
- [x] API tests and mathematical fixtures
- [ ] Frontend `vite build` verified on developer machine (npm registry unavailable here)
- [ ] Browser click-through verified on developer machine (browser restrictions here)

## Developer quick-check before Phase 3

1. Run `npm install` and `npm run build` in `/frontend`.
2. Run backend + frontend. Open Chrome DevTools → Console. Ensure zero JavaScript errors.
3. Visit `/funding` via the app nav, edit the family base/stress dates to 28 Oct and save. Refresh and confirm the data persists.
4. Verify `Home → Show the math` and `Plan → Show the math` for covered/delayed cases.
5. Verify editing settled historic wages is blocked.
6. Reset the demo to restore the original state.
7. Capture actual screenshots and logs before claiming completed execution evidence.

## Known limitations

- Editing unsettled funding from the current demo date onward is supported; past-due funding status management is deferred.
- Only MYR-denominated obligations are supported; funding MYR/USD is supported through a simulated conversion.
- UI does not yet implement every modal from the full 54-section wireframe; Phase 2 concentrates on the functional planning workflow.
- No external services or live AI yet.
- Local SQLite's JSON document storage is simple and not suitable for multi-user production access.

## Next Phase 3 dependency

Add pure deterministic `rescue.py` using funding/obligation data and scenario overrides. Validate each recovery option by re-running `forecast`; don't claim pending tuition extensions or unconfirmed remittances as guaranteed solutions. Return a Funding Gap Summary when no option can be verified feasible.
