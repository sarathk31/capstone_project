"""
pages/chatbot.py
Conversational chatbot — matches the unified widget exactly.
- No prediction shown to passenger
- Seat auto-filled
- No duplicate questions (all state in st.session_state)
- Data → st.session_state.submissions → dashboard reads it
"""
import random
import pandas as pd
import streamlit as st
from model import load_model, predict_record, next_seat

# ── Step constants ───────────────────────────────────────────────────
TOTAL_STEPS = 7
SEATS_LABELS = ["😡 Very poor","😕 Poor","😐 Average","🙂 Good","😍 Excellent"]

BOT_GREETINGS = [
    "Hey there, traveller! I'm **SkyBot** — your pre-flight feedback assistant. It takes about 90 seconds. Ready?",
    "Hello! I'm **SkyBot** ✈️  I'd love to hear about your pre-flight experience. Shall we get started?",
    "Welcome! **SkyBot** here. Your honest ratings help us make the skies friendlier. Ready to go?",
]

# ── State helpers ────────────────────────────────────────────────────
def _s(key, default=None):
    return st.session_state.get(key, default)

def _init():
    defaults = {
        "cb_step":     "greet",
        "cb_history":  [],
        "cb_pnr":      "",
        "cb_seat":     "",
        "cb_gender":   "",
        "cb_age":      30,
        "cb_cust":     "",
        "cb_travel":   "",
        "cb_cls":      "",
        "cb_dist":     844,
        "cb_booking":  0,
        "cb_checkin":  0,
        "cb_boarding": 0,
        "cb_gate":     0,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

def _add_msg(role, text):
    st.session_state.cb_history.append({"role": role, "text": text})

def _go(step):
    st.session_state.cb_step = step
    st.rerun()

# ── Progress bar ────────────────────────────────────────────────────
STEP_ORDER = ["greet","pnr","gender","cust","travel","dist","ratings","done"]

def _progress():
    step = st.session_state.cb_step
    idx  = STEP_ORDER.index(step) if step in STEP_ORDER else 0
    pct  = int(idx / (len(STEP_ORDER)-1) * 100)
    st.markdown(f"""
    <div class="pbar-wrap">
      <div class="pbar-track"><div class="pbar-fill" style="width:{pct}%"></div></div>
      <div class="pbar-label">Step {idx} of {TOTAL_STEPS}</div>
    </div>""", unsafe_allow_html=True)

# ── Chat history renderer ────────────────────────────────────────────
def _render_history():
    if not st.session_state.cb_history:
        return
    html = '<div class="chat-container">'
    for m in st.session_state.cb_history:
        if m["role"] == "bot":
            html += f'''
            <div class="bubble-bot">
              <div class="av-bot">SK</div>
              <div class="msg-bot">{m["text"]}</div>
            </div>'''
        else:
            html += f'''
            <div class="bubble-user">
              <div class="av-user">ME</div>
              <div class="msg-user">{m["text"]}</div>
            </div>'''
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)

# ── Rating widget ────────────────────────────────────────────────────
def _star_widget(key: str, question: str, sub: str, icon: str):
    st.markdown(f"""
    <div class="sky-card" style="margin-bottom:10px">
      <div style="font-size:18px;margin-bottom:4px">{icon}</div>
      <div style="font-size:14px;font-weight:600;color:#E2E8F0;margin-bottom:2px">{question}</div>
      <div style="font-size:11px;color:#4A5E7A;margin-bottom:12px">{sub}</div>
    </div>""", unsafe_allow_html=True)
    cols = st.columns(5)
    current = st.session_state.get(f"star_{key}", 0)
    for i, col in enumerate(cols):
        v = i + 1
        label = f"{v}\n{SEATS_LABELS[i]}"
        is_sel = current == v
        if col.button(label, key=f"sb_{key}_{v}",
                      type="primary" if is_sel else "secondary",
                      use_container_width=True):
            st.session_state[f"star_{key}"] = v
            st.rerun()
    return st.session_state.get(f"star_{key}", 0)

