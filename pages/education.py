"""
pages/education.py
---------------------
PAGE 10 - USER EDUCATION CENTER

Provides educational content: What is Diabetes, Risk Factors, Prevention,
Healthy Lifestyle, Diet Guidelines, Exercise Benefits, Medical Resources.
"""

import streamlit as st


def render():
    st.title("📚 User Education Center")
    st.caption("Learn about diabetes, its risk factors, and how to manage or prevent it.")

    tabs = st.tabs([
        "What is Diabetes", "Risk Factors", "Prevention", "Healthy Lifestyle",
        "Diet Guidelines", "Exercise Benefits", "Medical Resources",
    ])

    with tabs[0]:
        st.subheader("🩺 What is Diabetes?")
        st.markdown(
            """
            **Diabetes mellitus** is a chronic metabolic condition characterized by elevated
            blood glucose (sugar) levels, resulting from the body's inability to produce
            enough insulin, use insulin effectively, or both.

            **Main Types:**
            - **Type 1 Diabetes** — an autoimmune condition where the body attacks insulin-producing
              cells; usually diagnosed in children/young adults; requires insulin therapy.
            - **Type 2 Diabetes** — the most common form (~90% of cases), driven by insulin
              resistance, often linked to lifestyle and genetic factors; develops gradually.
            - **Gestational Diabetes** — develops during pregnancy and usually resolves after
              birth, but increases future Type 2 risk.

            Left unmanaged, diabetes can damage the eyes, kidneys, nerves, and cardiovascular system.
            """
        )

    with tabs[1]:
        st.subheader("⚠️ Risk Factors")
        st.markdown(
            """
            **Non-modifiable factors:**
            - Age (risk increases with age, especially after 45)
            - Family history / genetics
            - Ethnicity (certain populations have higher predisposition)

            **Modifiable factors:**
            - Excess body weight / high BMI
            - Physical inactivity
            - Unhealthy diet (high sugar, refined carbs, low fiber)
            - Smoking
            - Hypertension and abnormal cholesterol levels
            - Chronic stress and poor sleep
            """
        )

    with tabs[2]:
        st.subheader("🛡️ Prevention Strategies")
        st.markdown(
            """
            - Maintain a healthy body weight through balanced nutrition and regular activity.
            - Choose whole, minimally processed foods over sugary and refined products.
            - Engage in at least 150 minutes of moderate exercise weekly.
            - Avoid smoking and limit alcohol intake.
            - Get regular health screenings, especially if you have risk factors.
            - Manage stress and prioritize quality sleep.
            """
        )

    with tabs[3]:
        st.subheader("🌱 Healthy Lifestyle Tips")
        st.markdown(
            """
            - Build consistent daily routines around meals, activity, and sleep.
            - Stay hydrated and limit sugary beverages.
            - Practice portion control rather than restrictive dieting.
            - Find physical activities you enjoy to make exercise sustainable.
            - Build a support system — family, friends, or support groups can help sustain habits.
            """
        )

    with tabs[4]:
        st.subheader("🥗 Diet Guidelines")
        st.markdown(
            """
            - **Favor:** vegetables, whole grains, legumes, lean proteins, healthy fats (nuts, olive oil, fish).
            - **Limit:** sugary drinks, refined carbohydrates, processed/fried foods, excess saturated fat.
            - **Watch portions:** even healthy foods can affect blood sugar in large amounts.
            - **Glycemic Index awareness:** prefer low-GI foods that raise blood sugar more slowly.
            - **Meal timing:** regular, balanced meals help avoid blood sugar spikes and crashes.
            """
        )

    with tabs[5]:
        st.subheader("🏃 Exercise Benefits")
        st.markdown(
            """
            - Improves insulin sensitivity, helping cells use glucose more effectively.
            - Supports weight management and reduces visceral fat.
            - Strengthens the cardiovascular system, reducing heart disease risk.
            - Improves mood and reduces stress, which can indirectly support blood sugar control.
            - Both **aerobic exercise** (walking, cycling, swimming) and **resistance training**
              (weights, resistance bands) offer complementary benefits.
            """
        )

    with tabs[6]:
        st.subheader("📞 Medical Resources")
        st.markdown(
            """
            - **Primary Care Physician** — first point of contact for screening and referrals.
            - **Endocrinologist** — specialist in hormonal and metabolic conditions including diabetes.
            - **Registered Dietitian** — for personalized nutrition planning.
            - **Diabetes Educator** — specializes in helping patients manage day-to-day diabetes care.

            *In an emergency (e.g. signs of severe hyperglycemia or hypoglycemia), contact local
            emergency services immediately.*
            """
        )

    st.divider()
    st.warning(
        "⚕️ This content is for general educational purposes only and is not a substitute "
        "for professional medical advice, diagnosis, or treatment."
    )
