"""
pages/feedback.py
--------------------
PAGE 12 - FEEDBACK SYSTEM

Allows: User Feedback, Doctor Feedback, Suggestions. Stores feedback in DB.
"""

import streamlit as st
import pandas as pd

from database.db_manager import add_feedback, get_all_feedback
from config import ROLE_ADMIN, ROLE_PROVIDER, ROLE_PATIENT


FEEDBACK_TYPE_BY_ROLE = {
    ROLE_PATIENT: "User Feedback",
    ROLE_PROVIDER: "Doctor Feedback",
    ROLE_ADMIN: "Suggestion",
}


def render():
    st.title("💬 Feedback System")
    st.caption("Share your experience or suggestions to help us improve this system.")

    role = st.session_state["role"]
    default_type = FEEDBACK_TYPE_BY_ROLE.get(role, "User Feedback")

    with st.form("feedback_form"):
        feedback_type = st.selectbox(
            "Feedback Type",
            ["User Feedback", "Doctor Feedback", "Suggestion"],
            index=["User Feedback", "Doctor Feedback", "Suggestion"].index(default_type),
        )
        rating = st.slider("Overall Rating", 1, 5, 4)
        message = st.text_area("Your Feedback / Suggestion", height=120,
                                placeholder="Tell us what worked well, what didn't, or what you'd like to see improved...")
        submitted = st.form_submit_button("Submit Feedback", type="primary", use_container_width=True)

        if submitted:
            if not message.strip():
                st.error("Please enter a message before submitting.")
            else:
                add_feedback(st.session_state["user_id"], feedback_type, message.strip(), rating)
                st.success("✅ Thank you! Your feedback has been recorded.")

    st.divider()

    # Patients/providers see their own submission history is implicit via DB;
    # Admins/Providers get visibility into all feedback for monitoring purposes.
    if role in (ROLE_ADMIN, ROLE_PROVIDER):
        st.subheader("📋 All Submitted Feedback")
        all_feedback = get_all_feedback()
        if not all_feedback:
            st.caption("No feedback submitted yet.")
        else:
            fb_df = pd.DataFrame(all_feedback)[
                ["submitted_at", "full_name", "role", "feedback_type", "rating", "message"]
            ]
            fb_df.columns = ["Date", "Name", "Role", "Type", "Rating", "Message"]
            st.dataframe(fb_df, use_container_width=True, hide_index=True)

            avg_rating = fb_df["Rating"].dropna().mean()
            if not pd.isna(avg_rating):
                st.metric("Average Rating", f"{avg_rating:.1f} / 5")
