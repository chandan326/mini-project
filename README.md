# AgriHealth AI / GreenHealth

Django 5.2 plant assessment app in `chandan326/mini-project`, deployed as Vercel project `greenhealth`.

## Photo workflow

- Select a crop, add **1-5 photos** from the gallery, drag and drop, or use the camera.
- Live camera preview supports capture, switch camera and close; a device-camera picker is also available. Camera access requires HTTPS (localhost is supported for development) and browser permission.
- Add and remove photos before submitting. Originals up to 20 MB are resized to at most 1600 pixels and compressed before upload. JPG, PNG and WebP are supported; convert HEIC first.
- Server validation requires a readable image at least 200 x 200 pixels, checks the combined 4 MB request limit, normalizes orientation and removes metadata before saving.
- Upload progress reflects the real request. Failed requests preserve selected photos for retry; there is no artificial analysis delay.
- Reports, photo endpoints and feedback require the creating account or guest browser session. Registering or signing in claims assessments from that guest session.

## Analysis modes

`DEMO_MODE=True` exercises upload, questionnaire, storage, feedback and PDF generation. It **does not identify disease** and returns no invented disease probabilities. Existing reports from the original random predictor are treated as demo reports.

For live image analysis, set `DEMO_MODE=False`, `GEMINI_API_KEY` and optionally `GEMINI_MODEL` (default `gemini-3.8-flash`). The server sends all selected photos and questionnaire in one Gemini Interactions API request. Structured output is validated against the selected crop's disease catalog. Unknown or uncertain conditions are never forced into a catalog disease. Provider errors return HTTP 503; they never silently produce a demo diagnosis. The model's confidence is not measured diagnostic accuracy. This integration needs a working account/key and live verification before real-world use.

No custom trained classifier or model weights are included. The seed catalog has limited coverage. Crop guides and AI estimates require agricultural expert verification.

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

Tests cover account flows, ownership, 1-5 uploads, malformed files, image rotation/metadata, repeated multipart fields, input errors, CSRF, feedback, PDFs on storage without filesystem paths, query counts, and mocked Gemini success/failure/invalid output. A passing mocked provider test does not verify a live API key or model account.

Official integration references: [Django storage](https://docs.djangoproject.com/en/5.2/ref/settings/#storages), [Gemini image inputs](https://ai.google.dev/gemini-api/docs/image-understanding), [structured responses](https://ai.google.dev/gemini-api/docs/structured-output).
