# LegalEase

LegalEase is a local AI-assisted legal document drafting application. A Streamlit interface collects the document type, parties, terms, and effective date; a FastAPI service sends the request to Google Gemini; the user can review, edit, and download the resulting draft as TXT, DOCX, or PDF.

## Features

- Document types include freelance contracts, NDAs, employment documents, lease agreements, and custom types.
- Required fields are validated in the UI and API. Semicolon-separated terms are preserved in the generation prompt.
- Generated content can be edited before export. All three download formats use the current edited text.
- Styled HTML preview, branded DOCX/PDF headers and footers, automatic PDF page numbering, and local logo asset.
- API and AI errors are returned without revealing secrets or provider diagnostics.

## Architecture

```text
Streamlit (app.py) -> FastAPI (main.py / routes.py) -> GeminiDocumentGenerator
                                     -> DOCX/PDF/text formatters
```

## Folder structure

```text
ai_core/                 Gemini integration
assets/                  Local branding and output directory
utils/                   Text, DOCX, HTML, and PDF formatting
app.py                   Streamlit UI
main.py, routes.py       FastAPI app and endpoints
tests/                   Automated backend and export checks
requirements.txt         Runtime dependencies
```

## Prerequisites

- Python 3.10 or newer (Python 3.11 or 3.12 recommended for broad package compatibility).
- A Google Gemini API key from Google AI Studio for live document generation.

## Install on Windows PowerShell

Run these commands from the project directory:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `.env` and set `GEMINI_API_KEY` to your own key. Never commit `.env`. The optional `GEMINI_MODEL` defaults to `gemini-3.5-flash-lite`; `BACKEND_URL` defaults to `http://127.0.0.1:8000`.

### Gemini model compatibility

The original project document names Gemini 1.5 Pro and the older `google-generativeai` SDK. Google's current SDK is `google-genai`, imported as `from google import genai`, and uses `client.models.generate_content(...)`. The implementation uses that SDK and defaults to `gemini-3.5-flash-lite`, a current model recommended for new projects in Google's catalog. Gemini 3.8 Flash is also supported and can be selected with `GEMINI_MODEL`; during verification it returned a temporary capacity 503 while Flash-Lite completed a real generation request. [Google Gen AI SDK / generate content](https://ai.google.dev/gemini-api/docs/generate-content) · [Gemini model catalog](https://ai.google.dev/gemini-api/docs/models)

## Run the application

Open two PowerShell terminals in the project directory and activate `.venv` in both.

Backend:

```powershell
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000/docs` to inspect and call `GET /` and `POST /generate`.

Frontend:

```powershell
streamlit run app.py
```

## Example API request

```json
{
  "document_type": "Freelance Work Contract",
  "parties": "Jane Doe (Service Provider), TechNova Inc. (Client)",
  "terms": "Payment within 30 days; Confidentiality must be maintained; Either party may terminate with 15 days notice",
  "dates": "10 April 2026"
}
```

The response contains `document_type` and generated `content`. Input length limits and blank values are validated by FastAPI. Missing Gemini configuration returns HTTP 503; generation/provider failures return HTTP 502; invalid inputs return HTTP 422.

## Output formats

- TXT: UTF-8 text.
- DOCX: Times New Roman body, headings, numbered clauses, local branding, and footer.
- PDF: branded header/footer, wrapped paragraphs, numbered pages, and multiple-page layout.

The edit control is backed by Streamlit session state, so edits are retained while switching between preview and downloads.

## Tests

```powershell
python -m unittest discover -s tests -v
```

The suite checks the health route, request validation, configured/missing-key handling, Gemini SDK call construction with a mocked SDK response, and DOCX/PDF exports. A real `/generate` call also requires a valid key and network access; the mock does not claim the external service was reached.

## Troubleshooting

- **Missing key:** confirm `.env` is beside `main.py` and contains `GEMINI_API_KEY=...`.
- **Backend unavailable in Streamlit:** start Uvicorn and check `BACKEND_URL` in `.env`.
- **Provider error or rate limit:** check the key, project access, quota, selected `GEMINI_MODEL`, and network connection. Provider details are intentionally not displayed.
- **PowerShell blocks activation:** invoke tools directly as `.\.venv\Scripts\python.exe -m ...` without activating.

## Legal disclaimer

LegalEase provides AI-generated legal information and document drafts for informational purposes only. It is not a substitute for advice from a qualified legal professional. Users should review documents for jurisdiction-specific requirements before use. The application does not guarantee enforceability or legal validity.

## Deployment notes

Run the API and Streamlit as separate services. Configure `GEMINI_API_KEY`, `GEMINI_MODEL`, and the frontend `BACKEND_URL` through the hosting provider's secret/environment settings. Use HTTPS, restrict backend access as appropriate, and do not deploy with development reload enabled. This project is prepared for local use; no provider-specific deployment manifest is required.
