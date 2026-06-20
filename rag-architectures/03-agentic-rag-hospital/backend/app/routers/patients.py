import json
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status

from app.auth import User, get_current_user
from app.models import PatientSummary

router = APIRouter(prefix="/api/v1/patients", tags=["patients"])

DATA_DIR = Path(__file__).resolve().parents[3] / "data" / "patients"


def _load_patient(patient_id: str) -> dict[str, Any] | None:
    path = DATA_DIR / f"{patient_id}.json"
    if not path.exists():
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _summarize(patient: dict[str, Any]) -> PatientSummary:
    name = patient.get("name", [{}])[0]
    display_name = " ".join(name.get("given", [])) + " " + name.get("family", "")
    display_name = display_name.strip() or "Unknown"

    conditions = [
        c.get("code", {}).get("text", "")
        for c in patient.get("conditions", [])
    ]
    medications = [
        m.get("medicationCodeableConcept", {}).get("text", "")
        for m in patient.get("medications", [])
    ]
    allergies = [
        a.get("code", {}).get("text", "")
        for a in patient.get("allergies", [])
    ]

    return PatientSummary(
        patient_id=patient.get("id", ""),
        name=display_name,
        birth_date=patient.get("birthDate", ""),
        gender=patient.get("gender", ""),
        conditions=[c for c in conditions if c],
        medications=[m for m in medications if m],
        allergies=[a for a in allergies if a],
    )


@router.get("/{patient_id}", response_model=PatientSummary)
async def get_patient(patient_id: str, user: User = Depends(get_current_user)) -> PatientSummary:
    patient = _load_patient(patient_id)
    if patient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient {patient_id} not found",
        )
    return _summarize(patient)
