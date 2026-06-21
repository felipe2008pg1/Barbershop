from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional
import json
import os
from datetime import datetime

app = FastAPI(title="Barbershop - Appointment Scheduling System")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))


def load_appointments():
    db = os.path.join(BASE_DIR, "appointments.json")
    if not os.path.exists(db):
        return []
    with open(db, "r", encoding="utf-8") as f:
        return json.load(f)


def save_appointments(appointments):
    db = os.path.join(BASE_DIR, "appointments.json")
    with open(db, "w", encoding="utf-8") as f:
        json.dump(appointments, f, ensure_ascii=False, indent=2)


class Appointment(BaseModel):
    name: str
    service: str
    date: str
    time: str
    phone: Optional[str] = ""


class AppointmentUpdate(BaseModel):
    name: Optional[str] = None
    service: Optional[str] = None
    date: Optional[str] = None
    time: Optional[str] = None
    phone: Optional[str] = None


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(request, "index.html")


@app.get("/api/appointments")
def list_appointments(date: Optional[str] = None):
    appointments = load_appointments()
    if date:
        appointments = [a for a in appointments if a["date"] == date]
    appointments.sort(key=lambda x: (x["date"], x["time"]))
    return appointments


@app.post("/api/appointments", status_code=201)
def create_appointment(appointment: Appointment):
    appointments = load_appointments()
    conflict = any(
        a["date"] == appointment.date and a["time"] == appointment.time
        for a in appointments
    )
    if conflict:
        raise HTTPException(status_code=409, detail="An appointment already exists for this time.")
    new = {
        "id": int(datetime.now().timestamp() * 1000),
        "name": appointment.name.strip(),
        "service": appointment.service,
        "date": appointment.date,
        "time": appointment.time,
        "phone": appointment.phone.strip(),
        "created_at": datetime.now().isoformat()
    }
    appointments.append(new)
    save_appointments(appointments)
    return new


@app.put("/api/appointments/{id}")
def update_appointment(id: int, data: AppointmentUpdate):
    appointments = load_appointments()
    idx = next((i for i, a in enumerate(appointments) if a["id"] == id), None)

    if idx is None:
        raise HTTPException(status_code=404, detail="Appointment not found.")

    updated = appointments[idx]

    if data.name is not None:
        updated["name"] = data.name.strip()
    if data.service is not None:
        updated["service"] = data.service
    if data.date is not None:
        updated["date"] = data.date
    if data.time is not None:
        updated["time"] = data.time
    if data.phone is not None:
        updated["phone"] = data.phone.strip()

    conflict = any(
        a["date"] == updated["date"]
        and a["time"] == updated["time"]
        and a["id"] != id
        for a in appointments
    )

    if conflict:
        raise HTTPException(status_code=409, detail="An appointment already exists for this time.")

    appointments[idx] = updated
    save_appointments(appointments)
    return updated


@app.delete("/api/appointments/{id}", status_code=204)
def cancel_appointment(id: int):
    appointments = load_appointments()
    new_list = [a for a in appointments if a["id"] != id]

    if len(new_list) == len(appointments):
        raise HTTPException(status_code=404, detail="Appointment not found.")

    save_appointments(new_list)
