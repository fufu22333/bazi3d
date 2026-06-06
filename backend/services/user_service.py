import base64
import hashlib
import hmac
import json
import time

from werkzeug.security import check_password_hash, generate_password_hash

from backend.models import SessionLocal
from backend.models.evaluation_log import EvaluationLog
from backend.models.favorite import Favorite
from backend.models.generation_task import GenerationTask
from backend.models.input_profile import InputProfile
from backend.models.model_asset import ModelAsset
from backend.models.user import User
from backend.models.work import Work


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


def _serialize_datetime(value) -> str | None:
    return value.isoformat() if value else None


def export_user_data(user: User) -> dict:
    session = SessionLocal()
    db_user = session.get(User, user.id)
    if db_user is None:
        raise InvalidTokenError("Invalid token user")

    input_profiles = (
        session.query(InputProfile)
        .filter_by(user_id=db_user.id)
        .order_by(InputProfile.id)
        .all()
    )
    tasks = (
        session.query(GenerationTask)
        .filter_by(user_id=db_user.id)
        .order_by(GenerationTask.id)
        .all()
    )
    task_ids = [task.id for task in tasks]
    assets = (
        session.query(ModelAsset)
        .join(GenerationTask)
        .filter(GenerationTask.user_id == db_user.id)
        .order_by(ModelAsset.id)
        .all()
    )
    works = session.query(Work).filter_by(user_id=db_user.id).order_by(Work.id).all()

    return {
        "export_version": "phase3-beta-v1",
        "user": serialize_user(db_user),
        "input_profiles": [
            {
                "id": profile.id,
                "display_name": profile.display_name,
                "gender": profile.gender,
                "birth_datetime": _serialize_datetime(profile.birth_datetime),
                "calendar_type": profile.calendar_type,
                "birth_location": profile.birth_location,
                "style_profile": profile.style_profile or {},
                "extra_payload": profile.extra_payload or {},
                "reference_image_url": profile.reference_image_url,
                "created_at": _serialize_datetime(profile.created_at),
            }
            for profile in input_profiles
        ],
        "tasks": [
            {
                "id": task.id,
                "input_profile_id": task.input_profile_id,
                "status": task.status,
                "provider": task.provider,
                "external_task_id": task.external_task_id,
                "character_task_ref": task.character_task_ref,
                "spirit_task_ref": task.spirit_task_ref,
                "error_message": task.error_message,
                "created_at": _serialize_datetime(task.created_at),
                "updated_at": _serialize_datetime(task.updated_at),
            }
            for task in tasks
        ],
        "assets": [
            {
                "id": asset.id,
                "generation_task_id": asset.generation_task_id,
                "asset_type": asset.asset_type,
                "url": asset.storage_url,
                "file_format": asset.file_format,
                "metadata": asset.asset_metadata or {},
                "created_at": _serialize_datetime(asset.created_at),
            }
            for asset in assets
        ],
        "works": [
            {
                "id": work.id,
                "primary_asset_id": work.primary_asset_id,
                "title": work.title,
                "description": work.description,
                "visibility": work.visibility,
                "allow_remix": work.allow_remix,
                "created_at": _serialize_datetime(work.created_at),
            }
            for work in works
        ],
        "task_ids": task_ids,
    }


def delete_user_account(user: User) -> None:
    session = SessionLocal()
    db_user = session.get(User, user.id)
    if db_user is None:
        raise InvalidTokenError("Invalid token user")

    task_ids = [
        task_id
        for (task_id,) in session.query(GenerationTask.id)
        .filter_by(user_id=db_user.id)
        .all()
    ]
    work_ids = [
        work_id
        for (work_id,) in session.query(Work.id).filter_by(user_id=db_user.id).all()
    ]

    if work_ids:
        session.query(Favorite).filter(Favorite.work_id.in_(work_ids)).delete(
            synchronize_session=False
        )
        session.query(EvaluationLog).filter(EvaluationLog.work_id.in_(work_ids)).delete(
            synchronize_session=False
        )
    session.query(Favorite).filter_by(user_id=db_user.id).delete(
        synchronize_session=False
    )
    if task_ids:
        session.query(EvaluationLog).filter(
            EvaluationLog.generation_task_id.in_(task_ids)
        ).delete(synchronize_session=False)
    session.query(Work).filter_by(user_id=db_user.id).delete(synchronize_session=False)
    if task_ids:
        session.query(ModelAsset).filter(
            ModelAsset.generation_task_id.in_(task_ids)
        ).delete(synchronize_session=False)
    session.query(GenerationTask).filter_by(user_id=db_user.id).delete(
        synchronize_session=False
    )
    session.query(InputProfile).filter_by(user_id=db_user.id).delete(
        synchronize_session=False
    )
    session.delete(db_user)
    session.commit()


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
