"""Admin API routes — user management."""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from api.config import settings
from api.models.schemas import (
    AdminUserListResponse,
    AdminUserResponse,
    AdminUserUpdate,
)
from api.routes.deps import get_service_client, require_admin
from api.services.auth_security import record_reset_completed

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get(
    "/admin/users",
    response_model=AdminUserListResponse,
    summary="List all users (admin)",
    description="List all registered users with pagination and optional email search. Requires admin JWT token in Authorization header.",
    response_description="Paginated user list with total count",
)
async def list_users(
    _admin_id: Annotated[str, Depends(require_admin)],
    offset: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Max records to return (1-100)"),
    search: str | None = Query(None, description="Filter by email (case-insensitive partial match)"),
):
    client = get_service_client()
    query = client.table("users").select("*", count="exact")

    if search:
        query = query.ilike("email", f"%{search}%")

    resp = query.range(offset, offset + limit - 1).order("created_at", desc=True).execute()
    total = resp.count or 0

    users = [_profile_to_response(u) for u in (resp.data or [])]
    return AdminUserListResponse(users=users, total=total)


@router.get(
    "/admin/users/{user_id}",
    response_model=AdminUserResponse,
    summary="Get user by ID (admin)",
    description="Retrieve a single user's profile by their UUID. Requires admin JWT.",
    response_description="User profile data",
)
async def get_user(
    user_id: str,
    _admin_id: Annotated[str, Depends(require_admin)],
):
    """Get a single user by their UUID."""
    client = get_service_client()
    resp = client.table("users").select("*").eq("id", user_id).maybe_single().execute()
    if not resp.data:
        raise HTTPException(404, "User not found")
    return _profile_to_response(resp.data)


@router.patch(
    "/admin/users/{user_id}",
    response_model=AdminUserResponse,
    summary="Update user (admin)",
    description="Update a user's profile fields: full_name, subscription_tier (free/premium/enterprise), or is_admin. Requires admin JWT.",
    response_description="Updated user profile",
)
async def update_user(
    user_id: str,
    update: AdminUserUpdate,
    _admin_id: Annotated[str, Depends(require_admin)],
):
    """Update user profile fields (full_name, subscription_tier, is_admin)."""
    client = get_service_client()
    payload = update.model_dump(exclude_none=True)
    if not payload:
        raise HTTPException(400, "No fields to update")

    resp = client.table("users").update(payload).eq("id", user_id).execute()
    if not resp.data:
        raise HTTPException(404, "User not found")
    return _profile_to_response(resp.data[0])


@router.delete(
    "/admin/users/{user_id}",
    summary="Deactivate user (admin)",
    description="Soft-delete a user by clearing their profile data (name → '[deleted]') and banning their auth account for 100 years. Requires admin JWT.",
    response_description="Confirmation of user deactivation",
)
async def delete_user(
    user_id: str,
    _admin_id: Annotated[str, Depends(require_admin)],
):
    """Soft-delete a user: clear profile, ban auth account."""
    client = get_service_client()
    profile = client.table("users").select("id").eq("id", user_id).maybe_single().execute()
    if not profile.data:
        raise HTTPException(404, "User not found")

    client.table("users").update({
        "full_name": "[deleted]",
        "subscription_tier": "free",
        "is_admin": False,
    }).eq("id", user_id).execute()

    client.auth.admin.update_user_by_id(user_id, {"ban_duration": "876000h"})
    return {"detail": "User deactivated"}


@router.post(
    "/admin/users/{user_id}/reset-password",
    summary="Reset user password to default (admin)",
    description="Force-reset a user's password to the configured default and clear any pending forgot-password request. Requires admin JWT.",
    response_description="Confirmation of password reset",
)
async def reset_user_password(
    user_id: str,
    _admin_id: Annotated[str, Depends(require_admin)],
):
    """Force a user's password back to the default. Admin only."""
    client = get_service_client()
    profile = client.table("users").select("id, email").eq("id", user_id).maybe_single().execute()
    if not profile.data:
        raise HTTPException(404, "User not found")

    client.auth.admin.update_user_by_id(user_id, {"password": settings.default_password})
    record_reset_completed(profile.data.get("email", ""))
    return {"detail": "Password reset to default"}


def _profile_to_response(row: dict) -> AdminUserResponse:
    return AdminUserResponse(
        id=row["id"],
        email=row.get("email", ""),
        full_name=row.get("full_name", ""),
        subscription_tier=row.get("subscription_tier", "free"),
        is_admin=row.get("is_admin", False),
        created_at=str(row.get("created_at", "")),
    )
