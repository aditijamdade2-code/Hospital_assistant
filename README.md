# Hospital OPD Multilingual Voice Assistant (Phase 1: Text MVP)

> **CLINICAL DISCLAIMER & SAFETY NOTICE**  
> This system is strictly an **assistive workflow prototype**. It is **NOT** an autonomous diagnostic tool and must **NOT** independently prescribe medication, make unverified clinical judgments, or replace authorized medical doctors and nursing staff. All clinical protocols and red-flag rules are marked as **`DEMO / REQUIRES CLINICAL VALIDATION`**.

---

## 1. Project Overview

The **Hospital OPD Multilingual Voice Assistant** helps patients and hospital staff communicate smoothly during outpatient (OPD) and first-aid intake. The system:
- Collects structured patient complaints in **English**, **Hindi**, and **Marathi** (including mixed colloquial input like Hinglish).
- Normalizes complaints into language-agnostic structured clinical records (`chief_complaint`, `body_part`, `symptoms`, `duration`, `severity`, etc.).
- Evaluates deterministic, hospital-approved clinical protocols (P001–P008) to ask missing follow-up questions and provide approved first-aid advice placeholders.
- Evaluates deterministic clinical safety red-flags (e.g. arterial bleeding, anaphylaxis, chest pain) with **explainable escalation audit records**.
- Updates the clinical staff dashboard in real time via **WebSockets** without requiring manual page refreshes.

---

## 2. Architecture

```
Patient Text Input (EN / HI / MR)
       │
       ▼
LLM Extraction Layer (Provider-Independent: Mock / OpenAI)
       │  (Extracts structured information without hallucination; unknowns remain null)
       ▼
Structured Encounter Representation
       │
       ├────────────────────────────────────────┐
       ▼                                        ▼
Deterministic Protocol Engine            Deterministic Safety Engine
  - Matches P001-P008                      - Evaluates Red-Flag Rules (RF-001 - RF-009)
  - Identifies missing fields              - Sets Priority: NORMAL, NEEDS_REVIEW,
  - Evaluates follow-up questions            PRIORITY, IMMEDIATE_ESCALATION
  - Selects approved first-aid advice      - Halts questioning on critical danger
       │                                        │
       └───────────────────┬────────────────────┘
                           ▼
          Encounter State & Audit Log Update
                           │
             ┌─────────────┴─────────────┐
             ▼                           ▼
Patient Interface Response       Real-Time WebSocket Broadcast
(Guidance / Follow-up Qs)        (Staff OPD Triage Dashboard)
```

---

## 3. Technology Stack

- **Backend**: Python 3.11+, FastAPI, SQLAlchemy (Async), Pydantic v2, SQLite (`aiosqlite`) default with seamless PostgreSQL (`asyncpg`) support.
- **Frontend**: Next.js 14, React 18, TypeScript, Tailwind CSS, Lucide icons.
- **Real-time**: WebSockets for staff dashboard updates.
- **AI Abstraction**: Clean provider interface (`LLMProvider`) with deterministic `MockLocalLLMProvider` and `OpenAIProvider`.

---

## 4. Setup & Installation

### Prerequisites
- Python 3.11+
- Node.js v18+ and npm

### Backend Setup
```bash
# 1. Navigate to backend
cd backend

# 2. Create virtual environment
python -m venv venv

# 3. Activate virtual environment
# On Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# On Linux/macOS:
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Run tests to verify
pytest backend/tests
```

### Frontend Setup
```bash
# 1. Navigate to frontend
cd frontend

# 2. Install dependencies
npm install

# 3. Build for production check
npm run build
```

---

## 5. Environment Variables (`.env`)

Copy `.env.example` to `.env`:
```ini
ENVIRONMENT=development
LOG_LEVEL=INFO
SECRET_KEY=opd-assistant-secret-key-32chars

# Database: SQLite (default local) or PostgreSQL
DATABASE_URL=sqlite+aiosqlite:///./hospital_assistant.db
# DATABASE_URL=postgresql+asyncpg://hospital_user:hospital_password@localhost:5432/hospital_opd

# AI Configuration
LLM_PROVIDER=mock          # Options: "mock" (zero external deps) or "openai"
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4o-mini
OPENAI_BASE_URL=https://api.openai.com/v1

# Security / CORS
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Protocols Directory
PROTOCOLS_DIR=protocols/examples

# Frontend environment variables
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000/api/v1/ws/staff
```

