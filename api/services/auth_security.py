"""In-memory login rate-limiting and one-shot password-reset guards.

Holds nothing sensitive — only failure counts and pending-flag expiries, keyed
by email. Thread-safe via a single lock; state is per-process, so on serverless
(Vercel) it is approximate across cold instances.
# ponytail: in-memory dict is a per-instance guard; if abuse-at-scale becomes a
# problem, move the state to Redis/managed store. Fine for the current quota.
"""

import logging
import threading
import time

from api.config import settings

logger = logging.getLogger(__name__)

_lock = threading.Lock()
# email -> {"fails": int, "locked_until": float, "last_fail": float}
_login_state: dict[str, dict] = {}
# email -> expires_at (epoch seconds) while a reset is pending
_reset_pending: dict[str, float] = {}


class LockedOutError(Exception):
    """Too many failed login attempts; caller should return HTTP 429."""


class ResetPendingError(Exception):
    """A reset is already pending for this email; caller should return HTTP 429."""


def _now() -> float:
    return time.monotonic()


def _prune() -> None:
    """Drop entries that are no longer relevant: expired locks or idle counters."""
    now = _now()
    for email, state in list(_login_state.items()):
        active_lock = state.get("locked_until", 0) > now
        idle = now - state.get("last_fail", now) > settings.login_lockout_seconds
        if not active_lock and idle:
            del _login_state[email]


def check_login_allowed(email: str) -> None:
    """Raise LockedOutError if the account is currently locked out."""
    with _lock:
        _prune()
        state = _login_state.get(email)
        if state and _now() < state.get("locked_until", 0):
            raise LockedOutError()


def record_login_failure(email: str) -> int:
    """Register one failed attempt, auto-locking after `login_max_attempts`.

    Returns the number of attempts remaining before lockout (0 == locked now).
    """
    with _lock:
        _prune()
        state = _login_state.setdefault(
            email, {"fails": 0, "locked_until": 0.0, "last_fail": _now()}
        )
        # An idle, non-locked counter eventually resets instead of accumulating forever.
        if state["locked_until"] == 0 and _now() - state["last_fail"] > settings.login_lockout_seconds:
            state["fails"] = 0
        state["fails"] += 1
        state["last_fail"] = _now()
        remaining = max(settings.login_max_attempts - state["fails"], 0)
        if remaining == 0:
            state["locked_until"] = _now() + settings.login_lockout_seconds
        return remaining


def record_login_success(email: str) -> None:
    """Clear any accumulated failures/lockout on a successful login."""
    with _lock:
        _login_state.pop(email, None)


def check_reset_allowed(email: str) -> None:
    """Raise ResetPendingError if a reset is already pending or in cooldown."""
    with _lock:
        expires = _reset_pending.get(email)
        if expires is not None and _now() < expires:
            raise ResetPendingError


def record_reset_sent(email: str) -> None:
    """Mark an in-flight reset so the same email can't spam another until done."""
    with _lock:
        _reset_pending[email] = _now() + settings.reset_pending_ttl_seconds


def record_reset_completed(email: str) -> None:
    """Clear the pending reset after the user picks a new password."""
    with _lock:
        _reset_pending.pop(email, None)