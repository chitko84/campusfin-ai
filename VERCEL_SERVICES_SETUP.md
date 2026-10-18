# CampusFin AI — Vercel Services Deployment

## The selected configuration

- Vercel project Framework Preset: **Services**; Project Root Directory: **`./`**.
- **frontend** service at `/` (Vite SPA).
- **backend** service at `/api/*` (FastAPI at `backend/index.py` importing `app.main:app`).
- **No service bindings**: browser JavaScript calls same-origin relative `/api/...`; bindings work only in server-side functions, not Vite build output. The backend does not call the frontend.
- `frontend/src/main.jsx` uses `VITE_API_BASE_URL || ''`. Leave `VITE_API_BASE_URL` unset for same-origin deployment.

## Before pressing Deploy

1. Add `vercel.json` to the **repository root**, alongside `backend/` and `frontend/` (already included in this package).
2. Push changes to GitHub and refresh the Vercel import screen.
3. Choose **Services** as the Application Preset, with project Root Directory `./`. Do **not** choose `frontend` as root for this multiservice configuration.
4. Enable **Vercel Authentication → All Deployments** under Project → Security → Deployment Protection before publishing the API (Vercel announced Hobby support for production protection in September 2026). Visitors must have Vercel access; use an approved shareable link if appropriate. Avoid an unrestricted production public deployment while write endpoints and Gemini calls lack per-user authentication and rate limits.
5. For a protected Gemini demo, add `GEMINI_API_KEY` as a Vercel project environment variable, never `VITE_GEMINI_API_KEY`. Configure `GEMINI_MODEL` only if needed. Do not commit `.env`.
6. Deploy and check `https://YOUR-DOMAIN/api/health` and `https://YOUR-DOMAIN/`. Then test Scenario Lab and Copilot using verified synthetic data.

## Caveats (important)

- **SQLite is NOT persistent on Vercel Functions.** `backend/app/store.py` switches to `/tmp/campusfin_demo.sqlite3` while on Vercel, to prevent read-only filesystem errors. This storage can reset or diverge across function instances and deployments. It is *not* reliable for drafts, edits, audit logs, or multiple visitors. For reliable public use, replace SQLite with a managed database and add per-user isolation.
- The current backend has unprotected state-changing endpoints and the Gemini chat endpoint. **CORS alone is not authentication**. Never assume an exposed `/api/` is private just because services are internal by default; the `/api/` rewrite makes the backend publicly routable. Use Vercel Deployment Protection for a temporary restricted demo and add real authentication, per-user authorization, quotas and rate limits before making it public.
- `GET /api/health` does not verify database persistence or Gemini connectivity. Gemini status only confirms key presence until a real Copilot reply is received.
- Gemini API requests need network access and may have cost/quota/availability implications.
- Vite SPA fallback remains in `frontend/vercel.json`.

## Local development (unchanged)

Backend: `cd backend; py -m pip install -r requirements.txt; py -m uvicorn app.main:app --reload`.
Frontend (another terminal): `cd frontend; npm install; npm run dev`.

Or use Vercel CLI `vercel dev -L` from repository root after installing CLI.

## If you see 500 on backend routes

Check Vercel Runtime logs. Common culprits: dependencies, Python import entrypoint, and attempting to write outside `/tmp`. This version includes `backend/index.py` and uses `/tmp` by default in Vercel.
