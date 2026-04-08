# ✈️ SkyRate — Airline Passenger Satisfaction App
**Group 07 | PGP Data Science & AI | Great Learning | April 2026**

---

## 📁 File Structure
```
airline_app/
├── app.py                               # Entry point — tabs + shared CSS
├── model.py                             # Stage-1 XGBoost pipeline (trains on startup)
├── requirements.txt
├── .gitignore
├── README.md
├── airline_passenger_satisfaction.csv   # ← ADD THIS FILE (not committed)
└── pages/
    ├── __init__.py
    ├── chatbot.py                       # Passenger chatbot (no prediction shown)
    └── dashboard.py                     # Airline analytics dashboard
```

---

## 🔄 How It Works
```
Passenger → Chatbot → submits ratings (seat auto-assigned)
                ↓
     Stage-1 XGBoost predicts (exact notebook pipeline)
                ↓
   Result stored in st.session_state.submissions
                ↓
   Airline Dashboard tab → KPIs + Charts + Table update instantly
```
No prediction is shown to the passenger — only the airline dashboard sees it.

---

## 🚀 Run Locally
```bash
# 1. Place airline_passenger_satisfaction.csv in the project root
# 2. Install dependencies
pip install -r requirements.txt
# 3. Run
streamlit run app.py
```
Open **http://localhost:8501**

---

## 📤 Push to GitHub
```bash
git init
git add .
git commit -m "SkyRate app — Stage 1"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/skypulse.git
git push -u origin main
```

---

## ☁️ Deploy on Streamlit Cloud
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. New app → select your repo → **Main file: `app.py`**
3. Deploy
4. Upload `airline_passenger_satisfaction.csv` via **App settings → Files**

---

## 📊 Stage-1 Pipeline (exact notebook)
- Target: Satisfied=1, Neutral/Dissatisfied=0
- Split: 80/20 stratified, random_state=42
- log1p(Flight Distance) after split
- ColumnTransformer: StandardScaler(num) + OHE(cat)
- XGBClassifier(eval_metric='logloss', random_state=42)
