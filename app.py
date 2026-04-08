import streamlit as st

st.set_page_config(
    page_title="SkyRate | Airline Intelligence",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Shared state ────────────────────────────────────────
if "submissions" not in st.session_state:
    st.session_state.submissions = []
if "seat_counter" not in st.session_state:
    st.session_state.seat_counter = 0

# ── Custom CSS ──────────────────────────────────────────
st.markdown("""
<style>
/* Global dark theme */
.stApp { background-color: #0B1629; }
section[data-testid="stSidebar"] { display: none; }

/* Hide default streamlit elements */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 0 !important; max-width: 100% !important; }

/* Top navigation bar */
.topbar {
    display: flex; align-items: center; justify-content: space-between;
    padding: 12px 28px; background: #0D1E38;
    border-bottom: 1px solid rgba(255,255,255,0.07);
    position: sticky; top: 0; z-index: 999;
}
.logo-wrap { display: flex; align-items: center; gap: 10px; }
.logo-icon {
    width: 32px; height: 32px; background: #1ECFAA;
    border-radius: 8px; display: flex; align-items: center; justify-content: center;
}
.logo-text { font-size: 17px; font-weight: 700; color: #fff; margin: 0; }
.logo-sub  { font-size: 10px; color: #4A5E7A; text-transform: uppercase;
             letter-spacing: .5px; margin: 0; }
.live-badge {
    display: flex; align-items: center; gap: 6px;
    background: rgba(30,207,170,.12); border: 1px solid rgba(30,207,170,.25);
    border-radius: 20px; padding: 4px 14px; font-size: 12px; color: #1ECFAA;
}
.ldot {
    width: 7px; height: 7px; background: #1ECFAA; border-radius: 50%;
    animation: pulse 1.5s infinite;
}
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.3} }
.page-content { padding: 24px 28px; }

/* Cards */
.sky-card {
    background: #1A2744; border: 1px solid #253555;
    border-radius: 14px; padding: 18px;
}
/* Metric cards */
.metric-card {
    background: #1A2744; border: 1px solid #253555;
    border-radius: 12px; padding: 14px 16px;
}
.metric-label { font-size: 10px; text-transform: uppercase;
                letter-spacing: .5px; color: #4A5E7A; margin-bottom: 4px; }
.metric-value { font-size: 26px; font-weight: 700; line-height: 1; }
.metric-sub   { font-size: 11px; color: #4A5E7A; margin-top: 3px; }

/* Chat bubbles */
.chat-container {
    display: flex; flex-direction: column; gap: 12px;
    max-height: 420px; overflow-y: auto;
    padding: 16px; background: #0B1629;
    border-radius: 12px; border: 1px solid #1A2744;
    margin-bottom: 16px;
}
.bubble-bot, .bubble-user {
    display: flex; align-items: flex-start; gap: 8px; max-width: 80%;
}
.bubble-user { flex-direction: row-reverse; align-self: flex-end; }
.av-bot {
    width: 30px; height: 30px; border-radius: 50%; flex-shrink: 0;
    background: linear-gradient(135deg,#1ECFAA,#1A8EFF);
    display: flex; align-items: center; justify-content: center;
    font-size: 10px; font-weight: 700; color: #0B1629;
}
.av-user {
    width: 30px; height: 30px; border-radius: 50%; flex-shrink: 0;
    background: #1A2744; border: 1px solid #253555;
    display: flex; align-items: center; justify-content: center;
    font-size: 10px; color: #94A3B8;
}
.msg-bot {
    background: #1A2744; color: #CBD5E1;
    padding: 10px 14px; border-radius: 12px 12px 12px 3px;
    font-size: 14px; line-height: 1.55;
}
.msg-user {
    background: #1ECFAA; color: #0B1629; font-weight: 600;
    padding: 10px 14px; border-radius: 12px 12px 3px 12px;
    font-size: 14px; line-height: 1.55;
}
.msg-bot b, .msg-bot strong { color: #1ECFAA; }

/* Progress */
.pbar-wrap { margin-bottom: 6px; }
.pbar-track {
    height: 4px; background: #1A2744; border-radius: 2px;
    margin-bottom: 4px; overflow: hidden;
}
.pbar-fill {
    height: 100%;
    background: linear-gradient(90deg,#1ECFAA,#1A8EFF);
    border-radius: 2px; transition: width .4s;
}
.pbar-label { font-size: 11px; color: #4A5E7A; text-align: right; }

/* Section header */
.sec-head {
    font-size: 11px; font-weight: 600; color: #4A5E7A;
    text-transform: uppercase; letter-spacing: .6px;
    display: flex; align-items: center; gap: 10px;
    margin: 18px 0 12px;
}
.sec-head::after {
    content: ''; flex: 1; height: 1px; background: #1A2744;
}

/* Table */
.sky-table { width: 100%; border-collapse: collapse; font-size: 12px; }
.sky-table thead { background: #0D1E38; }
.sky-table th {
    padding: 9px 13px; text-align: left; color: #4A5E7A;
    font-size: 10px; text-transform: uppercase; letter-spacing: .4px;
    border-bottom: 1px solid #253555; white-space: nowrap;
}
.sky-table td {
    padding: 9px 13px; color: #CBD5E1;
    border-bottom: 1px solid #1A2744; white-space: nowrap;
}
.sky-table tr:hover td { background: rgba(26,39,68,.6); }
.sky-table tr:last-child td { border-bottom: none; }

/* Badges */
.bdg { display:inline-block; padding:3px 10px; border-radius:12px;
       font-size:11px; font-weight:600; }
.bdg-sat { background:#1ECFAA20; color:#1ECFAA; border:1px solid #1ECFAA30; }
.bdg-dis { background:#EF444420; color:#F87171; border:1px solid #EF444430; }
.stars { color: #FCD34D; }

/* Thanks card */
.thanks-card {
    background: #1A2744; border: 1px solid rgba(30,207,170,.25);
    border-radius: 14px; padding: 24px; text-align: center;
    max-width: 480px; margin: 0 auto;
}
.check-circle {
    width: 56px; height: 56px; background: rgba(30,207,170,.15);
    border-radius: 50%; display: flex; align-items: center;
    justify-content: center; margin: 0 auto 14px;
    font-size: 22px; color: #1ECFAA;
}
</style>
""", unsafe_allow_html=True)

# ── Top bar ─────────────────────────────────────────────
st.markdown("""
<div class="topbar">
  <div class="logo-wrap">
    <div class="logo-icon">
      <svg width="18" height="18" viewBox="0 0 24 24" fill="#0B1629">
        <path d="M21 16v-2l-8-5V3.5c0-.83-.67-1.5-1.5-1.5S10 2.67 10 3.5V9l-8 5v2l8-2.5V19l-2 1.5V22l3.5-1 3.5 1v-1.5L13 19v-5.5z"/>
      </svg>
    </div>
    <div>
      <div class="logo-text">SkyRate</div>
      <div class="logo-sub">Airline Intelligence · Stage 1</div>
    </div>
  </div>
  <div class="live-badge"><div class="ldot"></div>Live · Pre-Flight Feedback</div>
</div>
""", unsafe_allow_html=True)

# ── Tab navigation ──────────────────────────────────────
tab1, tab2 = st.tabs(["🤖  Passenger Feedback", "📊  Airline Dashboard"])

with tab1:
    from pages import chatbot
    chatbot.run()

with tab2:
    from pages import dashboard
    dashboard.run()