# ── Main run ─────────────────────────────────────────────────────────
def run():
    _init()
    st.markdown('<div class="page-content">', unsafe_allow_html=True)
    _progress()
    _render_history()

    step = st.session_state.cb_step

    # ── GREET ─────────────────────────────────────────────────────────
    if step == "greet":
        if not st.session_state.cb_history:
            _add_msg("bot", random.choice(BOT_GREETINGS))
            st.rerun()
        if st.button("Let's go! →", type="primary", use_container_width=True):
            _add_msg("user", "Let's go!")
            _add_msg("bot", "First up — what's your **PNR number**? You'll find it on your boarding pass or booking email.")
            _go("pnr")

    # ── PNR ──────────────────────────────────────────────────────────
    elif step == "pnr":
        with st.form("f_pnr", clear_on_submit=True):
            pnr = st.text_input("PNR number", placeholder="e.g. ABC123",
                                label_visibility="collapsed")
            sub = st.form_submit_button("Confirm →", type="primary", use_container_width=True)
        if sub:
            v = pnr.strip().upper()
            if not v:
                st.warning("Please enter your PNR number.")
            else:
                seat = next_seat()
                st.session_state.cb_pnr  = v
                st.session_state.cb_seat = seat
                _add_msg("user", f"PNR: **{v}**")
                _add_msg("bot",  f"Got it! PNR **{v}** ✓  Seat auto-assigned: **{seat}**. Now a couple of quick questions about you.")
                _go("gender")

    # ── GENDER ────────────────────────────────────────────────────────
    elif step == "gender":
        with st.container():
            st.markdown('<div class="sky-card">', unsafe_allow_html=True)
            st.markdown("**How do you identify?**")
            st.caption("For anonymous analytics only")
            col1, col2 = st.columns(2)
            for gender, col in [("Male", col1), ("Female", col2)]:
                if col.button(gender, key=f"g_{gender}", use_container_width=True):
                    st.session_state.cb_gender = gender
                    _add_msg("user", gender)
                    _add_msg("bot", "Got it! Are you a **first-time** or **returning** customer? ✈️")
                    _go("cust")
            st.markdown('</div>', unsafe_allow_html=True)

    # ── CUSTOMER TYPE ────────────────────────────────────────────────
    elif step == "cust":
        with st.container():
            st.markdown('<div class="sky-card">', unsafe_allow_html=True)
            st.markdown("**Customer type**")
            st.caption("Returning customers get a virtual high-five 🙌")
            col1, col2 = st.columns(2)
            for ctype, col in [("First-time", col1), ("Returning", col2)]:
                if col.button(ctype, key=f"c_{ctype}", use_container_width=True):
                    st.session_state.cb_cust = ctype
                    _add_msg("user", ctype)
                    msg = "Welcome back! 🎉 We love familiar faces. What was the purpose of your trip?" \
                          if ctype == "Returning" else \
                          "Welcome aboard for the first time! 🥳 What was the purpose of your trip?"
                    _add_msg("bot", msg)
                    _go("travel")
            st.markdown('</div>', unsafe_allow_html=True)

    # ── TRAVEL TYPE ──────────────────────────────────────────────────
    elif step == "travel":
        with st.container():
            st.markdown('<div class="sky-card">', unsafe_allow_html=True)
            st.markdown("**Type of travel**")
            st.caption("Helps us improve service for your journey type")
            col1, col2 = st.columns(2)
            for ttype, col in [("Business", col1), ("Personal", col2)]:
                if col.button(ttype, key=f"t_{ttype}", use_container_width=True):
                    st.session_state.cb_travel = ttype
                    st.session_state.cb_cls    = "Business" if ttype == "Business" else "Economy"
                    _add_msg("user", ttype)
                    _add_msg("bot", "Got it! 📏 Roughly how far was your flight? Drag to set the distance.")
                    _go("dist")
            st.markdown('</div>', unsafe_allow_html=True)

    # ── FLIGHT DISTANCE ──────────────────────────────────────────────
    elif step == "dist":
        with st.container():
            st.markdown('<div class="sky-card">', unsafe_allow_html=True)
            dist = st.slider("Flight distance (miles)",
                             min_value=31, max_value=4983, value=844, step=50,
                             label_visibility="collapsed")
            st.markdown(f'<div style="font-size:22px;font-weight:700;color:#1ECFAA">{dist:,} mi</div>', unsafe_allow_html=True)
            st.caption("Short <200 mi · Regional ~800 mi · International ~4000 mi")
            st.session_state.cb_dist = dist
            if st.button("Confirm →", type="primary", use_container_width=True):
                _add_msg("user", f"~{dist:,} miles")
                _add_msg("bot", "Now the main event — let's rate your **pre-flight experience**. Be honest, we can take it! 😄")
                st.session_state.cb_rating_idx = 0
                _go("ratings")
            st.markdown('</div>', unsafe_allow_html=True)

    # ── RATINGS ───────────────────────────────────────────────────────
    elif step == "ratings":
        RATING_FIELDS = [
            ("cb_booking",  "booking",  "📱", "Ease of online booking",   "Was our booking system a breeze or a puzzle?"),
            ("cb_checkin",  "checkin",  "🏢", "Check-in service",         "How smooth was the airport check-in?"),
            ("cb_boarding", "boarding", "📲", "Online boarding",          "Digital boarding pass experience"),
            ("cb_gate",     "gate",     "🚪", "Gate location convenience","Was your gate easy to reach?"),
        ]
        idx = st.session_state.get("cb_rating_idx", 0)

        if idx >= len(RATING_FIELDS):
            # All ratings collected → save and show thanks
            _save_and_done()
        else:
            ss_key, star_key, icon, question, sub = RATING_FIELDS[idx]
            val = _star_widget(star_key, question, sub, icon)
            label = "Next →" if idx < len(RATING_FIELDS)-1 else "Submit feedback →"
            if st.button(label, type="primary", use_container_width=True,
                         disabled=(val == 0)):
                st.session_state[ss_key] = val
                _add_msg("user", f"{icon} {question}: **{val}/5** — {SEATS_LABELS[val-1]}")
                if idx < len(RATING_FIELDS)-1:
                    next_q = RATING_FIELDS[idx+1][3]
                    _add_msg("bot", f"Got it! Next: **{next_q}**")
                st.session_state.cb_rating_idx = idx + 1
                st.rerun()

    # ── DONE ──────────────────────────────────────────────────────────
    elif step == "done":
        _render_thanks()

    st.markdown('</div>', unsafe_allow_html=True)


