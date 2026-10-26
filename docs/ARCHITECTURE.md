# Architecture

## Backend request flow

```
HTTP request
  → Flask app (app/__init__.py: create_app)
      → CORS, rate limiter, error handlers (app/errors.py)
      → blueprint in app/routes/<feature>.py
          → @token_required (app/auth.py) injects the user id
          → service / model code (app/services, app/models)
      ← JSON {success: bool, ...}
```

### Layers and rules

| Layer | Folder | Rule |
|---|---|---|
| Routes | `app/routes/` | Parse the request, call services/models, return JSON. One blueprint module per feature. |
| Services | `app/services/` | Business logic. No Flask request objects. `analysis/` = resume analysis, `routine/` = routine builder, chat and progress. |
| Models | `app/models/` | SQLAlchemy tables only. `db` comes from `app/extensions.py`. |
| Data | `app/data/` | Large static lookup tables (skill topics, learning videos). |
| Explore | `app/explore/` | Self-contained feature: blueprint + one service per tool. Loaded optionally – a failure here never stops the API. |

### Blueprints

| Module | Purpose |
|---|---|
| `auth` | signup, login, forgot/reset password |
| `profile` | profile read/update, profile-picture upload |
| `media` | serves files from `uploads/` |
| `analysis` | resume analysis |
| `postmatrics` | after-10th / 12th guidance, exams, scholarships, interest test |
| `routine`, `progress` | routine generation, mentor chat, evolution + weekly progress |
| `community`, `content`, `messaging`, `notifications` | groups & chat rooms, blogs/feedback/posts, direct messages, notifications |

### Adding an endpoint

1. Add a function to the matching file in `app/routes/` with `@bp.route(...)` and (if private) `@token_required`.
2. Put non-trivial logic in `app/services/`.
3. New blueprint file? Add its name to `BLUEPRINT_MODULES` in `app/routes/__init__.py`.
4. Refresh the endpoint reference: `python scripts/generate_api_docs.py` (run from `backend/`) rewrites `docs/API.md` from the route decorators.

### Deliberate lazy imports

`routes/analysis.py` and `routes/routine.py` import the heavy services (`resume_analyzer`, `engine`, `mistral_chat`, …)
*inside* the view. This is intentional: those modules pull in PDF/DOCX/ReportLab/optional NLP libraries, and a missing
or blocked library must only break that one feature, not the whole server.

### Configuration

All settings live in `app/config.py` and are driven by environment variables / `backend/.env` (see `.env.example`).
Upload folders are defined once there (`UPLOAD_DIR`, `PROFILE_PICTURE_DIR`, `VIDEO_DIR`, `COMMUNITY_IMAGE_DIR`).

## Frontend

* `config/api.js` exports `API_BASE_URL` (`REACT_APP_API_URL`, default `http://localhost:5000`). Never hard-code the address.
* `services/` – thin `fetch` wrappers and token storage (`authService`).
* `pages/` – route-level screens, wired in `App.js` (lazy-loaded where heavy).
* `components/` grouped by purpose: `auth/` (login modal, route guard), `common/` (buttons, inputs), `layout/` (navbar, footer),
  `home/` (landing sections), and feature folders (`community/`, `explore/`, `postMatrics/`, `resume/`, `charts/`).
