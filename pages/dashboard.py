"""
pages/dashboard.py
Airline dashboard — reads st.session_state.submissions (set by chatbot).
Matches the unified widget: KPIs + bar chart + donut + filterable table.
"""
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

TEAL = "#1ECFAA"
RED  = "#F87171"
AMBER= "#FCD34D"
BG   = "#1A2744"
BG2  = "#0D1E38"

def _df() -> pd.DataFrame:
    return pd.DataFrame(st.session_state.get("submissions", []))

def _stars(n):
    return "★" * int(n) + "☆" * (5 - int(n))

def run():
    st.markdown('<div class="page-content">', unsafe_allow_html=True)

    df = _df()

    # ── Empty state ───────────────────────────────────────────────────
    if df.empty:
        st.markdown("""
        <div style="text-align:center;padding:60px 20px">
          <div style="font-size:48px;margin-bottom:16px">📭</div>
          <div style="font-size:18px;font-weight:600;color:#E2E8F0;margin-bottom:8px">No passenger data yet</div>
          <div style="font-size:13px;color:#4A5E7A">
            Ask passengers to complete the feedback chatbot.<br>
            Their responses appear here instantly once submitted.
          </div>
        </div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        return

    # ── KPIs ─────────────────────────────────────────────────────────
    total   = len(df)
    sat     = (df["Predicted"] == "Satisfied").sum()
    dis     = total - sat
    sat_pct = round(sat / total * 100)
    avg_b   = round(df["Online Boarding"].mean(), 1)

    st.markdown('<div class="sec-head">Key Metrics</div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""<div class="metric-card">
          <div class="metric-label">Total responses</div>
          <div class="metric-value" style="color:#E2E8F0">{total}</div>
          <div class="metric-sub">passengers</div></div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="metric-card">
          <div class="metric-label">Satisfied</div>
          <div class="metric-value" style="color:{TEAL}">{sat}</div>
          <div class="metric-sub">{sat_pct}% of responses</div></div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""<div class="metric-card">
          <div class="metric-label">Dissatisfied</div>
          <div class="metric-value" style="color:{RED}">{dis}</div>
          <div class="metric-sub">{100-sat_pct}% of responses</div></div>""", unsafe_allow_html=True)
    with c4:
        st.markdown(f"""<div class="metric-card">
          <div class="metric-label">Avg online boarding</div>
          <div class="metric-value" style="color:{AMBER}">{avg_b}</div>
          <div class="metric-sub">out of 5.0</div></div>""", unsafe_allow_html=True)

    # ── Charts ────────────────────────────────────────────────────────
    st.markdown('<div class="sec-head">Analytics</div>', unsafe_allow_html=True)
    ch1, ch2 = st.columns(2)

    # Bar chart — avg rating per feature
    with ch1:
        feats = {
            "Online Booking":  df["Online Booking"].mean(),
            "Check-in":        df["Check-in"].mean(),
            "Online Boarding": df["Online Boarding"].mean(),
            "Gate Location":   df["Gate Location"].mean(),
        }
        colors = [TEAL if v >= 4 else AMBER if v >= 3 else RED for v in feats.values()]
        fig_bar = go.Figure(go.Bar(
            x=list(feats.values()),
            y=list(feats.keys()),
            orientation="h",
            marker_color=colors,
            text=[f"{v:.1f}" for v in feats.values()],
            textposition="outside",
        ))
        fig_bar.update_layout(
            title="Average rating by feature",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#94A3B8",
            xaxis=dict(range=[0, 5.5], gridcolor="#1A2744", tickfont_color="#4A5E7A"),
            yaxis=dict(gridcolor="#1A2744"),
            margin=dict(l=0, r=40, t=40, b=0),
            height=260,
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    # Donut chart — satisfaction split
    with ch2:
        fig_pie = go.Figure(go.Pie(
            labels=["Satisfied", "Dissatisfied"],
            values=[sat, dis],
            hole=0.52,
            marker_colors=[TEAL, RED],
            textinfo="percent+label",
            textfont_color=["#0B1629", "#0B1629"],
        ))
        fig_pie.update_layout(
            title="Satisfaction split",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#94A3B8",
            showlegend=False,
            margin=dict(l=0, r=0, t=40, b=0),
            height=260,
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    # ── Passenger table ───────────────────────────────────────────────
    st.markdown('<div class="sec-head">Passenger Records</div>', unsafe_allow_html=True)

    # Filter row
    fc1, fc2, fc3, fc4 = st.columns([3, 1, 1, 1])
    with fc1:
        search = st.text_input("Search", placeholder="Search by PNR or seat…",
                               label_visibility="collapsed")
    with fc2:
        f_all = st.button("All", use_container_width=True,
                          type="primary" if st.session_state.get("dash_filter","all")=="all" else "secondary")
    with fc3:
        f_sat = st.button("Satisfied", use_container_width=True,
                          type="primary" if st.session_state.get("dash_filter")=="sat" else "secondary")
    with fc4:
        f_dis = st.button("Dissatisfied", use_container_width=True,
                          type="primary" if st.session_state.get("dash_filter")=="dis" else "secondary")

    if f_all: st.session_state.dash_filter = "all"
    if f_sat: st.session_state.dash_filter = "sat"
    if f_dis: st.session_state.dash_filter = "dis"
    filt = st.session_state.get("dash_filter", "all")

    # Apply filters
    filtered = df.copy()
    if search.strip():
        q = search.strip().upper()
        filtered = filtered[
            filtered["PNR"].str.contains(q, na=False) |
            filtered["Seat"].str.upper().str.contains(q, na=False)
        ]
    if filt == "sat":
        filtered = filtered[filtered["Predicted"] == "Satisfied"]
    elif filt == "dis":
        filtered = filtered[filtered["Predicted"] == "Dissatisfied"]

    st.caption(f"Showing **{len(filtered)}** of **{total}** records")

    # Build HTML table
    rows_html = ""
    for _, row in filtered.iterrows():
        pred  = row["Predicted"]
        bdg   = f'<span class="bdg {"bdg-sat" if pred=="Satisfied" else "bdg-dis"}">{pred}</span>'
        stars = f'<span class="stars">{_stars(row["Online Booking"])}</span>'
        brd   = f'<span class="stars">{_stars(row["Online Boarding"])}</span>'
        ci    = f'<span class="stars">{_stars(row["Check-in"])}</span>'
        gl    = f'<span class="stars">{_stars(row["Gate Location"])}</span>'
        rows_html += f"""<tr>
          <td><b style="color:#E2E8F0">{row['PNR']}</b></td>
          <td style="color:#94A3B8">{row['Seat']}</td>
          <td>{row.get('Travel Type','—')}</td>
          <td>{row.get('Class','—')}</td>
          <td>{stars}</td>
          <td>{ci}</td>
          <td>{brd}</td>
          <td>{gl}</td>
          <td>{bdg}</td>
        </tr>"""

    st.markdown(f"""
    <div style="border-radius:10px;border:1px solid #253555;overflow:hidden">
    <table class="sky-table">
      <thead><tr>
        <th>PNR</th><th>Seat</th><th>Travel type</th><th>Class</th>
        <th>Booking</th><th>Check-in</th><th>Boarding</th><th>Gate</th>
        <th>Prediction</th>
      </tr></thead>
      <tbody>{rows_html}</tbody>
    </table>
    </div>""", unsafe_allow_html=True)

    # Export button
    st.markdown("<br>", unsafe_allow_html=True)
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️  Export all data as CSV", data=csv,
                       file_name="skypulse_data.csv", mime="text/csv",
                       type="primary")

    st.markdown('</div>', unsafe_allow_html=True)
