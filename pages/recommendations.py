"""
pages/recommendations.py
---------------------------
PAGE 6 - PERSONALIZED RECOMMENDATIONS

Generates recommendations based on the user's last prediction:
Diet, Exercise, Weight Management, Lifestyle Improvement, Sleep Improvement,
Medical Consultation Advice, Prevention Strategies.
"""

import streamlit as st
from config import RISK_LABELS


def _get_recommendations(risk_category: str, patient_input: dict) -> dict:
    """Returns a dict of recommendation categories tailored to risk level and inputs."""
    high = risk_category == RISK_LABELS["high"]
    moderate = risk_category == RISK_LABELS["moderate"]

    bmi = patient_input.get("bmi", 25) if patient_input else 25
    smoking = patient_input.get("smoking_history", "never") if patient_input else "never"

    diet = [
        "Reduce intake of refined sugars and sugary beverages.",
        "Favor whole grains over refined carbohydrates (e.g. brown rice, oats).",
        "Increase fiber intake through vegetables, legumes, and fruits.",
        "Limit saturated fats; prefer healthy fats (olive oil, nuts, fish).",
    ]
    if high:
        diet.insert(0, "Adopt a low-glycemic-index diet and consider consulting a registered dietitian.")

    exercise = [
        "Aim for at least 150 minutes of moderate aerobic activity per week (e.g. brisk walking).",
        "Include resistance/strength training 2-3 times per week to improve insulin sensitivity.",
        "Break up long periods of sitting with short walks every hour.",
    ]
    if high:
        exercise.insert(0, "Start with low-impact activity and gradually increase intensity under medical supervision.")

    weight = []
    if bmi >= 30:
        weight.append("Your BMI falls in the obese range — even a 5-7% weight loss can meaningfully reduce diabetes risk.")
    elif bmi >= 25:
        weight.append("Your BMI falls in the overweight range — gradual weight loss through diet and exercise is recommended.")
    else:
        weight.append("Your BMI is within a healthy range — focus on maintaining it through consistent habits.")

    lifestyle = [
        "Limit alcohol consumption to moderate levels.",
        "Manage stress through mindfulness, relaxation techniques, or hobbies.",
        "Stay well-hydrated and avoid prolonged fasting/binge eating cycles.",
    ]
    if smoking in ("current", "former", "ever"):
        lifestyle.insert(0, "Consider a smoking cessation program — smoking significantly worsens insulin resistance.")

    sleep = [
        "Aim for 7-9 hours of quality sleep per night.",
        "Maintain a consistent sleep schedule, even on weekends.",
        "Avoid screens and caffeine close to bedtime.",
    ]

    medical = [
        "Schedule a follow-up consultation with a healthcare provider to discuss this result.",
        "Consider routine blood glucose and HbA1c monitoring.",
    ]
    if high:
        medical.insert(0, "⚠️ Given the High Risk result, prompt clinical evaluation is strongly advised.")
    elif moderate:
        medical.insert(0, "A check-up within the next few months is advisable to monitor your risk trend.")

    prevention = [
        "Maintain a balanced diet and regular physical activity as the foundation of prevention.",
        "Get periodic health screenings, especially if you have a family history of diabetes.",
        "Track your weight, blood pressure, and blood sugar over time.",
    ]

    return {
        "🥗 Diet Recommendations": diet,
        "🏃 Exercise Suggestions": exercise,
        "⚖️ Weight Management Tips": weight,
        "🌱 Lifestyle Improvement": lifestyle,
        "😴 Sleep Improvement": sleep,
        "🏥 Medical Consultation Advice": medical,
        "🛡️ Prevention Strategies": prevention,
    }


def render():
    st.title("💡 Personalized Recommendations")
    st.caption("Actionable guidance generated from your most recent risk assessment.")

    if "last_prediction" not in st.session_state:
        st.info("Run a prediction on the **Diabetes Prediction** page first to receive personalized recommendations.")
        return

    result = st.session_state["last_prediction"]
    patient_input = st.session_state.get("last_patient_input", {})
    risk_category = result["risk_category"]

    risk_colors = {RISK_LABELS["low"]: "🟢", RISK_LABELS["moderate"]: "🟡", RISK_LABELS["high"]: "🔴"}
    st.markdown(f"### {risk_colors.get(risk_category, '')} Based on your **{risk_category}** result")

    recommendations = _get_recommendations(risk_category, patient_input)

    tabs = st.tabs(list(recommendations.keys()))
    for tab, (category, items) in zip(tabs, recommendations.items()):
        with tab:
            for item in items:
                st.markdown(f"- {item}")

    st.divider()
    st.warning(
        "⚕️ These recommendations are general, educational guidance generated from your screening "
        "result. They are not a substitute for personalized medical advice — please discuss any "
        "lifestyle or treatment changes with a qualified healthcare provider."
    )
