"""
authentication.py
-------------------
Complete authentication system for the Diabetes Risk Predictor.

Implements:
    - Registration (with input validation)
    - Login (bcrypt password verification)
    - Logout
    - Password Hashing (bcrypt)
    - Session Management (via Streamlit's session_state)
    - Role-Based Access Control (RBAC)

Security notes:
    - Passwords are NEVER stored in plain text; bcrypt hashing with salt.
    - All DB access goes through db_manager's parameterized queries (no SQL injection).
    - Basic input validation guards against malformed/garbage input.
"""

import os
import sys
import re
import bcrypt

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import ALL_ROLES
from database import db_manager as db


# ---------------------------------------------------------------------------
# PASSWORD HASHING
# ---------------------------------------------------------------------------
def hash_password(plain_password: str) -> str:
    """Hashes a plaintext password using bcrypt with an auto-generated salt."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(plain_password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, password_hash: str) -> bool:
    """Verifies a plaintext password against a stored bcrypt hash."""
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), password_hash.encode("utf-8"))
    except (ValueError, TypeError):
        return False


# ---------------------------------------------------------------------------
# INPUT VALIDATION
# ---------------------------------------------------------------------------
EMAIL_REGEX = re.compile(r"^[\w\.\+\-]+@[\w\-]+\.[a-zA-Z]{2,}$")
USERNAME_REGEX = re.compile(r"^[A-Za-z0-9_]{4,20}$")


def validate_registration_input(full_name, username, email, password, confirm_password, role) -> list:
    """Returns a list of human-readable validation errors (empty list = valid)."""
    errors = []

    if not full_name or len(full_name.strip()) < 3:
        errors.append("Full name must be at least 2 characters.")

    if not USERNAME_REGEX.match(username or ""):
        errors.append("Username must be 4-20 characters, letters/numbers/underscore only.")

    if not EMAIL_REGEX.match(email or ""):
        errors.append("Please enter a valid email address.")

    if not password or len(password) < 8:
        errors.append("Password must be at least 8 characters long.")
    elif not re.search(r"[A-Z]", password):
        errors.append("Password must contain at least one uppercase letter.")
    elif not re.search(r"[0-9]", password):
        errors.append("Password must contain at least one digit.")

    if password != confirm_password:
        errors.append("Passwords do not match.")

    if role not in ALL_ROLES:
        errors.append("Invalid role selected.")

    return errors


# ---------------------------------------------------------------------------
# REGISTRATION
# ---------------------------------------------------------------------------
def register_user(full_name, username, email, password, confirm_password, role):
    """
    Validates and creates a new user. Returns (success: bool, message: str).
    """
    errors = validate_registration_input(full_name, username, email, password, confirm_password, role)
    if errors:
        return False, " ".join(errors)

    if db.get_user_by_username(username):
        return False, "Username already taken. Please choose another."

    try:
        password_hash = hash_password(password)
        db.create_user(full_name.strip(), username.strip(), email.strip().lower(), password_hash, role)
        return True, "Registration successful! You can now log in."
    except Exception as e:
        # Catches UNIQUE constraint violations (e.g. duplicate email) and other DB errors
        if "UNIQUE constraint" in str(e):
            return False, "An account with this username or email already exists."
        return False, f"Registration failed: {e}"


# ---------------------------------------------------------------------------
# LOGIN / LOGOUT
# ---------------------------------------------------------------------------
def login_user(username: str, password: str):
    """
    Verifies credentials. Returns (success: bool, user_dict_or_message).
    On success, the second element is the user dict (without password_hash).
    """
    user = db.get_user_by_username((username or "").strip())

    if not user:
        return False, "Invalid username or password."

    if not user.get("is_active", 1):
        return False, "This account has been deactivated. Please contact an administrator."

    if not verify_password(password, user["password_hash"]):
        return False, "Invalid username or password."

    db.update_last_login(user["user_id"])
    safe_user = {k: v for k, v in user.items() if k != "password_hash"}
    return True, safe_user


def login_session(st_session_state, user: dict):
    """Populates Streamlit session_state with the authenticated user's info."""
    st_session_state["authenticated"] = True
    st_session_state["user_id"] = user["user_id"]
    st_session_state["username"] = user["username"]
    st_session_state["full_name"] = user["full_name"]
    st_session_state["role"] = user["role"]
    st_session_state["email"] = user["email"]


def logout_session(st_session_state):
    """Clears all authentication-related keys from Streamlit session_state."""
    keys_to_clear = ["authenticated", "user_id", "username", "full_name", "role", "email"]
    for key in keys_to_clear:
        if key in st_session_state:
            del st_session_state[key]


def is_authenticated(st_session_state) -> bool:
    return bool(st_session_state.get("authenticated", False))


# ---------------------------------------------------------------------------
# ROLE-BASED ACCESS CONTROL (RBAC)
# ---------------------------------------------------------------------------
def has_role(st_session_state, *allowed_roles) -> bool:
    """Checks whether the current session's user role is in allowed_roles."""
    if not is_authenticated(st_session_state):
        return False
    return st_session_state.get("role") in allowed_roles


def require_login(st_session_state, st_module):
    """
    Call at the top of any protected page. Stops page rendering (via st.stop())
    if the user is not authenticated.
    """
    if not is_authenticated(st_session_state):
        st_module.warning("🔒 Please log in to access this page.")
        st_module.stop()


def require_role(st_session_state, st_module, *allowed_roles):
    """
    Call at the top of role-restricted pages (e.g. Admin Panel).
    Stops rendering if the user's role isn't in allowed_roles.
    """
    require_login(st_session_state, st_module)
    if not has_role(st_session_state, *allowed_roles):
        st_module.error(f"⛔ Access denied. This page requires one of the following roles: {', '.join(allowed_roles)}.")
        st_module.stop()
