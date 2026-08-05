from pathlib import Path
from typing import Optional
import json
import re
import uuid

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr

app = FastAPI(
    title="HR Onboarding Agent API",
    version="1.0.0",
    description="Deployment artifact for the agentic HR onboarding capstone.",
)

BASE_DIR = Path(__file__).resolve().parent
PACKAGE_PATH = BASE_DIR / "artifacts" / "final_onboarding_package.json"
REGISTRY_PATH = BASE_DIR / "data" / "employee_registry.json"

class OnboardingRequest(BaseModel):
    candidate_id: str
    candidate_name: str
    email: EmailStr
    phone: str
    resume_text: str
    position: str
    department: str
    start_date: str
    hired: bool

def employee_exists(candidate_id: str, email: str) -> bool:
    if not REGISTRY_PATH.exists():
        return False

    try:
        records = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return False

    candidate_id = candidate_id.strip().lower()
    email = email.strip().lower()

    return any(
        str(record.get("candidate_id", "")).strip().lower() == candidate_id
        or str(record.get("email", "")).strip().lower() == email
        for record in records
    )

def contains_prompt_injection(text: str) -> bool:
    patterns = [
        r"ignore\s+(all\s+)?previous\s+instructions",
        r"reveal\s+(the\s+)?system\s+prompt",
        r"approve\s+.*without\s+(review|approval)",
        r"skip\s+(human\s+)?approval",
    ]
    return any(re.search(pattern, text, re.I) for pattern in patterns)

@app.get("/health")
def health():
    return {"status": "healthy", "service": "hr-onboarding-agent"}

@app.post("/onboard/validate")
def validate_onboarding(request: OnboardingRequest):
    if contains_prompt_injection(request.resume_text):
        raise HTTPException(
            status_code=400,
            detail="Input blocked by prompt-injection guardrail.",
        )

    if not request.hired:
        return {
            "accepted": False,
            "status": "not_hired",
            "candidate_id": request.candidate_id,
        }

    if employee_exists(request.candidate_id, str(request.email)):
        raise HTTPException(
            status_code=409,
            detail="Employee already exists; duplicate onboarding blocked.",
        )

    return {
        "accepted": True,
        "status": "ready_for_agentic_workflow",
        "thread_id": f"{request.candidate_id}-{uuid.uuid4().hex[:8]}",
    }

@app.get("/latest-package")
def latest_package():
    if not PACKAGE_PATH.exists():
        raise HTTPException(status_code=404, detail="No package generated yet.")
    return json.loads(PACKAGE_PATH.read_text(encoding="utf-8"))
