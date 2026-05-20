## This project are avaliable just in version PT-BR. <img width="1919" height="1079" alt="image" src="https://github.com/user-attachments/assets/77c217b4-58d5-4dbe-8b0f-60c06117ab5b" />


# ✂️ BarberShop – Sistema de Agendamentos

Sistema web para gerenciamento de agendamentos de barbearia, desenvolvido com **FastAPI** (backend) e **HTML/CSS/JS** (frontend).

## 🚀 Funcionalidades

- Agendar horário com nome, serviço, data e telefone
- Verificação automática de conflito de horários
- Visualizar agenda por data
- Editar agendamentos existentes
- Cancelar agendamentos

## 🛠️ Tecnologias

- Python + FastAPI
- Uvicorn
- Jinja2
- HTML5 / CSS3 / JavaScript

## ⚙️ Como rodar

```bash
# Instalar dependências
pip install -r requirements.txt

# Iniciar servidor
uvicorn app.main:app --reload
```

Acesse: http://localhost:8000

## 📁 Estrutura

```
barbearia/
├── app/main.py
├── static/css/style.css
├── static/js/app.js
├── templates/index.html
└── requirements.txt
```
