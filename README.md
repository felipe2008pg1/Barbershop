## This project was originally written in Portuguese and then translated into English. 🇧🇷 🇺🇸


# ✂️ BarberShop – Scheduling System

Web-based system for managing barber shop appointments, developed with **FastAPI** (backend) and **HTML/CSS/JS** (frontend).

## 🚀 Features

- Schedule an appointment with name, service, date, and phone number.
- Automatic scheduling conflict check.
- View schedule by date.
- Edit existing appointments.
- Cancel appointments.
  
## 🛠️ Technologies

- Python + FastAPI
- Uvicorn
- Jinja2
- HTML5 / CSS3 / JavaScript

## ⚙️ How to run

```bash
# Install dependences
pip install -r requirements.txt

# Start server
uvicorn app.main:app --reload
```

Acess: http://localhost:8000

## 📁 Structure

```
barbershop/
├── app/main.py
├── static/css/style.css
├── static/js/app.js
├── templates/index.html
└── requirements.txt
```
