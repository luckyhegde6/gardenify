"""Shared auth dependencies for API protection."""

import logging
from typing import Annotated

from fastapi import Depends, Header, HTTPException
from supabase import create_client

from api.config import settings

logger = logging.getLogger(__name__)


def get_service_client():
    if not settings.supabase_url or not settings.supabase_service_role_key:
        raise HTTPException(503, "Supabase not configured")
    return create_client(settings.supabase_url, settings.supabase_service_role_key)


def require_user(
    authorization: Annotated[str | None, Header()] = None,
) -> str:
    """Verify a Supabase JWT, returning the authenticated user id."""
    if not authorization:
        raise HTTPException(401, "Missing Authorization header")
    token = authorization.removeprefix("Bearer ")
    client = get_service_client()
    try:
        return client.auth.get_user(token).user.id
    except Exception as e:
        raise HTTPException(401, f"Invalid token: {e}") from e


def require_admin(user_id: str = Depends(require_user)) -> str:
    """Verify the caller is an authenticated admin; returns the admin's user id."""
    client = get_service_client()
    profile = (
        client.table("users")
        .select("is_admin")
        .eq("id", user_id)
        .maybe_single()
        .execute()
    )
    if not profile.data or not profile.data.get("is_admin"):
        raise HTTPException(403, "Admin access required")
    return user_id