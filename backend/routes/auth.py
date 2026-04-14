from functools import wraps

from flask import Blueprint, current_app, g, jsonify, request

from backend.services.user_service import (
    AuthenticationError,
    DuplicateUserError,
    InvalidTokenError,
    authenticate_user,
    create_user,
    decode_token,
    serialize_user,
)

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


def get_optional_auth_user():
    authorization = request.headers.get("Authorization", "")
    prefix = "Bearer "
    if not authorization:
        return None
    if not authorization.startswith(prefix):
        raise InvalidTokenError("Invalid token")

    token = authorization[len(prefix) :]
    return decode_token(
        token=token,
        secret_key=current_app.config["JWT_SECRET_KEY"],
    )


def require_auth(view_func):
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        try:
            g.current_user = get_optional_auth_user()
            if g.current_user is None:
                return jsonify({"error": "Unauthorized"}), 401
        except InvalidTokenError:
            return jsonify({"error": "Unauthorized"}), 401

        return view_func(*args, **kwargs)

    return wrapped


@auth_bp.post("/register")
def register():
    payload = request.get_json(silent=True) or {}
    try:
        user = create_user(
            email=payload.get("email"),
            username=payload.get("username"),
            password=payload.get("password"),
            secret_key=current_app.config["JWT_SECRET_KEY"],
        )
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except DuplicateUserError as exc:
        return jsonify({"error": str(exc)}), 409

    return jsonify(user), 201


@auth_bp.post("/login")
def login():
    payload = request.get_json(silent=True) or {}
    try:
        result = authenticate_user(
            email=payload.get("email"),
            password=payload.get("password"),
            secret_key=current_app.config["JWT_SECRET_KEY"],
        )
    except (ValueError, AuthenticationError) as exc:
        return jsonify({"error": str(exc)}), 401 if isinstance(exc, AuthenticationError) else 400

    return jsonify(result), 200


@auth_bp.get("/me")
@require_auth
def me():
    return jsonify({"user": serialize_user(g.current_user)}), 200
