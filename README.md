# AI-Powered Plant Disease Detection & Farmer Assistance Platform

A professional, production-ready, responsive web application for farmers that detects common plant diseases using 5-image ensemble analysis, farmer symptom questionnaire correlation, and verified agricultural knowledge base guidance.

---

## Key Features

1. **5-Step Mobile-First Diagnosis Wizard**:
   - **Step 1: Select Crop** (Searchable crop grid from database).
   - **Step 2: Upload 5 Photos** (Multi-angle close-up, stem, leaf, whole plant with camera trigger & blur detection).
   - **Step 3: Farmer Questionnaire** (Symptom onset, affected parts, visible symptoms, spreading status, weather, treatment).
   - **Step 4: Animated Analysis** (Visual ML ensemble + symptom correlation + knowledge base verification).
   - **Step 5: Assessment Result** (Disease prediction, confidence gauge, natural explanation, symptoms, immediate care, prevention, and expert consultation guidance).
2. **Modular ML Architecture (`ml_model/`)**:
   - Abstract `PlantDiseasePredictor` interface.
   - `DemoPredictor` for college/prototype presentation.
   - Image quality preprocessor (blur, contrast, brightness, resolution validation).
   - 5-image probability ensemble & inter-image consistency checker.
   - Low-confidence flag handling (< 60% confidence triggers warning & retake advice).
3. **Verified Knowledge Base (`knowledge_base/`)**:
   - Disease profiles, field symptoms, environmental causes, immediate management, prevention, and monitoring rules.
4. **Downloadable PDF Diagnostic Reports (`reports/`)**:
   - Pure-Python `ReportLab` implementation generating structured PDF reports.
5. **Farmer & Admin Dashboards**:
   - Auth system for farmers to track diagnostic history.
   - Customized Django Admin panel managing Crops, Diseases, Knowledge Base, ML models, and Feedback.
6. **Multilingual i18n Support**:
   - Native English & Hindi (`en` / `hi`) support.

---

## Local Setup & Quick Start

```bash
# 1. Clone repository & navigate to directory
cd "c:/Users/chand/Desktop/mini project"

# 2. Activate Virtual Environment (or create via py -3 -m venv .venv)
.\.venv\Scripts\python.exe -m pip install -r requirements.txt

# 3. Apply Database Migrations
.\.venv\Scripts\python.exe manage.py makemigrations
.\.venv\Scripts\python.exe manage.py migrate

# 4. Seed Database with Default Crops & Disease Knowledge Base
.\.venv\Scripts\python.exe manage.py seed_data

# 5. Create Superuser (Admin Account)
.\.venv\Scripts\python.exe manage.py createsuperuser

# 6. Run Development Server
.\.venv\Scripts\python.exe manage.py runserver
```

Open browser at `http://127.0.0.1:8000/`.

---

## Running Unit Tests

```bash
.\.venv\Scripts\python.exe manage.py test
```

---

## Docker Deployment

```bash
docker-compose up --build
```
