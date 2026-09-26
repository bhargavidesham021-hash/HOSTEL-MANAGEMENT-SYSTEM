# Jai Tulja Bhavani Hostel Management

React/Vite frontend and Flask/SQLAlchemy API for hostel operations. Local development defaults to SQLite; production uses PostgreSQL through `DATABASE_URL`.

## Local development

Backend (PowerShell):

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
# Set JWT_SECRET_KEY and ADMIN_EMAIL / ADMIN_PASSWORD in backend/.env.
python run.py
```

The backend runs at `http://localhost:5000`; `GET /health` checks both Flask and its database connection. Set `ADMIN_EMAIL` and `ADMIN_PASSWORD` to create an initial owner once. Existing account passwords are never changed by startup. For an existing local database, the former `bhargavi021@gmail.com` / `MRECW` development account is not recreated automatically; configure a bootstrap account or retain the existing database account.

Frontend (second terminal):

```powershell
cd frontend
npm ci
Copy-Item .env.example .env
npm run dev
```

The frontend runs at `http://localhost:5173`. Local SQLite is stored in `backend/hostel.db` and is only the fallback when `DATABASE_URL` is unset.

## Production deployment (Render/Railway or equivalent)

### Backend

- Root/build context: `backend`
- Install/build command: `pip install -r requirements.txt`
- Start command: `gunicorn run:app`
- Health check path: `/health`
- Set `DATABASE_URL` to the provider's PostgreSQL URL. `postgres://` is normalized automatically.
- Set `JWT_SECRET_KEY` to a long random secret (for example generate one with `python -c "import secrets; print(secrets.token_urlsafe(48))"`). Production startup refuses to run without it.
- Set `CORS_ORIGINS` to the exact comma-separated frontend origins, for example `https://your-app.vercel.app`.
- For the initial owner, set `ADMIN_EMAIL` and `ADMIN_PASSWORD`; optionally set `ADMIN_USERNAME` and `ADMIN_NAME`. Startup creates that account only if it does not already exist and never resets an existing password. Remove `ADMIN_PASSWORD` after bootstrap if desired.
- Optional password reset email requires `SMTP_HOST`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`, `SMTP_FROM_EMAIL`, and `SMTP_USE_TLS`.
- Tables are created idempotently from existing SQLAlchemy models at app startup. Startup does not drop tables or clear records. `create_all()` does not alter existing production columns; use a versioned migration when applying future model changes.

### Frontend

- Root/build context: `frontend`
- Install command: `npm ci`
- Build command: `npm run build`
- Output directory: `dist`
- Set `VITE_API_BASE_URL=https://YOUR-BACKEND-DOMAIN/api` in the frontend build environment, then rebuild/redeploy. Vite embeds this value into the bundle.
- `frontend/vercel.json` rewrites SPA routes to `index.html` for direct navigation and refreshes.

### First deployment order

1. Create a PostgreSQL database and copy its connection URL.
2. Deploy the backend with `DATABASE_URL`, `JWT_SECRET_KEY`, and `CORS_ORIGINS` set.
3. Set `ADMIN_EMAIL` and a strong `ADMIN_PASSWORD` for the initial owner account.
4. Start the backend once. It creates missing tables and inserts the initial hostel defaults and owner only when required.
5. Verify `https://YOUR-BACKEND-DOMAIN/health` returns HTTP 200 with `{"status":"ok","app":"JTBH Hostel Management"}`.
6. Deploy the frontend with `VITE_API_BASE_URL=https://YOUR-BACKEND-DOMAIN/api` and build again.
7. Sign in with the configured admin email/password. Confirm the dashboard loads and an authenticated API request succeeds.

## Moving existing SQLite data to PostgreSQL

Do not copy `hostel.db` to the production host. Back up the SQLite file and create the PostgreSQL schema first by starting the deployed backend once. Run the importer from `backend/` in an environment that can reach both databases:

```powershell
$env:SQLITE_URL = "sqlite:///hostel.db"
$env:DATABASE_URL = "postgresql://USER:PASSWORD@HOST:5432/DATABASE"
python migrate_sqlite_to_postgres.py
```

The script reflects every table present in both databases, preserves IDs and row data (including user password hashes), copies in foreign-key order, and adjusts PostgreSQL sequences. It stops if any destination table has rows and never deletes destination data. Review the printed per-table row counts and take verified backups before migration. For large datasets, schedule an outage or use a database migration service to avoid writes during the copy.

## Deployment troubleshooting

- `GET /health` returns 503: check PostgreSQL availability, network access, and `DATABASE_URL`; response does not include credentials.
- Browser CORS errors: add the exact frontend origin (scheme and host, no path) to `CORS_ORIGINS` and redeploy backend.
- API requests point to the wrong host: set `VITE_API_BASE_URL` in the frontend build environment and rebuild; changing it after build has no effect.
- Login returns 401: verify the owner exists in PostgreSQL and use its configured email. Startup does not reset passwords.
- Expired or invalid JWTs return JSON 401 and the frontend returns to sign-in with an explanation.