def _save_and_done():
    """Run model, save to submissions, advance to done."""
    model = load_model()
    record = {
        "gender":      st.session_state.cb_gender,
        "age":         st.session_state.cb_age,
        "cust_type":   st.session_state.cb_cust,
        "travel_type": st.session_state.cb_travel,
        "cls":         st.session_state.cb_cls,
        "dist":        st.session_state.cb_dist,
        "booking":     st.session_state.cb_booking,
        "checkin":     st.session_state.cb_checkin,
        "boarding":    st.session_state.cb_boarding,
        "gate":        st.session_state.cb_gate,
    }
    label, prob_sat, prob_dis = predict_record(model, record)

    submission = {
        "PNR":            st.session_state.cb_pnr,
        "Seat":           st.session_state.cb_seat,
        "Gender":         record["gender"],
        "Customer Type":  record["cust_type"],
        "Travel Type":    record["travel_type"],
        "Class":          record["cls"],
        "Flight Distance":record["dist"],
        "Online Booking": record["booking"],
        "Check-in":       record["checkin"],
        "Online Boarding":record["boarding"],
        "Gate Location":  record["gate"],
        "Predicted":      label,
        "Prob Satisfied": round(prob_sat * 100, 1),
    }
    st.session_state.submissions.append(submission)
    _add_msg("bot", "Thank you! Your feedback has been recorded and sent to the airline team. 🙏")
    _go("done")


def _render_thanks():
    """Thank you card — NO prediction shown."""
    st.markdown(f"""
    <div class="thanks-card">
      <div class="check-circle">✓</div>
      <div style="font-size:18px;font-weight:700;color:#1ECFAA;margin-bottom:8px">Feedback submitted!</div>
      <div style="font-size:13px;color:#94A3B8;line-height:1.6;margin-bottom:18px">
        Your response has been logged and is now visible on the
        <b style="color:#E2E8F0">Airline Dashboard</b>.
        The operations team will review it shortly.
      </div>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:18px;text-align:left">
        <div class="metric-card"><div class="metric-label">PNR</div>
          <div class="metric-value" style="font-size:16px;color:#E2E8F0">{st.session_state.cb_pnr}</div></div>
        <div class="metric-card"><div class="metric-label">Seat</div>
          <div class="metric-value" style="font-size:16px;color:#E2E8F0">{st.session_state.cb_seat}</div></div>
        <div class="metric-card"><div class="metric-label">Online Booking</div>
          <div class="metric-value" style="font-size:18px;color:#FCD34D">{st.session_state.cb_booking}<span style="font-size:11px;color:#4A5E7A">/5</span></div></div>
        <div class="metric-card"><div class="metric-label">Online Boarding</div>
          <div class="metric-value" style="font-size:18px;color:#FCD34D">{st.session_state.cb_boarding}<span style="font-size:11px;color:#4A5E7A">/5</span></div></div>
        <div class="metric-card"><div class="metric-label">Check-in</div>
          <div class="metric-value" style="font-size:18px;color:#FCD34D">{st.session_state.cb_checkin}<span style="font-size:11px;color:#4A5E7A">/5</span></div></div>
        <div class="metric-card"><div class="metric-label">Gate Location</div>
          <div class="metric-value" style="font-size:18px;color:#FCD34D">{st.session_state.cb_gate}<span style="font-size:11px;color:#4A5E7A">/5</span></div></div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Submit another response 🔄", use_container_width=True):
        _reset()

def _reset():
    for k in list(st.session_state.keys()):
        if k.startswith("cb_") or k.startswith("star_") or k.startswith("sb_"):
            del st.session_state[k]
    st.rerun()
