# Jai Tulja Bhavani Deluxe Boys Hostel Management System

Production-oriented hostel management system for Jai Tulja Bhavani Deluxe Boys Hostel, Near Aurora College, Aushapur.

## Stack

- Frontend: React, Vite, Tailwind CSS, React Router, Axios, Lucide icons, Recharts
- Backend: Flask REST API, SQLAlchemy, JWT auth, Flask-CORS
- Development database: SQLite
- Production database: PostgreSQL via `DATABASE_URL`

## Implemented Core Modules

- Public hostel landing page with Admin Login and Student Login
- JWT owner login with password hashing
- Student login by Student ID/phone plus admin-created password
- Seeded editable hostel structure: 3 floors, 10 rooms, 70 slots
- Dashboard with month selection and payment-based collected revenue
- Visual room layout and room detail with Bedroom/Hall slots
- Student creation with generated IDs like `JTBH2026001`
- Student removal and owner restore using status changes, not hard deletes
- Slot allocation with server-side double-allocation prevention
- Monthly invoice generation and automatic payment status calculation
- Partial payment recording with unique receipts like `JTBH-REC-2026-0001`
- Dues page with WhatsApp reminder links
- Expense add/edit/soft-delete with audit history
- Complaint register
- Outing request and admin status workflow
- Student dashboard for profile, payments, outings, complaints, and announcements
- Settings and report summary foundations
- Audit log table for important actions

## Backend Setup

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python run.py
```

The backend starts at `http://localhost:5000`.

Default owner account:

- Email: `bhargavi021@gmail.com`
- Password: `MRECW`

Change this password before real use.

## Frontend Setup

```powershell
cd frontend
npm install
Copy-Item .env.example .env
npm run dev
```

The frontend starts at `http://localhost:5173`.

Student accounts are created from the admin Students page. Enter a student portal password while adding the student, then the student can log in using their generated Student ID or phone number.

## Production Notes

- Set a strong `JWT_SECRET_KEY`.
- Use PostgreSQL by setting `DATABASE_URL`, for example `postgresql://user:password@host:5432/dbname`.
- Keep uploads on local disk for development. The backend is structured so S3 or Cloudinary storage can be added later.
- Replace `db.create_all()` with Alembic/Flask-Migrate migrations before multi-environment production rollout.
- Put the frontend and backend behind HTTPS and restrict `CORS_ORIGINS` to the deployed frontend URL.

## Next Modules To Extend

The data model already has tables for attendance, leave requests, visitors, announcements, notifications, and audit logs. Their full CRUD screens can be added without changing the core architecture.
