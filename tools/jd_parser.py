"""Minimal JD normalization placeholder tool."""
from pydantic import BaseModel, Field

class JDNormalizeInput(BaseModel):
    text: str = Field(..., description="Raw job description text")

class JDNormalizeOutput(BaseModel):
    normalized: str = Field(..., description="Normalized job description")
    length: int = Field(..., description="Length of normalized text")

def normalize_jd(input: JDNormalizeInput) -> JDNormalizeOutput:
    norm = " ".join(input.text.split())
    return JDNormalizeOutput(normalized=norm, length=len(norm))
