"""Cloud Monitoring Dashboard — reliable bootstrap + full beautiful UI."""
import os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

os.environ["MQTT_TOPIC_PREFIX"] = "tuma206grp1bvg_escanes0723"
os.environ["DASHBOARD_MODE"] = "remote"

try:
    from dotenv import load_dotenv
    load_dotenv(override=False)
except ImportError:
    pass

import streamlit as st
for key in ["MQTT_HOST", "MQTT_PORT", "MQTT_TLS", "MQTT_USERNAME", "MQTT_PASSWORD"]:
    try:
        val = st.secrets.get(key)
        if val is not None and key not in os.environ:
            os.environ[key] = str(val)
    except Exception:
        pass
os.environ["MQTT_TOPIC_PREFIX"] = "tuma206grp1bvg_escanes0723"
os.environ["DASHBOARD_MODE"] = "remote"

st.set_page_config(page_title="Beverage Line Monitor", layout="wide", page_icon="⏣")

# ── Connect MQTT ──
@st.cache_resource(show_spinner="Connecting to MQTT broker...")
def get_engine():
    from engine.remote import RemoteEngineProxy
    return RemoteEngineProxy(use_mqtt=True)

engine = get_engine()
import config
bus_kind = type(engine.bus).__name__

# ── Wait for first data ──
latest = engine.latest()
if not latest:
    status = st.empty()
    status.info("Waiting for data from local_backend.py...")
    for i in range(12):
        time.sleep(1)
        latest = engine.latest()
        if latest:
            break
    if not latest:
        status.error("No data received. Is local_backend.py running?")
        st.markdown(f"- Broker: `{config.MQTT_HOST}:{config.MQTT_PORT}`\n- Topic: `{config.MQTT_TOPIC_TAGS}`")
        st.stop()
    status.empty()

# ══════════════════════════════════════════════════════════════════
# THEME
# ══════════════════════════════════════════════════════════════════
BG = "#0d1117"; CARD = "#161b22"; BDR = "#30363d"; TXT = "#c9d1d9"
TXT2 = "#b0b8c0"; ACC = "#58a6ff"; GRN = "#3fb950"; ORN = "#d2991d"
RED = "#f85149"; CYA = "#39d2c0"; STEEL = "#2d333b"; LIQUID = "#3a7bd5"

