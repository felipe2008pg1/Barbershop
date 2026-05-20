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

app = FastAPI(title="Barbearia - Sistema de Agendamentos")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))


def carregar_agendamentos():
    db = os.path.join(BASE_DIR, "agendamentos.json")
    if not os.path.exists(db):
        return []
    with open(db, "r", encoding="utf-8") as f:
        return json.load(f)


def salvar_agendamentos(agendamentos):
    db = os.path.join(BASE_DIR, "agendamentos.json")
    with open(db, "w", encoding="utf-8") as f:
        json.dump(agendamentos, f, ensure_ascii=False, indent=2)


class Agendamento(BaseModel):
    nome: str
    servico: str
    data: str
    horario: str
    telefone: Optional[str] = ""


class AgendamentoUpdate(BaseModel):
    nome: Optional[str] = None
    servico: Optional[str] = None
    data: Optional[str] = None
    horario: Optional[str] = None
    telefone: Optional[str] = None


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(request, "index.html")


@app.get("/api/agendamentos")
def listar_agendamentos(data: Optional[str] = None):
    agendamentos = carregar_agendamentos()
    if data:
        agendamentos = [a for a in agendamentos if a["data"] == data]
    agendamentos.sort(key=lambda x: (x["data"], x["horario"]))
    return agendamentos


@app.post("/api/agendamentos", status_code=201)
def criar_agendamento(agendamento: Agendamento):
    agendamentos = carregar_agendamentos()
    conflito = any(
        a["data"] == agendamento.data and a["horario"] == agendamento.horario
        for a in agendamentos
    )
    if conflito:
        raise HTTPException(status_code=409, detail="Já existe um agendamento nesse horário.")
    novo = {
        "id": int(datetime.now().timestamp() * 1000),
        "nome": agendamento.nome.strip(),
        "servico": agendamento.servico,
        "data": agendamento.data,
        "horario": agendamento.horario,
        "telefone": agendamento.telefone.strip(),
        "criado_em": datetime.now().isoformat()
    }
    agendamentos.append(novo)
    salvar_agendamentos(agendamentos)
    return novo


@app.put("/api/agendamentos/{id}")
def atualizar_agendamento(id: int, dados: AgendamentoUpdate):
    agendamentos = carregar_agendamentos()
    idx = next((i for i, a in enumerate(agendamentos) if a["id"] == id), None)
    if idx is None:
        raise HTTPException(status_code=404, detail="Agendamento não encontrado.")
    atualizado = agendamentos[idx]
    if dados.nome is not None:
        atualizado["nome"] = dados.nome.strip()
    if dados.servico is not None:
        atualizado["servico"] = dados.servico
    if dados.data is not None:
        atualizado["data"] = dados.data
    if dados.horario is not None:
        atualizado["horario"] = dados.horario
    if dados.telefone is not None:
        atualizado["telefone"] = dados.telefone.strip()
    conflito = any(
        a["data"] == atualizado["data"]
        and a["horario"] == atualizado["horario"]
        and a["id"] != id
        for a in agendamentos
    )
    if conflito:
        raise HTTPException(status_code=409, detail="Já existe um agendamento nesse horário.")
    agendamentos[idx] = atualizado
    salvar_agendamentos(agendamentos)
    return atualizado


@app.delete("/api/agendamentos/{id}", status_code=204)
def cancelar_agendamento(id: int):
    agendamentos = carregar_agendamentos()
    novos = [a for a in agendamentos if a["id"] != id]
    if len(novos) == len(agendamentos):
        raise HTTPException(status_code=404, detail="Agendamento não encontrado.")
    salvar_agendamentos(novos)