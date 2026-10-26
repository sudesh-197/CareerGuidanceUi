# Clean-up report

Goal: fix structure, dead code and loopholes **without changing features, logic or UI**.
Every number below was measured on the original project and the result.

## 1. Structure

| Before | After |
|---|---|
| One 3,333-line `flask_cors_config.py` (66 routes, config, auth, mail, uploads, error handlers) plus a 1,592-line backup copy | Application factory (`app/__init__.py`) + `config`, `extensions`, `auth`, `errors` + **11 blueprint modules** (largest: 555 lines) |
| 40 flat modules in `backend/`, camelCase and snake_case mixed, imports resolved by `sys.path` hacks (repeated 5× inside route bodies) | Proper package: `models/`, `services/{analysis,routine}/`, `data/`, `utils/`, `explore/`; plain `from app...` imports, all snake_case |
| 60+ imports buried inside functions | Light imports hoisted to module top; heavy/optional libraries stay lazy on purpose (see ARCHITECTURE) |
| 7 copies of `os.path.join(os.path.dirname(__file__), 'uploads', …)` | One definition each in `app/config.py` |
| JWT creation copy-pasted in signup and login | `create_access_token()` |
| 2 divergent app factories (`app_config.py`, `db_init.py`) | Deleted – tests use the real factory |
| Frontend: backend URL hard-coded in 26 files (49 places) with 3 different conventions | `config/api.js` – one `API_BASE_URL` (default unchanged) |
| Frontend: 13 components dumped in one folder | `auth/ common/ layout/ home/` (imports rewritten automatically) |
| 25 test scripts mixed into the source folder | `backend/tests/`, plus `conftest.py` |
| 135 markdown status reports, README describing a landing page only | `README.md` + 4 accurate docs |
| `venv/` (324 MB) + parent `venv/` (610 MB), `node_modules/` (907 MB), `build/`, `__pycache__`, generated `_run_*.bat` with a personal `C:\Users\…` path | Not shipped; `.gitignore` covers them |

## 2. Dead code removed (archived in `_removed/` – delete it after review)

* Backend: `routineEngine.py` (408 lines), `progressTracker.py` (328), `scheduler.py` (282) – only referenced each other; the app uses `routineEngineCore`, `progressManager`, `weeklyScheduler`. Also `app_config.py`, `db_init.py`, `verify_files.py`, two one-off migrations (merged into `scripts/migrate_db.py`), sample json outputs.
* Frontend: 13 files never imported by the app (`Blogs`, `Feed`, `ReachOut`, `CreateBlogModal`, `Contact`, `After10th` + its service/scoring utils, `SharedStyles`, `App.css`, `logo.svg`, the stale CRA `App.test.js`), 5 unused exports in `routineService.js` that called non-existent endpoints, and ~20 unused imports/variables. ESLint warnings: **28 → 6** (the 6 left are 5 React hook-dependency notes and 1 accessibility note that I deliberately did not touch because changing them could alter behaviour).
* 24 unused imports in the backend package.

## 3. Bugs found and fixed (these are the only behaviour changes besides §4)

1. **`json` was never imported** in the old file, so `GET /api/routine/evolution?routineData=…` always hit a `NameError` hidden by a bare `except:` and silently ignored the data.
2. **`POST /api/analyze/upload` always returned 500** (`TypeError`: it re-called an already-wrapped view with an extra argument).
3. **The Explore rate limit never worked**: it was registered after the blueprint, Flask raised `AssertionError`, the surrounding `try/except` swallowed it and printed a misleading *"Explore blueprint not loaded"* although it was loaded. The message is now correct; the limit is opt-in via `EXPLORE_RATE_LIMIT` (default off = same effective behaviour as before).

## 4. Security hardening

| Issue in the original | Now |
|---|---|
| `app.run(debug=True, host='0.0.0.0')` – interactive debugger reachable from the network | Debug only with `FLASK_DEBUG=1` (the start script sets it for local dev); binds to `127.0.0.1` by default |
| Forgot-password returned the reset link in the HTTP response whenever e-mail was not configured → **anyone knowing an e-mail could take over that account** | Link only returned in debug / `ALLOW_DEV_RESET_LINK=1`; otherwise the generic "if that email exists…" message |
| No throttling on login / signup / password reset (brute force) | 10/min (login, signup, reset), 5/min (forgot-password) per IP |
| No upload size limit | `MAX_UPLOAD_MB` (default 500) with a JSON 413 response |
| `.env` (Gmail app password) was **not** git-ignored | Ignored. **Rotate that Gmail app password** – it has been in plain files and in the zip you shared |
| Hard-coded default `SECRET_KEY` silently used | Still the default (so existing logins keep working) but a startup warning is printed – set `SECRET_KEY` before deploying |
| CORS fixed to `*` | Same default, configurable with `CORS_ORIGINS` |
| Tests could write into the real database | `conftest.py` uses a temporary DB |

## 5. How it was verified

* Every one of the 66 original route functions was compared to its new version at AST level after normalising only the mechanical edits: **66/66 identical** except the 5 intentionally changed ones above (`signup`, `login`, `forgot_password`, `reset_password` hardening, `analyze_upload` fix).
* 33 of 34 moved modules are logically identical to the originals (only import lines differ); the 34th is the Explore routes header (path hacks removed).
* Both apps were booted side by side: **identical 73-rule URL map** (paths + methods); 15 HTTP probes (auth errors, preflight, 404s, validation) return identical status and body.
* Service tests (routine generation, video resources, weekly timetable, completion tracking, evolution analytics) produce **identical output** in both layouts.
* `career_guidance.db` and all 28 uploaded files are byte-identical to the originals.
* Frontend production build succeeds; bundle size unchanged (348.7 → 348.5 kB gzip).

**Not verified here:** the real Flask extensions (flask-cors/limiter/mail/sqlalchemy) and a browser were not available offline, so the above used stand-ins for those libraries. Please do one normal run-through (`START_PROJECT.bat`, log in, open each page) before relying on it.

## 6. Known issues I did NOT change (outside "no functional change")

* **Resume "DOCX download" button calls `/api/resume/download/docx`, which does not exist** – it fails in the original too.
* API errors return `str(e)` to the client (can leak internals); signup has no password-strength rule; password-reset tokens are kept in memory (lost on restart).
* Legacy duplicate endpoints are kept (`/reachout`, `/groups/<id>/join`, legacy messages/notifications) because external callers may exist.
* `RoutineBuild.jsx` (~1,000 lines), `AuthModal.jsx`, `Profile.jsx` are large; splitting UI components without a browser to check them was not worth the risk.
* `Profile.jsx` still fetches conversations it never displays; 5 hook-dependency warnings remain.
* Several backend routes (`/api/postmatrics/*`) are not used by the current UI (it computes client-side).
* `package.json` still lists `@testing-library/*`; Python code still uses the deprecated `datetime.utcnow()`.
