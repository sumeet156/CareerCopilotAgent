"""Minimal resume text extraction placeholder tool."""
from pydantic import BaseModel, Field

class ResumeTextInput(BaseModel):
    text: str = Field(..., description="Raw resume text")

class ResumeTextOutput(BaseModel):
    text: str = Field(..., description="Extracted resume text")
    chars: int = Field(..., description="Character count")

def extract_resume_text(input: ResumeTextInput) -> ResumeTextOutput:
    # In real usage you'd parse PDF/DOCX. For now, return text as-is.
    return ResumeTextOutput(text=input.text, chars=len(input.text))
