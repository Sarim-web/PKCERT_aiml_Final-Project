from pydantic import BaseModel, Field, field_validator

class IncidentRequest(BaseModel):
    text: str = Field(..., min_length=10, max_length=1000)

    @field_validator("text")
    @classmethod
    def not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("text cannot be empty")
        return v.strip()

class IncidentResponse(BaseModel):
    severity: str
    confidence: float
    label_id: int