"""Minimal JD normalization placeholder tool."""
from typing import Dict


def normalize_jd(text: str) -> Dict:
    return {"normalized": " ".join(text.split()), "length": len(text)}
