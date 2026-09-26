from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from .models import User


def roles_required(*roles):
    def wrapper(fn):
        @wraps(fn)
        def decorated(*args, **kwargs):
            verify_jwt_in_request()
            user = User.query.get(get_jwt_identity())
            # Admin routes formerly permitted staff accounts. The application
            # now has one authorized admin, the owner, so old staff JWTs cannot
            # retain access after public registration has been removed.
            allowed = ("owner",) if "owner" in roles else roles
            if not user or not user.is_active or user.role not in allowed:
                return jsonify({"error": "Permission denied"}), 403
            return fn(*args, **kwargs)
        return decorated
    return wrapper
