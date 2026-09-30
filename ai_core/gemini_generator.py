"""Google Gemini document generation."""

import os

from dotenv import load_dotenv


class GeminiConfigurationError(RuntimeError):
    """Raised when Gemini cannot be configured."""


class GeminiGenerationError(RuntimeError):
    """Raised when the Gemini request fails or returns no text."""

    def __init__(self, message: str, status_code: int = 502) -> None:
        super().__init__(message)
        self.status_code = status_code


class GeminiDocumentGenerator:
    """Create a document draft using Google's current Gen AI SDK."""

    def __init__(self, model: str | None = None) -> None:
        load_dotenv()
        api_key = os.getenv("GEMINI_API_KEY", "").strip()
        if not api_key or api_key == "your_gemini_api_key_here":
            raise GeminiConfigurationError("GEMINI_API_KEY is not configured.")

        try:
            from google import genai
        except ImportError as exc:
            raise GeminiConfigurationError(
                "The Google Gen AI SDK is missing. Install requirements.txt."
            ) from exc

        self.model = model or os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
        self.client = genai.Client(api_key=api_key)

    def generate_document(
        self, document_type: str, parties: str, terms: str, dates: str
    ) -> str:
        clauses = [item.strip() for item in terms.split(";") if item.strip()]
        clause_text = "\n".join(f"- {item}" for item in clauses) or terms.strip()
        prompt = f"""Draft a clear, professional {document_type} based only on the information below.

Document type: {document_type}
Parties and roles: {parties}
Effective date: {dates}
User-provided terms (preserve every clause faithfully; do not omit or materially change them):
{clause_text}

Write a complete, editable document in plain text. Adapt its sections to this specific
document type; do not force a generic contract structure. Use a title, descriptive section
headings, readable paragraphs, and numbered clauses where useful. Include signature blocks
when appropriate. Identify important missing details with clear [TO BE COMPLETED] placeholders
rather than inventing facts or terms. Do not assert that the document is legally valid or
give jurisdiction-specific conclusions without a jurisdiction being provided. Do not include
markdown code fences. Keep all names, dates, amounts, notice periods, and user terms accurate."""
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
            )
            text = (response.text or "").strip()
            if not text:
                raise GeminiGenerationError("Gemini returned an empty document.")
            return text
        except GeminiGenerationError:
            raise
        except Exception as exc:
            # Do not forward provider diagnostics: they can contain request details.
            provider_status = getattr(exc, "status_code", None)
            provider_code = getattr(exc, "code", None)
            if provider_status is None and isinstance(provider_code, int):
                provider_status = provider_code
            if provider_status == 429:
                raise GeminiGenerationError(
                    "Gemini is rate-limiting requests. Please wait and try again.", 429
                ) from exc
            if provider_status == 503 or type(exc).__name__ in {"ConnectError", "TimeoutException"}:
                raise GeminiGenerationError(
                    "Gemini is temporarily unavailable. Please try again shortly.", 503
                ) from exc
            raise GeminiGenerationError(
                "Gemini could not generate the document. Check the configured model and API access."
            ) from exc
