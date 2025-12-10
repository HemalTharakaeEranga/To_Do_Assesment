# 📝 To_Do Assessment

A small full-stack To-Do web application:

- **Frontend**: plain HTML, CSS, vanilla JS  
- **Backend**: FastAPI (Python)  
- **Database**: MySQL  
- **Runtime**: Docker + Docker Compose  

---

## Project Structure

```text
todo-assessment/
├─ backend/
│  ├─ app/
│  │  ├─ main.py          # FastAPI app
│  │  ├─ database.py      # SQLAlchemy engine
│  │  ├─ models.py        # Task model
│  │  ├─ schemas.py       # Pydantic schemas
│  │  ├─ crud.py          # DB operations
│  │  └─ __init__.py
│  ├─ tests/
│  │  └─ test_main.py     # Basic API tests
│  ├─ requirements.txt    # Python dependencies
│  └─ Dockerfile          # Backend Docker image
├─ frontend/
│  ├─ index.html          # UI
│  ├─ styles.css          # styling
│  └─ app.js              # Frontend logic (API calls)
│  └─ Dockerfile          # Frontend Docker image
├─ docker-compose.yml      # App + DB services
├─ mysql-init/
│  └─ init.sql            # Creates DB
└─ README.md
```
--------------

**Clone the repository**
--------------------------------
git clone https://github.com/HemalTharakaeEranga/To_Do_Assesment.git
cd To_Do_Assesment

--------

**Install Python(Python 3.11) and dependencies**
--------------------------------
- cd backend

- python -m venv .venv
- . .venv/Scripts/activate   # Windows PowerShell
- # or: source .venv/bin/activate  # Linux/Mac

- pip install -r requirements.txt
--------

**Start the app**
--------------------------------
- docker compose up --build # docker compose up -d
- docker volume ls
- docker compose down # stop containers
- docker compose ps # check containers
- docker compose down --volumes # remove containers and the MySQL volume
--------------------------------
