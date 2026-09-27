# Jai Tulja Bhavani Hostel Management

React/Vite frontend and Flask/SQLAlchemy API deployed together in one Vercel project. Supabase PostgreSQL stores production data; local development uses SQLite.

## Local development

Backend terminal (PowerShell):

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
# Set JWT_SECRET_KEY and ADMIN_EMAIL / ADMIN_PASSWORD in backend/.env if bootstrapping a local owner.
python run.py
```

The backend listens at `http://localhost:5000`; `GET /health` checks Flask and its database connection. If `DATABASE_URL` is unset, local SQLite lives at `backend/hostel.db`.

Frontend terminal:

```powershell
cd frontend
npm ci
Copy-Item .env.example .env
npm run dev
```

The frontend runs at `http://localhost:5173` and calls `http://localhost:5000/api` during development.

## One project on Vercel

Import this repository as a single Vercel project and set Root Directory to `HOSTEL MANAGEMENT SYSTEM` (the application folder inside this Git repository). The root `index.py` exports the Flask WSGI app. Vercel runs it as a Python Function; its Flask routes handle the API, while the compiled Vite files are included in that function and served through the React SPA fallback. No separate backend service is used. The API and UI share the deployment origin.

Set these Vercel environment variables for Production and Preview as needed:

- `DATABASE_URL`: Supabase PostgreSQL connection URI. Use Supabase's Transaction pooler URI (port 6543) for Vercel serverless requests; keep the credential only in Vercel's server-side environment.
- `JWT_SECRET_KEY`: a random secret with at least 32 characters. It is server-only and must not use a `VITE_` prefix.
- `VITE_API_BASE_URL`: `/api` (the app also defaults to same-origin `/api` for production builds).
- Optional owner bootstrap: `ADMIN_EMAIL`, `ADMIN_PASSWORD`, and optionally `ADMIN_USERNAME`, `ADMIN_NAME`. Startup creates the owner only when absent and never changes an existing password. Set a new strong production password; do not reuse a local development password.

The app requires SSL for PostgreSQL and uses SQLAlchemy `NullPool`, while Supabase's Transaction pooler reuses database-side connections. The Vercel app takes a PostgreSQL advisory transaction lock during first startup so parallel cold starts serialize schema creation and seeding. SQLAlchemy's `create_all()` creates missing tables but does not alter existing definitions. For a fresh installation, deploy normally and the app creates its schema and defaults. To migrate the existing SQLite data, explicitly set `SQLITE_URL` to the intended source database; do not rely on an implicit default because the project can contain older SQLite files. Run `backend/initialize_postgres_schema.py` first (it creates tables without seed rows), then `backend/migrate_sqlite_to_postgres.py` from an environment that can reach both databases. The importer refuses nonempty destination tables. If the local database has an owner, set `ADMIN_EMAIL` to that owner's email and `ADMIN_PASSWORD` to a new production password for the migration process; the importer replaces that owner's local password hash with a newly generated hash and never prints it. Back up both databases before migrating. Complaint attachment uploads use `/tmp` in Vercel and are temporary; only their database records persist across function instances.

The public endpoints use the same Vercel domain:

- `/`, `/login`, `/dashboard`, and other React routes serve the SPA, including direct refreshes.
- `/health` checks the Flask app and database.
- `/api/auth/login` and all other `/api/*` requests go to the real Flask routes.

Existing database tables are not dropped. The SQLite migration utility skips the retired feature's legacy table.

## Deploy

1. Create a Supabase project. In **Connect**, copy the Transaction pooler PostgreSQL URI (port 6543) and keep it in server-side environment settings only.
2. If migrating existing SQLite data, run the schema-only and migration commands above using the Supabase URI, then use that URI for Vercel. For an empty database, skip migration.
3. Import the repository in Vercel as one project. Set Root Directory to `HOSTEL MANAGEMENT SYSTEM`; the root `vercel.json` there builds the frontend and includes it with Flask.
4. Add `DATABASE_URL` and a newly generated `JWT_SECRET_KEY` in Vercel. Set `VITE_API_BASE_URL` to `/api`. Add `ADMIN_EMAIL` and a new strong `ADMIN_PASSWORD` only when bootstrapping a new owner.
5. Deploy. Verify `/health` returns HTTP 200 and that login submits to `/api/auth/login` on that same domain.

Supabase database setup is separate from Supabase Auth: this app keeps its Flask user table and Flask-JWT-Extended authentication. Startup safely creates missing tables; it never resets an existing owner password or deletes existing rows.

## Troubleshooting

- A browser request to an invalid host indicates a stale frontend build or incorrect `VITE_API_BASE_URL`. Set it to `/api` in Vercel and redeploy.
- `/health` returns 503 when the configured database cannot be reached; check the pooler URI and credentials.
- Login returns 401 when the account/password is not present in the production `user` table. Configure a production owner bootstrap or migrate the intended account and use its existing password.
- Local frontend requests need the Flask dev server on port 5000 and the local `.env.example` value.
