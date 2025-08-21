"""Minimal ATS scoring placeholder tool.

Portia can wrap Python callables as tools. This function is a simple stub
that returns a naive match score so imports don't fail.
"""
from typing import Dict


def ats_score(resume_text: str, job_description: str) -> Dict:
    resume = resume_text.lower()
    jd = job_description.lower()
    if not resume or not jd:
        return {"ats_score": 0, "matched_keywords": [], "missing_keywords": []}
    words = {w for w in jd.split() if len(w) > 3}
    matched = sorted([w for w in words if w in resume])
    missing = sorted(list(words - set(matched)))
    score = int(100 * (len(matched) / max(1, len(words))))
    return {"ats_score": score, "matched_keywords": matched, "missing_keywords": missing}
