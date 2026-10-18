# CampusFin AI — Five-minute judge demonstration

## Preflight (before recording)
1. Copy the ZIP to your own laptop and extract it. Do not use an old Phase 4 directory by accident.
2. Start FastAPI on `127.0.0.1:8000` and Vite on `localhost:5173`; confirm API `/api/health` and UI load.
3. Run `npm run build`, `py -m pytest -q`, confirm clean tests. Check browser at 390px and 1440px.
4. Reset the demo. This returns Amina’s original synthetic data and clears local drafts/audit entries. For evidence, do a complete flow **after** resetting.
5. If using Gemini, set the backend env var **privately**. Confirm a successful Gemini response inside Copilot. Avoid showing API keys in screenshots.
6. Cache images with `py scripts/download_photos.py` in advance if demo network is unreliable. Gradient fallback works without images.

## Scripted timing
- **0:00–0:35**: CampusFin home. Explain fixed tuition deadline versus delayed cross-border funding. Open Guided Demo.
- **0:35–1:15**: On-screen Financial Horizon. Move Base to Stress: the family USD 350 shifts to 28 October; RM 1,000 tuition gap emerges for 25 October. Show the math.
- **1:15–2:05**: Rescue Solver. Explain conditional options and EssentialGuard reserve. Do not claim transfer or extension has happened.
- **2:05–2:40**: Decision X-Ray. Explain how one changed arrival date triggered the gap; inspect provenance.
- **2:40–3:15**: TransferTruth synthetic quote comparison; optional reverse calculation.
- **3:15–4:10**: Copilot asks hypothetical arrival date; show verified Python fact card. If Gemini is down, say the offline fallback is deliberately labeled.
- **4:10–4:40**: Chaos Lab with **real** pass/fail results. No hardcoded outcomes.
- **4:40–5:00**: Audit history, no real payments, call to action and closing tagline.

## Fallbacks
- If `npm install` fails, run locally from a machine where dependencies were already installed and verified; **do not represent untested UI as complete**.
- If internet or hosted photos fail, use existing gradient backgrounds or cache images locally before the presentation.
- If Gemini rate limits or model is unavailable, show the labeled local guide and recorded live-success evidence if it actually exists.
- If a feature becomes unstable, prioritize the working forecasting → rescue → explanation flow and keep security/evidence claims accurate.

## Capture checklist
Record genuine screenshots or 1080p screen recording of: dashboard, stress scenario and RM 1,000 gap, ProofCard, EssentialGuard, transfer quote, Copilot tool activity, Chaos Lab result, security refusal, audit trail and test terminal. None are fabricated in this ZIP.
