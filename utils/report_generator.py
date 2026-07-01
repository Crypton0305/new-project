"""
report_generator.py
---------------------
Generates downloadable PDF and CSV reports summarizing a patient's
diabetes risk assessment: user info, prediction results, risk analysis,
model metrics, and recommendations.
"""

import os
import sys
import csv
import io
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import REPORTS_DIR, APP_NAME


def generate_pdf_report(user: dict, patient_input: dict, prediction_result: dict,
                         model_metrics: dict = None, recommendations: dict = None) -> str:
    """
    Builds a professional PDF report and saves it to REPORTS_DIR.
    Returns the absolute file path of the generated PDF.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"diabetes_report_{user.get('username', 'patient')}_{timestamp}.pdf"
    file_path = os.path.join(REPORTS_DIR, filename)

    doc = SimpleDocTemplate(file_path, pagesize=A4, topMargin=2 * cm, bottomMargin=2 * cm)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("TitleStyle", parent=styles["Title"], textColor=colors.HexColor("#0E7C7B"))
    heading_style = ParagraphStyle("HeadingStyle", parent=styles["Heading2"], textColor=colors.HexColor("#17A398"))
    normal = styles["Normal"]

    elements = []

    # --- Header ---
    elements.append(Paragraph(APP_NAME, title_style))
    elements.append(Paragraph("Diabetes Risk Assessment Report", styles["Heading3"]))
    elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", normal))
    elements.append(Spacer(1, 0.5 * cm))
    elements.append(HRFlowable(width="100%", color=colors.HexColor("#0E7C7B")))
    elements.append(Spacer(1, 0.5 * cm))

    # --- User Information ---
    elements.append(Paragraph("Patient Information", heading_style))
    user_table_data = [
        ["Full Name", user.get("full_name", "-")],
        ["Username", user.get("username", "-")],
        ["Email", user.get("email", "-")],
        ["Role", user.get("role", "-")],
    ]
    user_table = Table(user_table_data, colWidths=[5 * cm, 10 * cm])
    user_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#E8F6F6")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    elements.append(user_table)
    elements.append(Spacer(1, 0.5 * cm))

    # --- Input Data ---
    elements.append(Paragraph("Health & Lifestyle Inputs", heading_style))
    input_rows = [["Field", "Value"]]
    field_labels = {
        "age": "Age", "gender": "Gender", "bmi": "BMI", "hypertension": "Hypertension",
        "heart_disease": "Heart Disease", "smoking_history": "Smoking History",
        "blood_glucose_level": "Blood Glucose Level", "HbA1c_level": "HbA1c Level",
    }
    for key, label in field_labels.items():
        value = patient_input.get(key, "-")
        if key in ("hypertension", "heart_disease"):
            value = "Yes" if value == 1 else "No"
        input_rows.append([label, str(value)])
    input_table = Table(input_rows, colWidths=[6 * cm, 9 * cm])
    input_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0E7C7B")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
    ]))
    elements.append(input_table)
    elements.append(Spacer(1, 0.5 * cm))

    # --- Prediction Results ---
    elements.append(Paragraph("Prediction Results", heading_style))
    result_label = "Diabetic (High Likelihood)" if prediction_result["prediction_result"] == 1 else "Non-Diabetic"
    pred_rows = [
        ["Model Used", prediction_result.get("model_used", "-")],
        ["Prediction", result_label],
        ["Probability", f"{prediction_result['probability'] * 100:.1f}%"],
        ["Confidence Score", f"{prediction_result['confidence_score'] * 100:.1f}%"],
        ["Risk Category", prediction_result["risk_category"]],
    ]
    pred_table = Table(pred_rows, colWidths=[6 * cm, 9 * cm])
    risk_color = colors.HexColor("#E63946") if prediction_result["risk_category"] == "High Risk" else (
        colors.HexColor("#F4A261") if prediction_result["risk_category"] == "Moderate Risk" else colors.HexColor("#2A9D8F")
    )
    pred_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#E8F6F6")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("BACKGROUND", (1, 4), (1, 4), risk_color),
    ]))
    elements.append(pred_table)
    elements.append(Spacer(1, 0.5 * cm))

    # --- Model Metrics ---
    if model_metrics:
        elements.append(Paragraph("Model Performance Metrics", heading_style))
        metric_rows = [["Metric", "Value"]]
        for k, v in model_metrics.items():
            if k != "confusion_matrix":
                metric_rows.append([k.replace("_", " ").title(), str(v)])
        metric_table = Table(metric_rows, colWidths=[6 * cm, 9 * cm])
        metric_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#17A398")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
        ]))
        elements.append(metric_table)
        elements.append(Spacer(1, 0.5 * cm))

    # --- Recommendations ---
    if recommendations:
        elements.append(Paragraph("Personalized Recommendations", heading_style))
        for category, items in recommendations.items():
            elements.append(Paragraph(f"<b>{category}</b>", normal))
            for item in items:
                elements.append(Paragraph(f"&bull; {item}", normal))
            elements.append(Spacer(1, 0.2 * cm))

    # --- Disclaimer ---
    elements.append(Spacer(1, 0.5 * cm))
    elements.append(HRFlowable(width="100%", color=colors.grey))
    disclaimer_style = ParagraphStyle("Disclaimer", parent=normal, fontSize=8, textColor=colors.grey)
    elements.append(Paragraph(
        "Disclaimer: This report is generated by an AI-based screening tool for educational and "
        "decision-support purposes only. It does not constitute a medical diagnosis. Please consult "
        "a qualified healthcare professional for clinical decisions.",
        disclaimer_style,
    ))

    doc.build(elements)
    return file_path


def generate_csv_report(user: dict, patient_input: dict, prediction_result: dict) -> str:
    """Builds a CSV report and saves it to REPORTS_DIR. Returns the file path."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"diabetes_report_{user.get('username', 'patient')}_{timestamp}.csv"
    file_path = os.path.join(REPORTS_DIR, filename)

    rows = [
        ["Field", "Value"],
        ["Full Name", user.get("full_name", "-")],
        ["Username", user.get("username", "-")],
        ["Email", user.get("email", "-")],
        ["Generated At", datetime.now().isoformat()],
    ]
    for key, value in patient_input.items():
        rows.append([key, value])

    rows.append(["Model Used", prediction_result.get("model_used", "-")])
    rows.append(["Prediction Result", "Diabetic" if prediction_result["prediction_result"] == 1 else "Non-Diabetic"])
    rows.append(["Probability", prediction_result["probability"]])
    rows.append(["Confidence Score", prediction_result["confidence_score"]])
    rows.append(["Risk Category", prediction_result["risk_category"]])

    with open(file_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(rows)

    return file_path
