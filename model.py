"""
model.py — Stage-1 XGBoost pipeline (exact notebook replica)
Cached with @st.cache_resource — trains once on startup (~10 sec)
"""
import numpy as np
import pandas as pd
import streamlit as st
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from xgboost import XGBClassifier

STAGE1_COLS = [
    "Gender", "Age", "Customer Type", "Type of Travel", "Class",
    "Flight Distance", "Ease of Online Booking", "Check-in Service",
    "Online Boarding", "Gate Location", "Satisfaction",
]

SEATS = [
    "2A","3C","5B","7D","9F","11A","12C","14B","16D","18F",
    "21A","22C","24E","27B","31D","33F","36A","38C","40E","42B"
]

def next_seat():
    idx = st.session_state.get("seat_counter", 0)
    seat = SEATS[idx % len(SEATS)]
    st.session_state.seat_counter = idx + 1
    return seat

@st.cache_resource(show_spinner="🔧  Training Stage-1 model… (one-time, ~10 sec)")
def load_model(csv_path: str = "airline_passenger_satisfaction.csv"):
    df = pd.read_csv(csv_path)
    df_s1 = df[STAGE1_COLS].copy()
    X = df_s1.drop("Satisfaction", axis=1)
    y = df_s1["Satisfaction"].map({"Neutral or Dissatisfied": 0, "Satisfied": 1})

    X_train, _, y_train, _ = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=42
    )
    X_train = X_train.copy()
    X_train["Flight Distance"] = np.log1p(X_train["Flight Distance"])

    num_cols = X_train.select_dtypes(include=["int64", "float64"]).columns
    cat_cols = X_train.select_dtypes(include=["object"]).columns

    preprocessor = ColumnTransformer([
        ("num", StandardScaler(), num_cols),
        ("cat", OneHotEncoder(handle_unknown="ignore"), cat_cols),
    ])
    model = Pipeline([
        ("preprocessing", preprocessor),
        ("model", XGBClassifier(eval_metric="logloss", random_state=42)),
    ])
    model.fit(X_train, y_train)
    return model

def predict_record(model, record: dict):
    """
    record: flat dict with all Stage-1 feature keys (raw values, pre-log).
    Returns ('Satisfied'|'Dissatisfied', prob_satisfied, prob_dissatisfied)
    """
    df = pd.DataFrame([{
        "Gender":                 record["gender"],
        "Age":                    record["age"],
        "Customer Type":          record["cust_type"],
        "Type of Travel":         record["travel_type"],
        "Class":                  record["cls"],
        "Flight Distance":        record["dist"],
        "Ease of Online Booking": record["booking"],
        "Check-in Service":       record["checkin"],
        "Online Boarding":        record["boarding"],
        "Gate Location":          record["gate"],
    }])
    df["Flight Distance"] = np.log1p(df["Flight Distance"])
    prob = model.predict_proba(df)[0]   # [P(0=Dissatisfied), P(1=Satisfied)]
    pred = int(model.predict(df)[0])
    label = "Satisfied" if pred == 1 else "Dissatisfied"
    return label, float(prob[1]), float(prob[0])
