"""
db_manager.py - Firebase Firestore backend
Supports Streamlit Cloud Secrets + Local JSON file
"""

import os
import sys
from datetime import datetime

import firebase_admin
from firebase_admin import credentials, firestore

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import FIREBASE_CREDENTIALS_PATH

_db = None


def _get_db():
    global _db
    if _db is not None:
        return _db

    if not firebase_admin._apps:
        cred = None

        # Mode 1: Streamlit Cloud Secrets
        try:
            import streamlit as st
            if "firebase" in st.secrets:
                firebase_dict = dict(st.secrets["firebase"])
                if "private_key" in firebase_dict:
                    firebase_dict["private_key"] = firebase_dict["private_key"].replace("\\n", "\n")
                cred = credentials.Certificate(firebase_dict)
        except Exception:
            cred = None

        # Mode 2: Local JSON file
        if cred is None:
            if not os.path.exists(FIREBASE_CREDENTIALS_PATH):
                raise FileNotFoundError(
                    f"Firebase credentials not found.\n\n"
                    f"LOCAL: place service account JSON at:\n"
                    f"  {FIREBASE_CREDENTIALS_PATH}\n\n"
                    f"STREAMLIT CLOUD: add in App Settings -> Secrets:\n"
                    f"  [firebase]\n"
                    f"  type = 'service_account'\n"
                    f"  project_id = 'your-project-id'\n"
                    f"  private_key = '-----BEGIN RSA PRIVATE KEY-----\\n...'\n"
                    f"  client_email = 'firebase-adminsdk@your-project.iam.gserviceaccount.com'\n"
                    f"  ... (remaining fields from your downloaded JSON)"
                )
            cred = credentials.Certificate(FIREBASE_CREDENTIALS_PATH)

        firebase_admin.initialize_app(cred)

    _db = firestore.client()
    return _db


def initialize_database():
    _get_db()


# USERS
def create_user(full_name, username, email, password_hash, role):
    db = _get_db()
    doc_ref = db.collection("users").document()
    doc_ref.set({"full_name": full_name, "username": username, "email": email,
                 "password_hash": password_hash, "role": role,
                 "created_at": datetime.now().isoformat(), "last_login": None, "is_active": 1})
    return doc_ref.id

def get_user_by_username(username):
    db = _get_db()
    for doc in db.collection("users").where("username", "==", username).limit(1).stream():
        data = doc.to_dict(); data["user_id"] = doc.id; return data
    return None

def get_user_by_id(user_id):
    db = _get_db()
    doc = db.collection("users").document(str(user_id)).get()
    if doc.exists:
        data = doc.to_dict(); data["user_id"] = doc.id; return data
    return None

def update_last_login(user_id):
    _get_db().collection("users").document(str(user_id)).update({"last_login": datetime.now().isoformat()})

def get_all_users():
    db = _get_db()
    users = []
    for doc in db.collection("users").stream():
        data = doc.to_dict(); data["user_id"] = doc.id; data.pop("password_hash", None); users.append(data)
    return users

def set_user_active_status(user_id, is_active: bool):
    _get_db().collection("users").document(str(user_id)).update({"is_active": int(is_active)})

def delete_user(user_id):
    _get_db().collection("users").document(str(user_id)).delete()


# HEALTH RECORDS
def add_health_record(user_id, data: dict):
    db = _get_db()
    doc_ref = db.collection("health_records").document()
    doc_ref.set({"user_id": str(user_id), "age": data.get("age"), "gender": data.get("gender"),
                 "bmi": data.get("bmi"), "hypertension": data.get("hypertension"),
                 "heart_disease": data.get("heart_disease"), "smoking_history": data.get("smoking_history"),
                 "blood_glucose_level": data.get("blood_glucose_level"), "hba1c_level": data.get("HbA1c_level"),
                 "recorded_at": datetime.now().isoformat()})
    return doc_ref.id

def get_health_records_for_user(user_id):
    db = _get_db()
    records = []
    for doc in db.collection("health_records").where("user_id", "==", str(user_id)).stream():
        data = doc.to_dict(); data["record_id"] = doc.id; records.append(data)
    return sorted(records, key=lambda r: r.get("recorded_at", ""), reverse=True)


