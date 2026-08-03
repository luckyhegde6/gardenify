"""Auth API routes — login (rate-limited) and password recovery flows."""

import logging

from fastapi import APIRouter, HTTPException

from api.config import settings
from api.models.schemas import (
    AuthUserResponse,
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    LoginRequest,
    LoginResponse,
    ResetPasswordRequest,
)
from api.routes.deps import get_service_client
from api.services.auth_security import (
    LockedOutError,
    ResetPendingError,
    check_login_allowed,
    check_reset_allowed,
    record_login_failure,
    record_login_success,
    record_reset_completed,
    record_reset_sent,
)

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "/auth/login",
    response_model=LoginResponse,
    summary="Log in a user",
    description="Sign a user in and return session tokens. Failed attempts are rate-limited with a temporary account lockout.",
)
def login(body: LoginRequest) -> LoginResponse:
    try:
        check_login_allowed(body.email.lower())
    except LockedOutError as e:
        raise HTTPException(429, f"Too many failed attempts. Try again later. ({e!s})") from e

    client = get_service_client()
    try:
        resp = client.auth.sign_in_with_password(
            {"email": body.email.lower(), "password": body.password}
        )
    except Exception:
        remaining = record_login_failure(body.email.lower())
        if remaining == 0:
            raise HTTPException(
                429,
                f"Too many failed attempts. Account locked. Try again in {settings.login_lockout_seconds // 60} minutes.",
            )
        raise HTTPException(401, "Invalid email or password")

    record_login_success(body.email.lower())
    session = resp.session
    user = resp.user
    is_admin = False
    try:
        profile = (
            client.table("users")
            .select("is_admin")
            .eq("id", user.id)
            .maybe_single()
            .execute()
        )
        is_admin = bool(profile.data and profile.data.get("is_admin"))
    except Exception as exc:
        logger.warning("Could not read is_admin for %s: %s", user.id, exc)

    return LoginResponse(
        access_token=session.access_token,
        refresh_token=session.refresh_token,
        expires_at=getattr(session, "expires_at", None),
        user=AuthUserResponse(id=user.id, email=user.email or "", is_admin=is_admin),
    )


@router.post(
    "/auth/forgot-password",
    response_model=ForgotPasswordResponse,
    summary="Send a password recovery email",
    description="Sends a password recovery link to the given email. Each email may only have one pending reset at a time until it is completed, and resends are rate-limited.",
)
def forgot_password(body: ForgotPasswordRequest) -> ForgotPasswordResponse:
    email = body.email.lower()
    try:
        check_reset_allowed(email)
    except ResetPendingError as e:
        raise HTTPException(429, "A password reset is already pending for this email. Complete it before requesting another.") from e

    client = get_service_client()
    try:
        client.auth.reset_password_for_email(email, {"redirect_to": settings.reset_redirect_url})
    except Exception:
        # Never reveal whether the email exists; always look like a success.
        logger.info("forgot-password request for %s failed", email)
        return ForgotPasswordResponse()

    record_reset_sent(email)
    return ForgotPasswordResponse()


@router.post(
    "/auth/reset-password",
    response_model=ForgotPasswordResponse,
    summary="Set a new password using the recovery code",
    description="Exchange the recovery code from the emailed link for a session, then set the new password. Clears the pending reset for the email.",
)
def reset_password(body: ResetPasswordRequest) -> ForgotPasswordResponse:
    client = get_service_client()
    email = body.email.lower()
    try:
        session = client.auth.verify_otp(
            {"email": email, "token": body.code, "type": "recovery"}
        )
    except Exception as e:
        raise HTTPException(400, "Invalid or expired reset code") from e

    user_id = session.user.id
    try:
        client.auth.admin.update_user_by_id(
            user_id, {"password": body.new_password}
        )
    except Exception as e:
        raise HTTPException(400, "Could not update password") from e

    record_reset_completed(email)
    return ForgotPasswordResponse(detail="password_updated")