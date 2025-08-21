"""Minimal resume text extraction placeholder tool."""
from typing import Dict


def extract_resume_text(text: str) -> Dict:
    # In real usage you'd parse PDF/DOCX. For now, return text as-is.
    return {"text": text, "chars": len(text)}
