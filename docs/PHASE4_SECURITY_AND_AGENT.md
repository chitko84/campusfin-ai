# CampusFin AI — Phase 4: Agent Tooling & Security Self-Assessment (Prototype)

Date: 18 October 2026. Status: **implementation and test evidence, not a production security certification.** All values and profiles are synthetic.

## Architecture

`React chat UI → /api/agent/chat → FastAPI permission gate → Gemini generateContent REST → read-only Python tool registry → verified financial engine`.

- Default model: `gemini-3.8-flash` (can be overridden with `GEMINI_MODEL`). Uses `v1beta/models/{model}:generateContent` and Google API function declarations/responses. The API key stays in the backend environment and is never transmitted to the browser.
- No key: returns **OFFLINE GUIDE** with trusted computed facts. This is not represented as live AI.
- Invalid response, model outage, rate limit or unsafe model action: fails closed to labeled guidance or an explicit blocked action.
- Finance calculations use Python `Decimal` and existing Phase 1–3 computations; Gemini never computes displayed financial figures.

## Permission tiers

| Tier | Examples | Implemented control |
|---|---|---|
| 0 — read/simulate | financial overview, cash-flow forecast, shortfall detection, rescue simulation, simulated quote comparison | Model may invoke **only** allowlisted Tier 0 tools; all validate their arguments; model has no SQLite store handle |
| 1 — local draft | FamilyBridge funding request, university extension draft | User opens the Requests UI and saves an editable draft; agent can preview a draft without saving it. User must explicitly approve the saved draft. Never sent. |
| 2 — ledger mutation | create/edit/delete a synthetic funding source or obligation | Available through local student UI only; never registered with Gemini. The server enforces schema validation and locks settled historical income. Edits are audit logged. **No account login or independent API-user authentication exists.** |
| Unavailable | real transfer, bank settlement, actual messaging, university approvals | No backend endpoints or integration exist |

## Tool registry

`get_financial_overview`, `run_cashflow_forecast`, `detect_shortfalls`, `generate_rescue_options`, `compare_transfer_quotes`, `calculate_required_sender`, `preview_funding_request`.

All tools are explicitly read-only. Even a model-generated fake `delete_funding` or `mark_funding_settled` functionCall cannot execute. Gemini turns are limited to 4 request rounds and 6 total tool calls. Chat history is capped at 4 entries and user messages at 1,200 characters.

## Important threat model and honest limitations

1. **Prompt injection:** User-supplied messages and financial source text are untrusted. The model gets bounded instructions, and most importantly has only side-effect-free tools. This prevents AI-driven unauthorized ledger changes; it does not provide a mathematical guarantee against all prompt-injection effects on conversational wording.
2. **Hallucination:** Model-generated text containing numeric financial figures is rejected and replaced with a deterministic explanation. The interface renders verified fact cards directly from trusted server calculations. Model text may still contain nonnumeric inaccuracies; users should check the evidence panel.
3. **Exfiltration:** Configuring Gemini sends **synthetic text and financial inputs** to Google's external API. Do not use real student data or secrets. Read Google's free-tier data usage and privacy terms before selecting a service.
4. **Authentication:** The API is intentionally restricted to a local, single-demo-user workflow without account authentication or multi-user authorization. Anyone who can reach the API can call its student-edit routes; do **not** bind it to 0.0.0.0 or deploy publicly. UI controls are not sufficient for production access control.
5. **Approval:** User editing forms require clicking Save, deletes use an explicit browser confirmation, and locally approving a draft requires a separate confirmation checkbox. The model cannot perform any of these mutations. This is demo consent, not verified user identity.
6. **Audit:** local SQLite records agent turns (mode and tools only), user record edits and draft approvals. Content and API keys are intentionally not stored in the audit log. Audit rows can be deleted by a local user/reset; the log is not tamper-evident. Never claim otherwise.
7. **Transfers:** All quotes, costs and arrival times are clearly hypothetical; no payment action exists.
8. **Rate limits:** Free tier quota, project/region eligibility, and model availability can change. Explicit offline guidance remains operational without Gemini.
9. **No production assurance:** No penetration testing, real KYC, banking compliance assessment or end-to-end deployed-frontend QA has been completed.

## Actual execution checks

The local command `python -m pytest -v` runs previous phases and new Phase 4 tests. It checks ledger immutability on blocked AI calls, real function-call roundtrip *with mocked Gemini transport*, unverified-number filtering, malformed arguments, local offline fallback, request bounds, quote arithmetic, draft non-delivery, and audit event creation.

**Mocked Gemini protocol tests do not prove that a real Gemini API key works**. Set the key and conduct a real smoke test before marking live integration completed.

## Real API smoke-test checklist (to be completed on developer's Windows PC)

- [ ] `GET /api/agent/status` reports configured, without ever showing the key.
- [ ] Ask "What happens if my family transfer is delayed?" with the Stress scenario.
- [ ] Confirm Copilot displays **Gemini response** and `live_ai: true`.
- [ ] Confirm tool trace includes `detect_shortfalls` or `generate_rescue_options` for a relevant question.
- [ ] Open ProofCard and check RM 1,000 gap in delayed Amina fixture.
- [ ] Ask to mark funding settled without student action; response must be blocked, ledger unchanged.
- [ ] Test prompt-injection text in a funding source title; ledger must remain unchanged.
- [ ] Disconnect the API key; confirm clearly labeled offline mode works.
- [ ] Run `npm run build` and browser check on mobile + desktop.
- [ ] Capture screenshots, logs and an explicit pass/fail matrix; do not claim any unexecuted test has passed.
