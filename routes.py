"""API routes for LegalEase."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, field_validator

from ai_core.gemini_generator import (
    GeminiConfigurationError,
    GeminiDocumentGenerator,
    GeminiGenerationError,
)

router = APIRouter()


class DocumentRequest(BaseModel):
    document_type: str = Field(min_length=2, max_length=120)
    parties: str = Field(min_length=2, max_length=8000)
    terms: str = Field(min_length=2, max_length=16000)
    dates: str = Field(min_length=2, max_length=120)

    @field_validator("document_type", "parties", "terms", "dates")
    @classmethod
    def reject_whitespace_only(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("This field cannot be empty.")
        return value.strip()


@router.post("/generate")
def generate_document(request: DocumentRequest) -> dict[str, str]:
    try:
        generator = GeminiDocumentGenerator()
        content = generator.generate_document(
            document_type=request.document_type,
            parties=request.parties,
            terms=request.terms,
            dates=request.dates,
        )
        return {"document_type": request.document_type, "content": content}
    except GeminiConfigurationError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except GeminiGenerationError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=502, detail="Document generation is temporarily unavailable."
        ) from exc
