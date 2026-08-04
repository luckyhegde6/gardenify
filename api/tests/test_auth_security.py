import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import pytest
from api.config import settings
from api.services import auth_security
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


@pytest.fixture(autouse=True)
def clean_state():
    with auth_security._lock:
        auth_security._login_state.clear()
        auth_security._reset_pending.clear()
    yield


def test_allows_login_up_to_max_attempts():
    email = "a@b.com"
    n = settings.login_max_attempts
    for _ in range(n - 1):
        assert record_login_failure(email) > 0  # still has tries left
        check_login_allowed(email)  # not locked yet
    assert record_login_failure(email) == 0  # now locked
    with pytest.raises(LockedOutError):
        check_login_allowed(email)


def test_success_clears_failures():
    email = "a@b.com"
    record_login_failure(email)
    record_login_failure(email)
    record_login_success(email)
    check_login_allowed(email)  # no lockout after a successful login


def test_reset_once_then_allowed_after_completion():
    email = "a@b.com"
    record_reset_sent(email)
    with pytest.raises(ResetPendingError):
        check_reset_allowed(email)
    record_reset_completed(email)
    check_reset_allowed(email)  # reset reopened after completion


def test_reset_pending_expires_after_ttl():
    email = "a@b.com"
    record_reset_sent(email)
    # Force expiry so retry is permitted after the window passes.
    auth_security._reset_pending[email] = (
        auth_security._now() - settings.reset_pending_ttl_seconds - 1
    )
    check_reset_allowed(email)