---

## 6. Running Locally

### Start Backend
From repository root with venv activated:
```powershell
python backend/run.py
```
- API runs at: `http://localhost:8000`
- Interactive Swagger / OpenAPI docs: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/health`

### Start Frontend
From repository root in another terminal:
```bash
cd frontend
npm run dev
```
- Patient Intake Screen: `http://localhost:3000/patient`
- Staff OPD Dashboard: `http://localhost:3000/staff`
- Landing Selector: `http://localhost:3000`

---

## 7. Running with PostgreSQL via Docker

If Docker is installed:
```bash
docker-compose up --build
```
This boots:
1. PostgreSQL on port 5432
2. FastAPI Backend on port 8000
3. Next.js Frontend on port 3000

---

## 8. Running Automated Tests

Run the full pytest suite from the repository root:
```powershell
.\backend\venv\Scripts\pytest backend\tests -v
```

Includes:
- `test_schemas.py`: Encounter, Patient, Message, and Safety schema validations.
- `test_protocol_engine.py`: Protocol matching, missing field detection, and guidance retrieval.
- `test_safety_engine.py`: Deterministic red-flag triggers, arterial spurting, chest pain, and anaphylaxis.
- `test_llm_extraction.py`: Extraction across English, Hindi, Marathi, and Hinglish without hallucination.
- `test_encounter_workflow.py`: End-to-end integration of intake, messages, staff acknowledgment, and audit history.

---

## 9. Extending the System

### Adding a New Protocol
1. Create a new JSON file in `protocols/examples/` (e.g. `P009_head_injury.json`):
```json
{
  "protocol_id": "P009",
  "name": "Minor Head Injury",
  "version": "1.0",
  "category": "TRAUMA_FIRST_AID",
  "clinical_validation_status": "DEMO / REQUIRES CLINICAL VALIDATION",
  "keywords": ["head hit", "bump on head", "sir pe chot"],
  "required_fields": ["loss_of_consciousness", "vomiting", "headache_severity"],
  "questions": [
    {
      "field": "loss_of_consciousness",
      "text": "Did the patient pass out or lose consciousness, even for a second?",
      "text_hi": "क्या मरीज एक सेकंड के लिए भी बेहोश हुआ था?",
      "text_mr": "रुग्ण एका क्षणासाठीही बेशुद्ध पडला होता का?"
    }
  ],
  "guidance": [
    {
      "step": 1,
      "instruction": "DEMO PLACEHOLDER: Keep patient sitting upright and apply ice pack wrapped in a towel.",
      "instruction_hi": "डेमो सूचना: मरीज को सीधा बिठाएं और तौलिए में बर्फ लपेटकर लगाएं।",
      "instruction_mr": "डेमो सूचना: रुग्णाला सरळ बसवून ठेवा आणि टॉवेलमध्ये गुंडाळलेला बर्फ लावा."
    }
  ],
  "escalation": {
    "default_priority": "PRIORITY",
    "trigger_conditions": ["loss_of_consciousness_true", "repeated_vomiting"]
  }
}
```
2. Reload protocols via backend restart or calling `protocol_loader.load_all()`.

### Adding an AI Provider
1. Inherit from `LLMProvider` in `backend/app/services/llm/base.py`.
2. Implement `extract_information` and `generate_response`.
3. Register the new provider in `backend/app/services/llm/factory.py`.

### Adding an STT Provider (Phase 2)
1. Define abstract base class `SpeechToTextProvider` in `backend/app/services/stt/base.py`:
   - Method: `async def transcribe(audio_bytes, language) -> str`
2. Implement providers: e.g. `WhisperSTTProvider`, `BhashiniSTTProvider`, `GoogleCloudSTTProvider`.

### Adding a TTS Provider (Phase 2)
1. Define abstract base class `TextToSpeechProvider` in `backend/app/services/tts/base.py`:
   - Method: `async def synthesize(text, language) -> bytes`
2. Implement providers: e.g. `ElevenLabsTTSProvider`, `BhashiniTTSProvider`, `EdgeTTSProvider`.
