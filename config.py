import os
from pathlib import Path


class Config:
    SECRET_KEY = os.environ.get("CAREERFORGE_SECRET_KEY")
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    DATABASE = os.environ.get(
        "CAREERFORGE_DATABASE",
        str(Path(__file__).resolve().parent / "instance" / "careerforge.sqlite"),
    )
    READINESS_WEIGHTS = {
        "skills": float(os.environ.get("CAREERFORGE_SKILLS_WEIGHT", "0.40")),
        "coding": float(os.environ.get("CAREERFORGE_CODING_WEIGHT", "0.35")),
        "interview": float(os.environ.get("CAREERFORGE_INTERVIEW_WEIGHT", "0.25")),
    }
    CODING_TARGET = int(os.environ.get("CAREERFORGE_CODING_TARGET", "20"))
