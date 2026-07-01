"""
app.py
------
Main entry point for the Intelligent Diabetes Risk Predictor.

Responsibilities:
    - Page config + global styling
    - Authentication gate (Login / Register screens)
    - Sidebar navigation (role-aware menu)
    - Routing to individual page modules
"""

import os
import sys
import streamlit as st

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import APP_NAME, APP_ICON, STYLES_PATH, ROLE_ADMIN, ROLE_PROVIDER, ROLE_PATIENT
from database.db_manager import initialize_database
from utils.authentication import (
    register_user, login_user, login_session, logout_session, is_authenticated,
)

# ---------------------------------------------------------------------------
# PAGE CONFIG (must be the first Streamlit call)
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title=APP_NAME,
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# GLOBAL STYLES
# ---------------------------------------------------------------------------
def load_css():
    if os.path.exists(STYLES_PATH):
        with open(STYLES_PATH) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# ---------------------------------------------------------------------------
# DB INIT (idempotent - safe to call on every rerun)
# ---------------------------------------------------------------------------
initialize_database()

# ---------------------------------------------------------------------------
# PAGE REGISTRY
# Maps sidebar labels -> (module_path, allowed_roles or None for "all")
# ---------------------------------------------------------------------------
PAGE_REGISTRY = {
    "🏠 Home Dashboard": ("pages.home", None),
    "📊 Data Analysis": ("pages.data_analysis", None),
    "🤖 Model Training": ("pages.model_training", [ROLE_ADMIN, ROLE_PROVIDER]),
    "🩺 Diabetes Prediction": ("pages.prediction", None),
    "🔍 Risk Factor Analysis": ("pages.risk_analysis", None),
    "💡 Recommendations": ("pages.recommendations", None),
    "📈 Longitudinal Tracking": ("pages.tracking", None),
    "📉 Visualization Dashboard": ("pages.dashboard", None),
    "📄 Report Generation": ("pages.reports", None),
    "📚 Education Center": ("pages.education", None),
    "🏥 Clinical Decision Support": ("pages.clinical_support", [ROLE_ADMIN, ROLE_PROVIDER]),
    "💬 Feedback": ("pages.feedback", None),
    "⚙️ Admin Panel": ("pages.admin", [ROLE_ADMIN]),
}


# ---------------------------------------------------------------------------
# AUTH SCREENS
# ---------------------------------------------------------------------------
def render_login_form():
    st.subheader("🔐 Login")
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login", use_container_width=True)

        if submitted:
            success, result = login_user(username, password)
            if success:
                login_session(st.session_state, result)
                st.success(f"Welcome back, {result['full_name']}!")
                st.rerun()
            else:
                st.error(result)


def render_register_form():
    st.subheader("📝 Create an Account")
    with st.form("register_form"):
        full_name = st.text_input("Full Name")
        username = st.text_input("Username (4-20 chars, letters/numbers/underscore)")
        email = st.text_input("Email")
        role = st.selectbox("Role", [ROLE_PATIENT, ROLE_PROVIDER, ROLE_ADMIN])
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        submitted = st.form_submit_button("Register", use_container_width=True)

        if submitted:
            success, message = register_user(full_name, username, email, password, confirm_password, role)
            if success:
                st.success(message)
            else:
                st.error(message)


def render_auth_gate():
    st.markdown(
        f"""
        <div style="text-align:center; padding: 1.5rem 0;">
            <h1>{APP_ICON} {APP_NAME}</h1>
            <p style="font-size:1.1rem; color:#555;">
                AI-powered clinical decision support for early diabetes risk detection
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        tab_login, tab_register = st.tabs(["Login", "Register"])
        with tab_login:
            render_login_form()
        with tab_register:
            render_register_form()


# ---------------------------------------------------------------------------
# SIDEBAR / NAVIGATION
# ---------------------------------------------------------------------------
def get_visible_pages(role: str):
    visible = {}
    for label, (module_path, allowed_roles) in PAGE_REGISTRY.items():
        if allowed_roles is None or role in allowed_roles:
            visible[label] = module_path
    return visible


def render_sidebar():
    with st.sidebar:
        st.markdown(f"## {APP_ICON} {APP_NAME}")
        st.markdown(f"**{st.session_state['full_name']}**")
        st.caption(f"Role: {st.session_state['role']}")
        st.divider()

        visible_pages = get_visible_pages(st.session_state["role"])
        selection = st.radio("Navigate", list(visible_pages.keys()), label_visibility="collapsed")

        st.divider()
        if st.button("🚪 Logout", use_container_width=True):
            logout_session(st.session_state)
            st.rerun()

        return visible_pages[selection]


# ---------------------------------------------------------------------------
# MAIN ROUTER
# ---------------------------------------------------------------------------
def main():
    if not is_authenticated(st.session_state):
        render_auth_gate()
        return

    module_path = render_sidebar()

    # Dynamic import + render of the selected page module.
    import importlib
    try:
        page_module = importlib.import_module(module_path)
        importlib.reload(page_module)  # picks up edits during dev without full restart
        page_module.render()
    except ModuleNotFoundError:
        st.info("🚧 This page is under construction and will be available soon.")
    except Exception as e:
        st.error(f"An error occurred while loading this page: {e}")


if __name__ == "__main__":
    main()
