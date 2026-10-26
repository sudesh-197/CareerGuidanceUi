<div align="center">

# 🎓 CareerAI

### Intelligent Career Guidance System

Analyse your resume, get a personalised learning routine, explore career paths and connect with a community - all in one place.

![React](https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=white)
![Tailwind](https://img.shields.io/badge/Tailwind_CSS-3-38BDF8?logo=tailwindcss&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3-000000?logo=flask&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.9+-3776AB?logo=python&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?logo=sqlite&logoColor=white)

</div>

---

## ✨ Features

| Module | What it does |
|---|---|
| 📄 **Resume Analyzer** | Upload a resume (PDF/DOCX) or enter skills manually; get an ATS-style score, skill gaps and role-readiness for a target domain |
| 🛠️ **Resume Builder** | Create a resume with live preview and download it as PDF |
| 🗓️ **Routine Builder** | Generates a personalised weekly learning timetable with curated video resources, progress tracking and an AI mentor chat |
| 🎒 **Post-Matric Guidance** | After-10th and after-12th stream guidance, competitive exams, skill-based careers, scholarships and an interest test |
| 🔭 **Explore** | Career snapshot, future simulation, side-by-side career comparison, skill ROI, reality check and a "confused? find my path" tool |
| 👥 **Community** | Interest-based groups, group chat, direct messages, feedback wall and notifications |
| 👤 **Accounts** | Sign up / log in (JWT), profile with picture, password reset by email |

## 🧱 Tech stack

| Layer | Technology |
|---|---|
| Frontend | React 19, React Router 7, Tailwind CSS 3, Framer Motion, Lucide icons, jsPDF |
| Backend | Flask 3, Flask-SQLAlchemy, Flask-CORS, Flask-Limiter, Flask-Mail, PyJWT |
| Database | SQLite (created automatically) |
| Documents | PyPDF2, python-docx, ReportLab |
| AI (optional) | Local Mistral-7B via [LM Studio](https://lmstudio.ai/) - falls back to rule-based replies when not running |

## 📁 Project structure

```
.
├── backend/
│   ├── run.py                 # entry point
│   ├── requirements.txt
│   ├── .env.example           # all settings, documented
│   ├── app/
│   │   ├── __init__.py        # create_app() factory
│   │   ├── config.py  extensions.py  auth.py  errors.py
│   │   ├── routes/            # one blueprint per feature
│   │   ├── models/            # SQLAlchemy models
│   │   ├── services/          # business logic (analysis/, routine/, community)
│   │   ├── explore/           # Explore module
│   │   ├── data/              # static knowledge tables
│   │   └── utils/
│   ├── scripts/               # maintenance scripts
│   └── tests/
├── frontend/
│   └── src/
│       ├── config/api.js      # backend URL (single source of truth)
│       ├── services/          # API clients
│       ├── pages/             # one component per route
│       └── components/        # auth, common, layout, home, community, explore, ...
├── docs/                      # ARCHITECTURE, SETUP, API, CHANGES
├── scripts/                   # helpers for the Windows launcher
├── INSTALL_DEPS.bat  START_PROJECT.bat  STOP_PROJECT.bat
└── README.md
```

## 🚀 Getting started

### Prerequisites
- [Python 3.9+](https://www.python.org/downloads/) (tick **Add to PATH** on Windows)
- [Node.js 18+](https://nodejs.org/)

### Option A - Windows one-click
1. Double-click **`INSTALL_DEPS.bat`** (first time only)
2. Double-click **`START_PROJECT.bat`** - the app opens at <http://localhost:3000>
3. Double-click **`STOP_PROJECT.bat`** to stop

### Option B - Manual (Windows / macOS / Linux)

**1. Clone**
```bash
git clone https://github.com/<your-username>/<your-repo>.git
cd <your-repo>
```

**2. Backend** (terminal 1)
```bash
cd backend
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env              # Windows: copy .env.example .env
python run.py                     # API on http://localhost:5000
```
> Add `FLASK_DEBUG=1` for development (Flask debugger; shows the password-reset link when email is not configured).

**3. Frontend** (terminal 2)
```bash
cd frontend
npm install
npm start                         # App on http://localhost:3000
```

The SQLite database and upload folders are created automatically on first run.

## ⚙️ Configuration

Copy `backend/.env.example` to `backend/.env`. Everything is optional for local use.

| Variable | Purpose |
|---|---|
| `SECRET_KEY` | Signs login tokens - **set a long random value before deploying** |
| `MAIL_USERNAME`, `MAIL_PASSWORD` | Gmail + [App Password](https://myaccount.google.com/apppasswords) for password-reset emails |
| `FRONTEND_URL` | Used in the reset link (default `http://localhost:3000`) |
| `CORS_ORIGINS` | Allowed origins, comma separated (default `*`) |
| `FLASK_DEBUG` | `1` for development only |

Frontend: set `REACT_APP_API_URL` in `frontend/.env` if the API is not on `http://localhost:5000`.

More options: [`docs/SETUP.md`](docs/SETUP.md).

## 🤖 Optional: AI mentor chat

1. Install **LM Studio**, load a *Mistral-7B-Instruct* model and click **Start Server** (`http://localhost:1234/v1`).
2. Start the backend. If LM Studio is not running, the chat uses built-in fallback replies.

## 🧪 Tests

```bash
cd backend
pip install -r requirements-dev.txt
python -m pytest tests -q
```
Tests run against a temporary database and never touch your real data.

## 📚 Documentation

- [Setup & troubleshooting](docs/SETUP.md)
- [Architecture](docs/ARCHITECTURE.md)
- [API reference](docs/API.md) (73 endpoints)
- [Clean-up report](docs/CHANGES.md)

## 🔒 Security notes

- Never commit `.env` or `*.db` (both are in `.gitignore`).
- Set a strong `SECRET_KEY` and a restrictive `CORS_ORIGINS` for any public deployment.
- Do not run with `FLASK_DEBUG=1` on a public server.

## 📝 License

Add your license here (e.g. MIT) and include a `LICENSE` file.

## 👤 Author

**Your Name** - final-year project
GitHub: [@your-username](https://github.com/your-username)
