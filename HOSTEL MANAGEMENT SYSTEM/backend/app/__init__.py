import os

from dotenv import load_dotenv
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from sqlalchemy import text
from sqlalchemy.engine import make_url
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.pool import NullPool

from .extensions import db
from .models import User
from .routes import api
from .seed import seed_database


def create_app():
    load_dotenv()
    app_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.abspath(os.path.join(app_dir, ".."))
    app = Flask(__name__, instance_path=app_dir)

    is_vercel = os.getenv("VERCEL") == "1" or bool(os.getenv("VERCEL_ENV"))
    is_production = (
        os.getenv("FLASK_ENV", "").lower() == "production"
        or os.getenv("ENVIRONMENT", "").lower() == "production"
        or is_vercel
    )
    database_url = os.getenv("DATABASE_URL", "").strip()
    if database_url.startswith("postgres://"):
        database_url = "postgresql://" + database_url[len("postgres://"):]
    is_production = is_production or database_url.startswith("postgresql")
    if not database_url:
        if is_production:
            raise RuntimeError("DATABASE_URL must be configured in production")
        database_url = "sqlite:///" + os.path.join(backend_dir, "hostel.db").replace("\\", "/")
    elif is_production and not database_url.startswith("postgresql"):
        raise RuntimeError("Production DATABASE_URL must point to PostgreSQL")
    if database_url.startswith("postgresql"):
        parsed_url = make_url(database_url)
        if "sslmode" not in parsed_url.query:
            parsed_url = parsed_url.set(query={**parsed_url.query, "sslmode": "require"})
        database_url = parsed_url.render_as_string(hide_password=False)
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {"pool_pre_ping": True}
    if database_url.startswith("postgresql"):
        # Vercel is serverless. Let Supavisor's transaction pooler manage
        # database connections instead of retaining sockets across invocations.
        app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
            "poolclass": NullPool,
            "connect_args": {"connect_timeout": 10},
        }
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    jwt_secret = os.getenv("JWT_SECRET_KEY", "").strip()
    if is_production and len(jwt_secret) < 32:
        raise RuntimeError("JWT_SECRET_KEY must contain at least 32 characters in production")
    if not jwt_secret:
        jwt_secret = "dev-only-change-me"
    app.config["JWT_SECRET_KEY"] = jwt_secret
    default_upload_folder = "/tmp/hostel-uploads" if is_vercel else "uploads"
    app.config["UPLOAD_FOLDER"] = os.getenv("UPLOAD_FOLDER", default_upload_folder)
    app.config["MAX_CONTENT_LENGTH"] = int(os.getenv("MAX_CONTENT_LENGTH", "5242880"))

    db.init_app(app)
    jwt = JWTManager(app)

    @jwt.unauthorized_loader
    def missing_jwt(reason):
        return jsonify({"error": "Authentication required"}), 401

    @jwt.invalid_token_loader
    def invalid_jwt(reason):
        return jsonify({"error": "Invalid authentication token"}), 401

    @jwt.expired_token_loader
    def expired_jwt(jwt_header, jwt_payload):
        return jsonify({"error": "Your session has expired. Please log in again."}), 401
    configured_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173")
    origins = [origin.strip().rstrip("/") for origin in configured_origins.split(",") if origin.strip()]
    CORS(app, resources={r"/*": {"origins": origins}}, allow_headers=["Content-Type", "Authorization"], methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
    app.register_blueprint(api, url_prefix="/api")

    @app.route("/api", defaults={"api_path": ""}, methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
    @app.route("/api/<path:api_path>", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
    def unknown_api_route(api_path):
        return jsonify({"error": "Not found"}), 404

    @app.get("/health")
    def health():
        try:
            db.session.execute(text("SELECT 1"))
            return {"status": "ok", "app": "JTBH Hostel Management"}
        except SQLAlchemyError:
            db.session.rollback()
            return jsonify({"status": "error", "error": "Database connection failed"}), 503

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Not found"}), 404

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({"error": "Invalid request"}), 400

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        app.logger.exception("Unhandled server error")
        return jsonify({"error": "Internal server error"}), 500

    @app.errorhandler(SQLAlchemyError)
    def database_error(error):
        db.session.rollback()
        app.logger.error("Database operation failed: %s", type(error).__name__)
        return jsonify({"error": "Database operation failed"}), 503

    # The Vercel Flask function serves both the API and the compiled Vite app.
    # Exact API and health routes above take precedence; unknown API paths stay
    # JSON 404s instead of being swallowed by the React SPA fallback.
    frontend_dist = os.path.abspath(os.path.join(backend_dir, "..", "frontend", "dist"))

    @app.get("/")
    def frontend_index():
        return send_from_directory(frontend_dist, "index.html")

    @app.get("/<path:frontend_path>")
    def frontend_routes(frontend_path):
        if frontend_path == "api" or frontend_path.startswith("api/"):
            return jsonify({"error": "Not found"}), 404
        candidate = os.path.join(frontend_dist, frontend_path)
        if os.path.isfile(candidate):
            return send_from_directory(frontend_dist, frontend_path)
        return send_from_directory(frontend_dist, "index.html")

    with app.app_context():
        if database_url.startswith("postgresql"):
            # Serialize first boot across parallel cold starts; create_all and
            # seed run in the same transaction, then release the transaction
            # lock when seed_database commits.
            db.session.execute(text("SELECT pg_advisory_xact_lock(1680096768)"))
            db.metadata.create_all(bind=db.session.connection())
            seed_database()
        else:
            db.create_all()
            ensure_sqlite_schema(app)
            seed_database()

    return app


def ensure_sqlite_schema(app):
    if not app.config["SQLALCHEMY_DATABASE_URI"].startswith("sqlite"):
        return
    additions = {
        "complaint": [("subject", "VARCHAR(255)"), ("title", "VARCHAR(255)"), ("assigned_to_id", "INTEGER"), ("admin_response", "TEXT"), ("last_updated_at", "DATETIME")],
        "student": [("joining_date", "DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP"), ("removed_at", "DATETIME"), ("removed_by_id", "INTEGER"), ("removal_reason", "TEXT"), ("restored_at", "DATETIME")],
        "expense": [("expense_date", "DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP"), ("notes", "TEXT"), ("bill_path", "VARCHAR(255)"), ("edited_by_id", "INTEGER"), ("edited_at", "DATETIME"), ("is_deleted", "BOOLEAN DEFAULT 0 NOT NULL"), ("deleted_by_id", "INTEGER"), ("deleted_at", "DATETIME"), ("deletion_reason", "TEXT")],
        "payment": [("payment_date", "DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP")],
        "notification": [("user_id", "INTEGER")],
        "outing_request": [("request_no", "VARCHAR(40)"), ("admin_remarks", "TEXT")],
    }
    with db.engine.begin() as conn:
        for table, columns in additions.items():
            existing = {row[1] for row in conn.exec_driver_sql(f"PRAGMA table_info({table})").fetchall()}
            if not existing:
                continue
            for name, definition in columns:
                if name not in existing:
                    conn.exec_driver_sql(f"ALTER TABLE {table} ADD COLUMN {name} {definition}")
        # Keep SQLite's legacy date normalization limited to rows that need it.
        for table, column in (("student", "joining_date"), ("expense", "expense_date"), ("payment", "payment_date")):
            conn.exec_driver_sql(f"UPDATE {table} SET {column} = {column} || ' 00:00:00' WHERE {column} NOT LIKE '% %'")
        conn.exec_driver_sql("UPDATE complaint SET title = COALESCE(NULLIF(title, ''), subject, category, 'Complaint')")
        conn.exec_driver_sql("UPDATE complaint SET last_updated_at = COALESCE(last_updated_at, updated_at, created_at)")
