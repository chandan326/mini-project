# AgriHealth AI / GreenHealth

Django 5.2 plant assessment app in `chandan326/mini-project`, deployed as Vercel project `greenhealth`.

## Photo workflow

- Home and the crop directory have instant English/Hindi/scientific-name search with a clear button and result count.
- “How It Works” opens a keyboard-accessible video dialog with play/pause, replay, ±10s, speed, native volume/fullscreen, close and download controls. Closing stops playback. The 60-second 720p MP4 is bundled locally, uses female synthetic English narration and burned-in captions, and loads only when opened. No InVideo or paid API is used for the final video. Rebuild offline using `python scripts/build_tutorial.py` with Pillow and FFmpeg (Flite support).

- Select a crop, add **1-5 photos** from the gallery, drag and drop, or use the camera.
- The scanner includes 30 widely grown Indian field and horticultural crops, with English and Hindi names. Re-running `python manage.py seed_data` safely adds or updates the full list.
- Live camera preview supports capture, switch camera and close; a device-camera picker is also available. Camera access requires HTTPS (localhost is supported for development) and browser permission.
- Add and remove photos before submitting. Originals up to 20 MB are resized to at most 1600 pixels and compressed before upload. JPG, PNG and WebP are supported; convert HEIC first.
- Server validation requires a readable image at least 200 x 200 pixels, checks the combined 4 MB request limit, normalizes orientation and removes metadata before saving.
- Upload progress reflects the real request. Failed requests preserve selected photos for retry; there is no artificial analysis delay.
- Reports, photo endpoints and feedback require the creating account or guest browser session. Registering or signing in claims assessments from that guest session.

## Analysis modes

`DEMO_MODE=True` exercises upload, questionnaire, storage, feedback and PDF generation. It **does not identify disease** and returns no invented disease probabilities. Existing reports from the original random predictor are treated as demo reports.

For live image analysis, set `DEMO_MODE=False`, `GEMINI_API_KEY` and optionally `GEMINI_MODEL` (default `gemini-3.1-flash-lite`). The server sends all selected photos and questionnaire in one Gemini `generateContent` API request. Gemini can return a structured disease, pest, nutrient issue, environmental stress, healthy state, or unknown result even when the condition is absent from the local disease catalog. A local disease ID is accepted only for an exact match, and unknown or uncertain conditions are never forced into the catalog. Provider errors return HTTP 503; they never silently produce a demo diagnosis. The model's confidence is not measured diagnostic accuracy. This integration needs a working account/key and live verification before real-world use.

Live deployment settings (set the key only as a server-side secret):

```dotenv
AI_PROVIDER=gemini
GEMINI_API_KEY=<your-server-side-key>
GEMINI_MODEL=gemini-3.1-flash-lite
GEMINI_TIMEOUT_SECONDS=60
ENABLE_AI_GENERATION=true
DEMO_MODE=false
```

`DEMO_MODE=true` explicitly selects the demo workflow. Otherwise `ENABLE_AI_GENERATION=false` disables provider requests, and unsupported providers or missing/invalid model configuration fail before storing an assessment. The UI and health endpoint use the same readiness rules. `GEMINI_TIMEOUT_SECONDS` controls the provider read timeout (5–120 seconds, default 60; malformed values fall back to 60), with a separate 5-second connection timeout. The browser allows additional time for photo storage and upload. Deploy again after changing hosting environment variables.

Authentication, model-access and quota errors receive clear messages without returning provider response bodies or credentials. Incomplete, blocked or malformed AI responses never produce a completed report. The app does not retry provider requests automatically, avoiding duplicate billable calls.

No custom trained classifier or model weights are included. The local disease knowledge base has limited coverage; catalog-independent findings use cautious Gemini-generated field steps and an expert-referral message. Crop guides and AI estimates require agricultural expert verification before treatment decisions.

## Local development

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS / Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py seed_data
python manage.py runserver
```

The checked-in SQLite file is the existing demo seed database. Do not overwrite a production database with it. Export environment variables from `.env.example` through your shell or IDE; the application does not automatically load `.env` files.

## Production configuration

Use a stable `SECRET_KEY`, `DEBUG=False`, a valid **PostgreSQL** `DATABASE_URL`, and all three Cloudinary credentials (or `CLOUDINARY_URL`). A `MONGO_URI` alone does not configure this Django ORM app. Migrate and seed a new PostgreSQL database once using `python manage.py migrate` and `python manage.py seed_data`, with that database's environment active. Preserve and back up existing data before a database change.

On Vercel, `/tmp` SQLite/media are temporary and can disappear or differ between function instances. This fallback is for demos only; saved accounts/reports require PostgreSQL and Cloudinary. Cookie sessions also depend on a stable secret and shared database. `GET /api/health/` reports database connectivity, storage mode, persistence and configured analysis mode without exposing secret values. `production_ready` is a configuration check, not a live Gemini/Cloudinary transaction check.

Django 5.2 storage is configured with `STORAGES`. Image requests and PDF generation use the storage API, with bounded Cloudinary HTTP timeouts. Configure `CSRF_TRUSTED_ORIGINS` for additional custom domains. API submissions use Django CSRF protection and best-effort per-process throttles. For heavy production traffic configure a shared Django cache (e.g. Redis) for rate limits across instances.

## API

Preserve cookies between requests. First GET `/diagnosis/` to obtain a CSRF token from the hidden form input. Include it as `X-CSRFToken` for POST requests. Authenticated users sign in via `/accounts/login/`; guest ownership is bound to the session cookie.

| Endpoint | Method | Purpose |
| --- | --- | --- |
| `/api/health/` | GET | Connectivity and configuration readiness |
| `/api/crops/` | GET | Active crops, paginated |
| `/api/diseases/?crop_id=1` | GET | Active disease guides, paginated |
| `/api/diagnosis/create/` | POST multipart | `crop_id` and repeated `images` fields (1-5) |
| `/api/diagnosis/<uuid>/` | GET | Owner/session-only assessment |
| `/api/reports/<uuid>/` | GET | Owner/session-only PDF |
| `/api/diagnosis/feedback/` | POST | `diagnosis`, explicit `is_helpful`, optional `reason`/`comments` |

Creation accepts repeated `affected_parts` and `visible_symptoms`, plus `first_noticed`, `weather_condition`, `is_spreading`, `treatment_applied`, and optional `treatment_details`. The response contains `id`, `status`, `analysis_method`, `images`, `answers` and `result_url`. Invalid data returns 400, missing CSRF 403, unauthorized records 404, throttling 429 and unavailable services 503.

## Verification

```bash
python manage.py collectstatic --noinput
python manage.py check
python manage.py test
python manage.py makemigrations --check --dry-run
```

Tests cover account flows, ownership, 1-5 uploads, malformed files, image rotation/metadata, repeated multipart fields, input errors, CSRF, feedback, PDFs on storage without filesystem paths, query counts, the 30-crop seed catalog, catalog-independent findings, and mocked Gemini success/failure/invalid output. A passing mocked provider test does not verify a live API key or model account.

Official integration references: [Django storage](https://docs.djangoproject.com/en/5.2/ref/settings/#storages), [Gemini image inputs](https://ai.google.dev/gemini-api/docs/image-understanding), [structured responses](https://ai.google.dev/gemini-api/docs/structured-output).
