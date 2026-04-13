"""
CRM Integration Layer — Clínica Saúde Integral
----------------------------------------------
Provides an abstract interface + a JSON-file mock implementation.
Swap MockCRM for HubSpotCRM, SalesforceCRM, etc. by implementing BaseCRM.
"""

from __future__ import annotations

import json
import uuid
from abc import ABC, abstractmethod
from datetime import datetime, date, timedelta
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

class Patient(dict):
    """Thin dict subclass — keeps CRM data loosely typed for flexibility."""

class Appointment(dict):
    pass


# ---------------------------------------------------------------------------
# Abstract interface — implement this to connect a real CRM
# ---------------------------------------------------------------------------

class BaseCRM(ABC):

    @abstractmethod
    def find_patient(self, cpf: str) -> Optional[Patient]:
        """Return existing patient or None."""

    @abstractmethod
    def create_patient(
        self,
        nome: str,
        cpf: str,
        email: str,
        telefone: str = "",
        canal: str = "whatsapp",
    ) -> Patient:
        """Create and return a new patient record."""

    @abstractmethod
    def list_procedures(self) -> list[dict]:
        """Return list of available procedures with name, duration_min, price."""

    @abstractmethod
    def check_availability(
        self, procedure: str, preferred_date: Optional[str] = None
    ) -> list[dict]:
        """
        Return list of available slots:
        [{"date": "2024-06-15", "time": "09:00", "doctor": "Dra. Ana Lima"}, ...]
        """

    @abstractmethod
    def create_appointment(
        self,
        patient_id: str,
        procedure: str,
        date: str,
        time: str,
        doctor: str,
        notes: str = "",
    ) -> Appointment:
        """Book appointment and return the created record."""


# ---------------------------------------------------------------------------
# Mock CRM — persists data to data/crm_data.json
# ---------------------------------------------------------------------------

DATA_FILE = Path(__file__).parent.parent / "data" / "crm_data.json"

PROCEDURES = [
    {"name": "Consulta Clínica Geral", "duration_min": 30, "price": 150.00},
    {"name": "Consulta Cardiologia", "duration_min": 40, "price": 250.00},
    {"name": "Consulta Dermatologia", "duration_min": 30, "price": 200.00},
    {"name": "Consulta Ginecologia", "duration_min": 40, "price": 220.00},
    {"name": "Consulta Ortopedia", "duration_min": 30, "price": 200.00},
    {"name": "Consulta Pediatria", "duration_min": 30, "price": 180.00},
    {"name": "Exame de Sangue (Hemograma)", "duration_min": 15, "price": 80.00},
    {"name": "Eletrocardiograma (ECG)", "duration_min": 20, "price": 120.00},
    {"name": "Ultrassom Abdominal", "duration_min": 30, "price": 180.00},
    {"name": "Raio-X", "duration_min": 15, "price": 90.00},
]

DOCTORS = {
    "Consulta Clínica Geral": ["Dr. Carlos Mendes", "Dra. Ana Lima"],
    "Consulta Cardiologia": ["Dr. Roberto Faria"],
    "Consulta Dermatologia": ["Dra. Patrícia Souza"],
    "Consulta Ginecologia": ["Dra. Mariana Costa"],
    "Consulta Ortopedia": ["Dr. Felipe Torres"],
    "Consulta Pediatria": ["Dra. Julia Ramos"],
    "Exame de Sangue (Hemograma)": ["Técnico Lab"],
    "Eletrocardiograma (ECG)": ["Técnico ECG"],
    "Ultrassom Abdominal": ["Dr. Lucas Martins"],
    "Raio-X": ["Técnico Radiologia"],
}

SLOTS = ["08:00", "08:30", "09:00", "09:30", "10:00", "10:30",
         "11:00", "14:00", "14:30", "15:00", "15:30", "16:00", "16:30"]


class MockCRM(BaseCRM):
    """JSON-file-backed mock CRM for development and testing."""

    def __init__(self):
        DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
        if not DATA_FILE.exists():
            DATA_FILE.write_text(json.dumps({"patients": {}, "appointments": []}, indent=2))

    # --- internal helpers ---

    def _load(self) -> dict:
        return json.loads(DATA_FILE.read_text())

    def _save(self, data: dict):
        DATA_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False))

    # --- BaseCRM implementation ---

    def find_patient(self, cpf: str) -> Optional[Patient]:
        cpf_clean = cpf.replace(".", "").replace("-", "").strip()
        data = self._load()
        return data["patients"].get(cpf_clean)

    def create_patient(
        self,
        nome: str,
        cpf: str,
        email: str,
        telefone: str = "",
        canal: str = "whatsapp",
    ) -> Patient:
        cpf_clean = cpf.replace(".", "").replace("-", "").strip()
        data = self._load()
        patient = {
            "id": str(uuid.uuid4()),
            "nome": nome,
            "cpf": cpf_clean,
            "email": email,
            "telefone": telefone,
            "canal": canal,
            "criado_em": datetime.now().isoformat(),
        }
        data["patients"][cpf_clean] = patient
        self._save(data)
        return Patient(patient)

    def list_procedures(self) -> list[dict]:
        return PROCEDURES

    def check_availability(
        self, procedure: str, preferred_date: Optional[str] = None
    ) -> list[dict]:
        """Return next 3 available days with mock slots."""
        doctors = DOCTORS.get(procedure, ["Médico Disponível"])
        slots = []
        start = datetime.now().date() + timedelta(days=1)
        if preferred_date:
            try:
                start = date.fromisoformat(preferred_date)
            except ValueError:
                pass

        for delta in range(7):
            day = start + timedelta(days=delta)
            # Skip weekends
            if day.weekday() >= 5:
                continue
            for t in SLOTS[:6]:  # show 6 slots per day
                slots.append({
                    "date": day.isoformat(),
                    "time": t,
                    "doctor": doctors[0],
                })
            if len(slots) >= 9:  # return ~9 slots across 2-3 days
                break
        return slots

    def create_appointment(
        self,
        patient_id: str,
        procedure: str,
        date: str,
        time: str,
        doctor: str,
        notes: str = "",
    ) -> Appointment:
        data = self._load()
        appt = {
            "id": str(uuid.uuid4()),
            "patient_id": patient_id,
            "procedure": procedure,
            "date": date,
            "time": time,
            "doctor": doctor,
            "notes": notes,
            "status": "agendado",
            "criado_em": datetime.now().isoformat(),
        }
        data["appointments"].append(appt)
        self._save(data)
        return Appointment(appt)


# ---------------------------------------------------------------------------
# Singleton — import crm from here in other modules
# ---------------------------------------------------------------------------

crm: BaseCRM = MockCRM()
