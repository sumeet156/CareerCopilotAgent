"""Minimal ATS scoring placeholder tool.

Portia can wrap Python callables as tools. This function is a simple stub
that returns a naive match score so imports don't fail.
"""
from pydantic import BaseModel, Field

class ATSScoreInput(BaseModel):
    resume_text: str = Field(..., description="Resume text to analyze")
    job_description: str = Field(..., description="Job description to match against")

class ATSScoreOutput(BaseModel):
    ats_score: int = Field(..., description="ATS match score (0-100)")
    matched_keywords: list[str] = Field(default_factory=list, description="Keywords matched in resume")
    missing_keywords: list[str] = Field(default_factory=list, description="Keywords missing from resume")

def ats_score(input: ATSScoreInput) -> ATSScoreOutput:
    resume = input.resume_text.lower()
    jd = input.job_description.lower()
    if not resume or not jd:
        return ATSScoreOutput(ats_score=0, matched_keywords=[], missing_keywords=[])
    words = {w for w in jd.split() if len(w) > 3}
    matched = sorted([w for w in words if w in resume])
    missing = sorted(list(words - set(matched)))
    score = int(100 * (len(matched) / max(1, len(words))))
    return ATSScoreOutput(ats_score=score, matched_keywords=matched, missing_keywords=missing)
