# Setup, configuration and troubleshooting

## Requirements
Python 3.9+, Node.js 18+. (LM Studio only if you want the AI chatbot.)

## Configuration
Backend settings are read from environment variables or `backend/.env`; copy `backend/.env.example` and uncomment what you need.

| Variable | Default | Meaning |
|---|---|---|
| `SECRET_KEY` | insecure built-in | Signs login tokens. **Set it before any real deployment** (changing it logs everyone out). |
| `MAIL_USERNAME`, `MAIL_PASSWORD` | – | Gmail + [App Password](https://myaccount.google.com/apppasswords) for password-reset e-mails |
| `FRONTEND_URL` | `http://localhost:3000` | Used in the reset link |
| `FLASK_DEBUG` | `0` | `1` = Flask debugger, and the reset link is returned in the API response when e-mail is not set up. `START_PROJECT.bat` sets it. |
| `FLASK_HOST`, `PORT` | `127.0.0.1`, `5000` | Bind address / port |
| `CORS_ORIGINS` | `*` | Comma-separated list, e.g. `http://localhost:3000` |
| `MAX_UPLOAD_MB` | `500` | Upload size limit |
| `EXPLORE_RATE_LIMIT` | off | e.g. `30 per minute` for `/api/explore/*` |
| `DATABASE_URL` | `sqlite:///backend/career_guidance.db` | Any SQLAlchemy URL |

Frontend: `frontend/.env` – `REACT_APP_API_URL` if the API is not on `http://localhost:5000`.

## Local AI chatbot (optional)
1. Open **LM Studio**, load a *Mistral-7B-Instruct* model, click **Start Server** (`http://localhost:1234/v1`).
2. Start the backend. Without LM Studio the Routine Builder chat automatically uses its rule-based fallback.
3. Prefer no LM Studio? `pip install -r requirements-optional.txt` then `python scripts/setup_mistral.py` (downloads a GGUF into `backend/models/` and sets `MISTRAL_MODEL_PATH`).

## Tests
```bash
cd backend
pip install -r requirements-dev.txt
python -m pytest tests -q
```
`tests/conftest.py` points the app at a **temporary database**, so pytest never touches `career_guidance.db`.
Many files in `tests/` are older script-style checks (they print results); run one directly with
`python -m tests.test_video_resources` from `backend/` (those run against the real database, as before).

## Maintenance scripts (run from `backend/`)
| Command | Purpose |
|---|---|
| `python scripts/migrate_db.py` | Upgrade an *old* DB file (adds `users.profile_picture`, `posts.video_url`) – safe to repeat |
| `python -m scripts.create_missing_profiles` | Create reach-out profiles for users who signed up before profiles existed |
| `python scripts/view_database.py` | Print table contents |

## Troubleshooting
| Symptom | Fix |
|---|---|
| `venv` errors after copying the project to another PC | Delete `backend/venv`; `INSTALL_DEPS.bat` recreates it |
| Port 3000/5000 in use | `STOP_PROJECT.bat` |
| Reset-password gives no link / no e-mail | Configure `MAIL_*`, or run with `FLASK_DEBUG=1` to get the link in the response |
| `ModuleNotFoundError: app` | Run commands from the `backend/` folder |
| Resume analysis says a library is missing | `pip install -r requirements.txt` |
| Chat is not "smart" | LM Studio is not running – the fallback is used |
