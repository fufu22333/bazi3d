import base64
import hashlib
import hmac
import json
import time

from werkzeug.security import check_password_hash, generate_password_hash

from backend.models import SessionLocal
from backend.models.user import User


class DuplicateUserError(Exception):
    pass


class AuthenticationError(Exception):
    pass


class InvalidTokenError(Exception):
    pass


def _base64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("utf-8")


def _base64url_decode(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(f"{data}{padding}")


def serialize_user(user: User) -> dict:
    return {
        "id": user.id,
        "email": user.email,
        "username": user.username,
    }


def generate_token(user: User, secret_key: str) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    payload = {
        "sub": user.id,
        "email": user.email,
        "exp": int(time.time()) + 24 * 60 * 60,
    }
    header_segment = _base64url_encode(
        json.dumps(header, separators=(",", ":")).encode("utf-8")
    )
    payload_segment = _base64url_encode(
        json.dumps(payload, separators=(",", ":")).encode("utf-8")
    )
    signing_input = f"{header_segment}.{payload_segment}".encode("utf-8")
    signature = hmac.new(
        secret_key.encode("utf-8"), signing_input, hashlib.sha256
    ).digest()
    signature_segment = _base64url_encode(signature)
    return f"{header_segment}.{payload_segment}.{signature_segment}"


def decode_token(token: str, secret_key: str) -> User:
    try:
        header_segment, payload_segment, signature_segment = token.split(".")
    except ValueError as exc:
        raise InvalidTokenError("Invalid token") from exc

    signing_input = f"{header_segment}.{payload_segment}".encode("utf-8")
    expected_signature = hmac.new(
        secret_key.encode("utf-8"), signing_input, hashlib.sha256
    ).digest()
    actual_signature = _base64url_decode(signature_segment)
    if not hmac.compare_digest(expected_signature, actual_signature):
        raise InvalidTokenError("Invalid token")

    try:
        payload = json.loads(_base64url_decode(payload_segment))
    except (json.JSONDecodeError, ValueError) as exc:
        raise InvalidTokenError("Invalid token") from exc

    if payload.get("exp", 0) < int(time.time()):
        raise InvalidTokenError("Token expired")

    session = SessionLocal()
    user = session.get(User, payload.get("sub"))
    if user is None:
        raise InvalidTokenError("Invalid token user")
    return user


def create_user(email: str | None, username: str | None, password: str | None, secret_key: str) -> dict:
    if not email or not username or not password:
        raise ValueError("email, username and password are required")

    session = SessionLocal()
    if session.query(User).filter_by(email=email).first() is not None:
        raise DuplicateUserError("Email already exists")
    if session.query(User).filter_by(username=username).first() is not None:
        raise DuplicateUserError("Username already exists")

    user = User(
        email=email,
        username=username,
        password_hash=generate_password_hash(password),
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    return {"user": serialize_user(user), "token": generate_token(user, secret_key)}


def authenticate_user(email: str | None, password: str | None, secret_key: str) -> dict:
    if not email or not password:
        raise ValueError("email and password are required")

    session = SessionLocal()
    user = session.query(User).filter_by(email=email).first()
    if user is None or not check_password_hash(user.password_hash, password):
        raise AuthenticationError("Invalid credentials")

    return {"user": serialize_user(user), "token": generate_token(user, secret_key)}
