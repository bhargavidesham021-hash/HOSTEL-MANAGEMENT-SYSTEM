from datetime import datetime
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
from .extensions import db
from .models import User
from .routes import api
from .seed import seed_database
import os


def create_app():
    load_dotenv()
    app_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.abspath(os.path.join(app_dir, ".."))
    app = Flask(__name__, instance_path=app_dir)
    default_db = "sqlite:///" + os.path.join(backend_dir, "hostel.db").replace("\\", "/")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", default_db)
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "dev-only-change-me")
    app.config["UPLOAD_FOLDER"] = os.getenv("UPLOAD_FOLDER", "uploads")
    app.config["MAX_CONTENT_LENGTH"] = int(os.getenv("MAX_CONTENT_LENGTH", "5242880"))

    db.init_app(app)
    JWTManager(app)
    cors_origins = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173,http://192.168.1.140:5173",
    ).split(",")
    CORS(app, origins=[origin.strip() for origin in cors_origins])

    app.register_blueprint(api, url_prefix="/api")

    @app.get("/health")
    def health():
        return {"status": "ok", "app": "JTBH Hostel Management"}

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Not found"}), 404

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({"error": str(error)}), 400

    with app.app_context():
        db.create_all()
        ensure_sqlite_schema(app)
        seed_database()

    return app


def ensure_sqlite_schema(app):
    if not app.config["SQLALCHEMY_DATABASE_URI"].startswith("sqlite"):
        return
    additions = {
        "complaint": [("subject", "VARCHAR(255)"), ("title", "VARCHAR(255)")],
        "student": [
            ("joining_date", "DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP"),
            ("removed_at", "DATETIME"),
            ("removed_by_id", "INTEGER"),
            ("removal_reason", "TEXT"),
            ("restored_at", "DATETIME"),
        ],
        "expense": [
            ("expense_date", "DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP"),
            ("notes", "TEXT"),
            ("bill_path", "VARCHAR(255)"),
            ("edited_by_id", "INTEGER"),
            ("edited_at", "DATETIME"),
            ("is_deleted", "BOOLEAN DEFAULT 0 NOT NULL"),
            ("deleted_by_id", "INTEGER"),
            ("deleted_at", "DATETIME"),
            ("deletion_reason", "TEXT"),
        ],
        "payment": [
            ("payment_date", "DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP"),
        ],
    }
    engine = db.engine
    with engine.begin() as conn:
        for table, columns in additions.items():
            existing = {row[1] for row in conn.exec_driver_sql(f"PRAGMA table_info({table})").fetchall()}
            for name, definition in columns:
                if name not in existing:
                    conn.exec_driver_sql(f"ALTER TABLE {table} ADD COLUMN {name} {definition}")
            if table == "student":
                conn.exec_driver_sql("UPDATE student SET joining_date = joining_date || ' 00:00:00' WHERE joining_date NOT LIKE '% %'")
            elif table == "expense":
                conn.exec_driver_sql("UPDATE expense SET expense_date = expense_date || ' 00:00:00' WHERE expense_date NOT LIKE '% %'")
            elif table == "payment":
                conn.exec_driver_sql("UPDATE payment SET payment_date = payment_date || ' 00:00:00' WHERE payment_date NOT LIKE '% %'")
            elif table == "complaint":
                # Migrate records created by the pre-title complaint implementation.
                conn.exec_driver_sql("UPDATE complaint SET title = COALESCE(NULLIF(title, ''), subject, category, 'Complaint')")