# MODELS
def save_model_metadata(model_name, file_path, metrics: dict, is_best=False):
    db = _get_db()
    if is_best:
        for doc in db.collection("models").where("is_best_model", "==", 1).stream():
            db.collection("models").document(doc.id).update({"is_best_model": 0})
    doc_ref = db.collection("models").document()
    doc_ref.set({"model_name": model_name, "file_path": file_path, "accuracy": metrics.get("accuracy"),
                 "precision_score": metrics.get("precision"), "recall_score": metrics.get("recall"),
                 "f1_score": metrics.get("f1"), "roc_auc": metrics.get("roc_auc"),
                 "is_best_model": int(is_best), "trained_at": datetime.now().isoformat()})
    return doc_ref.id

def get_best_model():
    db = _get_db()
    best = None
    for doc in db.collection("models").where("is_best_model", "==", 1).stream():
        data = doc.to_dict(); data["model_id"] = doc.id
        if best is None or data["trained_at"] > best["trained_at"]: best = data
    return best

def get_all_models():
    db = _get_db()
    models = []
    for doc in db.collection("models").stream():
        data = doc.to_dict(); data["model_id"] = doc.id; models.append(data)
    return sorted(models, key=lambda m: m.get("trained_at", ""), reverse=True)


# PREDICTIONS
def add_prediction(user_id, record_id, model_id, prediction_result, probability, confidence_score, risk_category):
    db = _get_db()
    doc_ref = db.collection("predictions").document()
    doc_ref.set({"user_id": str(user_id), "record_id": str(record_id) if record_id else None,
                 "model_id": str(model_id) if model_id else None, "prediction_result": int(prediction_result),
                 "probability": float(probability), "confidence_score": float(confidence_score),
                 "risk_category": risk_category, "predicted_at": datetime.now().isoformat()})
    return doc_ref.id

def get_predictions_for_user(user_id):
    db = _get_db()
    preds = []
    for doc in db.collection("predictions").where("user_id", "==", str(user_id)).stream():
        data = doc.to_dict(); data["prediction_id"] = doc.id; preds.append(data)
    return sorted(preds, key=lambda p: p.get("predicted_at", ""), reverse=True)

def get_all_predictions():
    db = _get_db()
    preds = []
    for doc in db.collection("predictions").stream():
        data = doc.to_dict(); data["prediction_id"] = doc.id; preds.append(data)
    return sorted(preds, key=lambda p: p.get("predicted_at", ""), reverse=True)


# FEEDBACK
def add_feedback(user_id, feedback_type, message, rating=None):
    db = _get_db()
    doc_ref = db.collection("feedback").document()
    doc_ref.set({"user_id": str(user_id), "feedback_type": feedback_type,
                 "message": message, "rating": rating, "submitted_at": datetime.now().isoformat()})
    return doc_ref.id

def get_all_feedback():
    db = _get_db()
    feedback_list = []
    for doc in db.collection("feedback").stream():
        data = doc.to_dict(); data["feedback_id"] = doc.id
        user = get_user_by_id(data["user_id"])
        data["full_name"] = user["full_name"] if user else "Unknown"
        data["role"] = user["role"] if user else "Unknown"
        feedback_list.append(data)
    return sorted(feedback_list, key=lambda f: f.get("submitted_at", ""), reverse=True)


# REPORTS
def add_report(user_id, prediction_id, report_type, file_path):
    db = _get_db()
    doc_ref = db.collection("reports").document()
    doc_ref.set({"user_id": str(user_id), "prediction_id": str(prediction_id) if prediction_id else None,
                 "report_type": report_type, "file_path": file_path, "generated_at": datetime.now().isoformat()})
    return doc_ref.id

def get_reports_for_user(user_id):
    db = _get_db()
    reports = []
    for doc in db.collection("reports").where("user_id", "==", str(user_id)).stream():
        data = doc.to_dict(); data["report_id"] = doc.id; reports.append(data)
    return sorted(reports, key=lambda r: r.get("generated_at", ""), reverse=True)

def get_all_reports():
    db = _get_db()
    reports = []
    for doc in db.collection("reports").stream():
        data = doc.to_dict(); data["report_id"] = doc.id
        user = get_user_by_id(data["user_id"])
        data["full_name"] = user["full_name"] if user else "Unknown"
        reports.append(data)
    return sorted(reports, key=lambda r: r.get("generated_at", ""), reverse=True)