# CampusFin Phase 3 — Engineering Handoff

## Included

All Phase 1/2 functionality plus a deterministic rescue simulator (`app/rescue.py`), auditable sample quote comparison, funding request drafts, local activity logging, and four new responsive frontend screens.

## Key API endpoints

| Endpoint | Description |
|---|---|
| `POST /api/rescue` | `scenario`, `arrival_overrides`, optional `capabilities`; returns conditional options, no-plan path and computed gap |
| `POST /api/transfers/compare` | `total_sender_budget_usd` string; equal-budget comparison of fictional quotes |
| `POST /api/transfers/required-sender` | `recipient_target_myr`, `quote_id`; cent-accurate minimum total sender budget |
| `POST /api/drafts` | `kind` family or university plus scenario; stores private draft, no sending |
| `GET /api/drafts` | Lists local saved drafts |
| `PUT /api/drafts/{id}` | Edits unapproved draft |
| `POST /api/drafts/{id}/approve` | `confirmed: true`; marks draft approved locally, not sent |
| `GET /api/audit` | Recent local events |
| `POST /api/reset` | Resets seed, clears drafts and audit |

## Security invariants and engineering decisions

- No real transfers or messages.
- API offers no settlement endpoint. Existing Phase 2 source editing only covers expected/in-transit funds; settled historical wages remain immutable.
- Simulated plan modifications occur in deep copies of the finance document, not persisted to the ledger.
- All money uses Decimal and cents, with reverse-transfer budgets rounded upward and verified with a forward quote.
- `confirmed_solution` is always false, and every potentially successful proposal is marked `conditional` until externally confirmed.
- A no-feasible-option result is available by disabling all three opportunity flags in the Rescue workspace. It does not manufacture funding availability.
- Approving a draft requires an explicit checkbox + request body confirmation. A draft can never be edited after approval.
- Access controls are not production-grade: local single-person demo only, never deploy publicly without identity checks.

## Test evidence

`backend/tests/test_phase3.py` includes cases for confirmed vs projected, zero viable options, fee mode comparisons, exact transfer budget sizing, illegal inputs, editing approved drafts, denied unconfirmed approval, reset, and local ledger immutability.

Run `python -m pytest -v` from `backend` before capturing evidence for the competition. Capture **real logs**, not an imagined screenshot.

## Implementation order next phase

1. Run frontend package install and build on Windows; fix runtime interactions if needed.
2. Add bounded Gemini agent tools that call only proven finance functions and cannot mutate the ledger.
3. Add strict server-side authorization for any future state modifications.
4. Expand tests with prompt-injection and tool-call validation.
5. Collect screenshot evidence and draft submission documentation.
