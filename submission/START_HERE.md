# Start CampusFin AI Phase 5 on Windows

Open the complete extracted `CampusFin_AI_Phase5_Competition_Ready` folder in VS Code. Use **two terminals**.

**Terminal 1: Python backend**
```powershell
cd backend
py -m pip install -r requirements.txt
# Optional, only to enable live Gemini:
$env:GEMINI_API_KEY="YOUR_EXISTING_PRIVATE_KEY"
$env:GEMINI_MODEL="YOUR_WORKING_MODEL_ID"
py -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

**Terminal 2: React frontend** (start at the project root)
```powershell
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`. On the top bar click **Guided demo**. On mobile, the star-shaped top-bar button opens the same 6-step tour.

**Tests:**
```powershell
cd backend
$env:PYTHONPATH="."
py -m pytest -q
cd ..\frontend
npm run build
```

**Demo photo cache (optional):** from root `py scripts/download_photos.py`.

The ZIP intentionally excludes the local SQLite database and your API key. Startup creates the synthetic database again. Backends must remain local-only: no authentication or user isolation is implemented.

**Important:** This Phase 5 code was checked using 72 backend tests and JSX/CSS source validation, but npm dependency download timed out in the production environment used to prepare this package; you must complete frontend build/browser testing locally.