st.markdown(f"""
<style>
    .stApp {{ background: {BG}; }}
    .main .block-container {{ padding-top: 0.4rem; }}
    header[data-testid="stHeader"] {{
        background: linear-gradient(90deg, {BG}, {CARD}, {BG});
        border-bottom: 1px solid {BDR};
    }}
    header[data-testid="stHeader"] * {{ color: {TXT} !important; }}
    .kpi-card {{
        background: {CARD}; border: 1px solid {BDR}; border-radius: 10px;
        padding: 14px 16px; display: flex; align-items: center; gap: 14px;
        transition: border-color 0.3s; height: 88px; box-sizing: border-box;
    }}
    .kpi-card:hover {{ border-color: {ACC}66; }}
    .kpi-icon {{ flex-shrink: 0; width: 48px; height: 48px; }}
    .kpi-body {{ flex: 1; }}
    .kpi-value {{ font-size: 1.55rem; font-weight: 700; color: {TXT};
        line-height: 1.15; font-family: 'SF Mono','Consolas',monospace; }}
    .kpi-label {{ font-size: 0.6rem; font-weight: 600; text-transform: uppercase;
        letter-spacing: 0.08em; color: {TXT2}; margin-top: 2px; }}
    .kpi-sub {{ font-size: 0.58rem; color: {TXT2}; margin-top: 1px; }}
    .status-dot {{ display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 8px; }}
    .dot-ok {{ background: {GRN}; box-shadow: 0 0 8px {GRN}88; }}
    .dot-warn {{ background: {ORN}; box-shadow: 0 0 8px {ORN}88; }}
    .dot-fault {{ background: {RED}; box-shadow: 0 0 8px {RED}88; animation: pulse 1.5s infinite; }}
    @keyframes pulse {{ 0%,100%{{opacity:1}} 50%{{opacity:0.5}} }}
    .section-label {{ font-size: 0.62rem; font-weight: 600; text-transform: uppercase;
        letter-spacing: 0.1em; color: {TXT2}; margin: 16px 0 8px 0;
        padding-bottom: 6px; border-bottom: 1px solid {BDR}; }}
    .alarm-row {{ background: {CARD}; border-left: 3px solid {RED}; border-radius: 4px;
        padding: 6px 12px; margin: 3px 0; font-size: 0.7rem; color: {TXT}; }}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# SVG ICONS
# ══════════════════════════════════════════════════════════════════
def icon_tank(level_pct):
    h = max(3, level_pct / 100 * 30); y = 34 - h
    return f'<svg viewBox="0 0 48 48" width="48" height="48"><rect x="6" y="4" width="36" height="40" rx="6" fill="{STEEL}" stroke="{BDR}" stroke-width="1.5"/><rect x="10" y="{y:.0f}" width="28" height="{h:.0f}" rx="3" fill="url(#liq)"/><defs><linearGradient id="liq" x1="0" y1="1" x2="0" y2="0"><stop offset="0%" stop-color="{LIQUID}" stop-opacity="0.95"/><stop offset="100%" stop-color="{ACC}" stop-opacity="0.45"/></linearGradient></defs></svg>'

def icon_thermo(temp, ok):
    c = GRN if ok else RED
    return f'<svg viewBox="0 0 48 48" width="48" height="48"><circle cx="24" cy="36" r="10" fill="none" stroke="{c}" stroke-width="2.5"/><rect x="20" y="6" width="8" height="22" rx="4" fill="{c}" opacity="0.7"/><circle cx="24" cy="36" r="5" fill="{c}" opacity="0.8"/></svg>'

def icon_cooler(temp, ok):
    c = CYA if ok else ORN
    return f'<svg viewBox="0 0 48 48" width="48" height="48"><circle cx="24" cy="26" r="12" fill="none" stroke="{c}" stroke-width="2"/><line x1="24" y1="10" x2="24" y2="18" stroke="{c}" stroke-width="2"/><line x1="24" y1="34" x2="24" y2="42" stroke="{c}" stroke-width="2"/><line x1="10" y1="26" x2="18" y2="26" stroke="{c}" stroke-width="2"/><line x1="30" y1="26" x2="38" y2="26" stroke="{c}" stroke-width="2"/></svg>'

def icon_flow(active):
    c = ACC if active else TXT2; anim = '<animateTransform attributeName="transform" type="rotate" from="0 24 24" to="360 24 24" dur="0.8s" repeatCount="indefinite"/>' if active else ""
    return f'<svg viewBox="0 0 48 48" width="48" height="48"><circle cx="24" cy="24" r="16" fill="none" stroke="{c}" stroke-width="2.5"/><g>{anim}<polygon points="24,12 32,20 24,16 16,20" fill="{c}" opacity="0.8"/></g></svg>'

def icon_buffer(buf, mx):
    frac = buf / max(mx, 1); c = ORN if frac > 0.85 else (GRN if frac < 0.5 else ACC)
    fw = int(frac * 34)
    return f'<svg viewBox="0 0 48 48" width="48" height="48"><rect x="4" y="20" width="40" height="8" rx="3" fill="{STEEL}" stroke="{BDR}" stroke-width="1.5"/><rect x="7" y="23" width="{fw}" height="2" rx="1" fill="{c}"/><circle cx="10" cy="24" r="5" fill="{STEEL}" stroke="{BDR}" stroke-width="1.5"/><circle cx="38" cy="24" r="5" fill="{STEEL}" stroke="{BDR}" stroke-width="1.5"/><rect x="16" y="10" width="5" height="10" rx="2" fill="{LIQUID}" opacity="0.6"/><rect x="24" y="10" width="5" height="10" rx="2" fill="{LIQUID}" opacity="0.6"/><rect x="32" y="10" width="5" height="10" rx="2" fill="{LIQUID}" opacity="0.6"/></svg>'

def icon_bottles(n):
    c = CYA if n > 0 else TXT2
    return f'<svg viewBox="0 0 48 48" width="48" height="48"><rect x="18" y="10" width="12" height="28" rx="3" fill="none" stroke="{c}" stroke-width="2"/><rect x="20" y="14" width="8" height="6" rx="1" fill="{LIQUID}" opacity="0.6"/><rect x="20" y="22" width="8" height="6" rx="1" fill="{LIQUID}" opacity="0.6"/><rect x="21" y="7" width="6" height="4" rx="1" fill="{c}" opacity="0.5"/></svg>'

def icon_plc(state):
    c = GRN if state == "RUNNING" else (RED if state == "FAULT" else ORN)
    return f'<svg viewBox="0 0 48 48" width="48" height="48"><circle cx="24" cy="24" r="16" fill="none" stroke="{c}" stroke-width="3"/><circle cx="24" cy="24" r="8" fill="{c}" opacity="0.75"/></svg>'

def icon_alarm(active):
    c = RED if active else GRN; ch = "!" if active else "&#10003;"
    return f'<svg viewBox="0 0 48 48" width="48" height="48"><polygon points="24,4 44,44 4,44" fill="none" stroke="{c}" stroke-width="2.5"/><text x="24" y="36" text-anchor="middle" fill="{c}" font-size="18" font-weight="900">{ch}</text></svg>'

def kpi_card(icon_svg, value, label, sub="", status=""):
    dot_cls = {"ok": "dot-ok", "warn": "dot-warn", "fault": "dot-fault"}.get(status, "")
    dot = f'<span class="status-dot {dot_cls}"></span>' if dot_cls else ""
    return f'<div class="kpi-card"><div class="kpi-icon">{icon_svg}</div><div class="kpi-body"><div class="kpi-value">{dot}{value}</div><div class="kpi-label">{label}</div><div class="kpi-sub">{sub}</div></div></div>'

# ══════════════════════════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════════════════════════
st.markdown(f"""
<div style="background:linear-gradient(90deg,{BG},{CARD},{BG});border-radius:8px;
padding:10px 22px;margin-bottom:10px;border-bottom:1px solid {BDR};
display:flex;justify-content:space-between;align-items:center;">
<div>
  <span style="font-size:1.1rem;font-weight:700;color:#f0f6fc;letter-spacing:0.06em;">BEVERAGE LINE</span>
  <span style="font-size:0.58rem;color:{TXT2};margin-left:12px;letter-spacing:0.05em;">LIVE MONITOR — MQTT</span>
</div>
<div style="font-size:0.62rem;color:{TXT2};text-align:right;">
</div>
</div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# MQTT STATUS
# ══════════════════════════════════════════════════════════════════
if bus_kind == "MqttBus":
    st.caption(f"MQTT connected → {config.MQTT_HOST}:{config.MQTT_PORT}")
else:
    st.caption(f"WARNING: Using {bus_kind} — MQTT broker unreachable.")

# ══════════════════════════════════════════════════════════════════
# LIVE DATA — auto-refresh every 5s
# ══════════════════════════════════════════════════════════════════
latest = engine.latest()

if not latest:
    st.error("No data. Check that local_backend.py is running.")
elif bus_kind != "MqttBus":
    st.warning("Not connected to MQTT. Showing cached data if any.")
else:
    alarm_code = int(latest.get("alarm_code", 0))
    plc = latest.get("plc_state", "IDLE")
    temp = float(latest.get("pasteur_temp", 0))
    cool = float(latest.get("cooler_temp", 0))
    flow = float(latest.get("flow_rate", 0))
    level = float(latest.get("tank_level", 0))
    buf = int(latest.get("conveyor_queue", 0))
    buf_max = int(latest.get("conveyor_max", config.CONVEYOR_MAX_BOTTLES))
    completed = int(latest.get("bottles_completed", 0))
    heater = float(latest.get("heater_power_cmd", 0))
    cool_v = float(latest.get("cooling_valve_cmd", 0))
    tick = int(latest.get("tick", 0))

    t_ok = config.PASTEUR_SAFE_MIN <= temp <= config.PASTEUR_SAFE_MAX
    c_ok = cool <= config.COOLER_MAX_BOTTLING
    l_ok = config.TANK_LEVEL_LOW <= level <= config.TANK_LEVEL_HIGH
    alarm_label = config.ALARM_LABELS.get(alarm_code, "None")

    last_ts = latest.get("ts", 0)
    age = time.time() - last_ts if last_ts else 999
    if age < 5:
        mqtt_dot = "dot-ok"; mqtt_msg = f"MQTT live · updated {age:.0f}s ago"
    elif age < 15:
        mqtt_dot = "dot-warn"; mqtt_msg = f"MQTT stale · last update {age:.0f}s ago"
    else:
        mqtt_dot = "dot-fault"; mqtt_msg = f"MQTT disconnected · {age:.0f}s since last data"

    plc_dot = {"RUNNING": "dot-ok", "STARTING": "dot-warn", "FAULT": "dot-fault"}.get(plc, "")

    st.markdown(
        f'<div style="display:flex;gap:24px;align-items:center;font-size:0.72rem;color:{TXT2};padding:4px 0 8px 0;">'
        f'<span><span class="status-dot {mqtt_dot}"></span>{mqtt_msg}</span>'
        f'<span>PLC: <b style="color:{TXT}">{plc}</b></span>'
        f'<span>Alarm: <b style="color:{RED if alarm_code else GRN}">{alarm_label}</b></span>'
        f'<span>Tick: <b style="color:{TXT}">{tick}</b></span>'
        f'</div>', unsafe_allow_html=True)

    # ── KPI Cards Row 1 ──
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(kpi_card(icon_thermo(temp, t_ok), f"{temp:.1f}°C", "PASTEURIZER",
            f"Heater {heater:.0f}% · SP {config.PASTEUR_SETPOINT:.0f}°C · {config.PASTEUR_SAFE_MIN:.0f}–{config.PASTEUR_SAFE_MAX:.0f}°C",
            "ok" if t_ok else "fault"), unsafe_allow_html=True)
    with c2:
        st.markdown(kpi_card(icon_cooler(cool, c_ok), f"{cool:.1f}°C", "COOLER",
            f"Valve {cool_v:.0f}% · Limit {config.COOLER_MAX_BOTTLING:.0f}°C",
            "ok" if c_ok else "warn"), unsafe_allow_html=True)
    with c3:
        st.markdown(kpi_card(icon_flow(flow > 1), f"{flow:.1f} L/min", "FLOW RATE",
            f"{'FLOWING' if flow > 1 else 'IDLE'}", "ok" if flow > 1 else ""), unsafe_allow_html=True)
    with c4:
        st.markdown(kpi_card(icon_bottles(completed), f"{completed}", "COMPLETED",
            f"Buffer: {buf}/{buf_max}  ·  Belt {latest.get('conveyor_cmd',0):.0f}%",
            "ok" if completed > 0 else ""), unsafe_allow_html=True)

    # ── KPI Cards Row 2 ──
    c5, c6, c7, c8 = st.columns(4)
    with c5:
        st.markdown(kpi_card(icon_tank(level), f"{level:.1f}%", "RAW TANK",
            f"Target {config.TANK_LEVEL_TARGET:.0f}% · Range {config.TANK_LEVEL_LOW:.0f}–{config.TANK_LEVEL_HIGH:.0f}%",
            "ok" if l_ok else "warn"), unsafe_allow_html=True)
    with c6:
        st.markdown(kpi_card(icon_buffer(buf, buf_max), f"{buf}/{buf_max}", "CONVEYOR BUFFER",
            f"{'CRITICAL' if buf > buf_max*0.85 else 'NORMAL'}",
            "warn" if buf > buf_max * 0.85 else "ok"), unsafe_allow_html=True)
    with c7:
        plc_label = {"IDLE": "IDLE", "STARTING": "STARTING", "RUNNING": "RUNNING",
                     "FAULT": "FAULT", "STOPPING": "STOPPING"}.get(plc, plc)
        st.markdown(kpi_card(icon_plc(plc), plc_label, "PLC STATE", "Automated",
            "ok" if plc == "RUNNING" else ("fault" if plc == "FAULT" else "warn")), unsafe_allow_html=True)
    with c8:
        st.markdown(kpi_card(icon_alarm(alarm_code != 0),
            alarm_label if alarm_code else "NORMAL", "STATUS",
            "Active alarm" if alarm_code else "No active alarms",
            "" if alarm_code == 0 else "fault"), unsafe_allow_html=True)

    # ── Trend Charts ──
    st.markdown('<div class="section-label">Process Trends</div>', unsafe_allow_html=True)
    history = engine.historian.recent(window_s=300)

    if history:
        import pandas as pd
        import plotly.graph_objects as go

        df = pd.DataFrame(history)
        df["time"] = pd.to_datetime(df["ts"], unit="s")
        if "plc_state" in df.columns:
            df = df[df["plc_state"] != "IDLE"]

        left, right = st.columns(2)
        with left:
            fig_tank = go.Figure()
            if "tank_level" in df.columns:
                fig_tank.add_trace(go.Scatter(x=df["time"], y=df["tank_level"],
                    name="Tank Level", fill="tozeroy",
                    line=dict(color=ACC, width=2, shape="spline"),
                    fillcolor="rgba(88,166,255,0.12)",
                    hovertemplate="%{y:.1f}%<extra></extra>"))
            for y, lbl, clr in [(config.TANK_LEVEL_TARGET, f"Target {config.TANK_LEVEL_TARGET:.0f}%", ORN),
                                (config.TANK_LEVEL_LOW, "", RED), (config.TANK_LEVEL_HIGH, "", RED)]:
                fig_tank.add_hline(y=y, line_dash="dot",
                    line_color=f"rgba({248 if clr==RED else 210},{153 if clr==ORN else 81},{73 if clr==RED else 29},0.4)",
                    annotation_text=lbl)
            fig_tank.update_layout(title="Tank Level", plot_bgcolor=CARD, paper_bgcolor=BG,
                font=dict(color=TXT, size=10), height=280,
                margin=dict(t=35, b=10, l=45, r=10),
                xaxis=dict(gridcolor=BDR, zeroline=False),
                yaxis=dict(gridcolor=BDR, zeroline=False, range=[0, 105]),
                showlegend=False, uirevision="cloud_tank")
            st.plotly_chart(fig_tank, use_container_width=True, key="cld_tank")

        with right:
            fig_temp = go.Figure()
            if "pasteur_temp" in df.columns:
                fig_temp.add_trace(go.Scatter(x=df["time"], y=df["pasteur_temp"],
                    name="Pasteur Temp", line=dict(color=RED, width=2, shape="spline"),
                    hovertemplate="%{y:.1f}°C<extra></extra>"))
            for y, lbl in [(config.PASTEUR_SAFE_MAX, "78°C"), (config.PASTEUR_SAFE_MIN, "68°C")]:
                fig_temp.add_hline(y=y, line_dash="dot", line_color="rgba(248,81,73,0.45)",
                                   annotation_text=lbl)
            fig_temp.add_hline(y=config.PASTEUR_SETPOINT, line_dash="dash",
                line_color="rgba(210,153,29,0.45)",
                annotation_text=f"SP {config.PASTEUR_SETPOINT:.0f}°C")
            fig_temp.update_layout(title="Pasteurizer Temperature", plot_bgcolor=CARD,
                paper_bgcolor=BG, font=dict(color=TXT, size=10), height=280,
                margin=dict(t=35, b=10, l=45, r=10),
                xaxis=dict(gridcolor=BDR, zeroline=False),
                yaxis=dict(gridcolor=BDR, zeroline=False, range=[60, 82]),
                showlegend=False, uirevision="cloud_temp")
            st.plotly_chart(fig_temp, use_container_width=True, key="cld_temp")
    else:
        st.caption("Waiting for trend data...")

    # ── Recent Alarms ──
    st.markdown('<div class="section-label">Recent Alarms</div>', unsafe_allow_html=True)
    alarms = engine.historian.recent_alarms(20)
    if alarms:
        adf = pd.DataFrame(alarms)
        adf["time"] = pd.to_datetime(adf["ts"], unit="s")
        adf = adf.sort_values("time", ascending=False)
        for _, row in adf.head(5).iterrows():
            atime = row["time"].strftime("%H:%M:%S")
            st.markdown(f'<div class="alarm-row"><b>{atime}</b> &nbsp;{row.get("label","?")} &mdash; {row.get("description","")[:140]}</div>', unsafe_allow_html=True)
    else:
        st.caption("No alarms recorded.")

    # ── Footer ──
    st.markdown(f"""
    <div style="text-align:center;padding:12px 0 4px 0;font-size:0.55rem;color:{TXT2};">
    BEVERAGE LINE MONITOR · TUMA206 Group 1 · MQTT topic: {config.MQTT_TOPIC_TAGS}
    </div>""", unsafe_allow_html=True)

    # Auto-refresh
    time.sleep(5)
    st.rerun()
