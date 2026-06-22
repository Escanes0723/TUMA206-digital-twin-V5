"""Cloud Monitoring Dashboard — ultra-lightweight, no dashboard.cloud import."""
import os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

import streamlit as st

for key in ["MQTT_HOST", "MQTT_PORT", "MQTT_TLS", "MQTT_USERNAME",
            "MQTT_PASSWORD", "MQTT_TOPIC_PREFIX",
            "OPENAI_API_KEY", "ANTHROPIC_API_KEY", "DASHBOARD_MODE"]:
    try:
        val = st.secrets.get(key)
        if val is not None and key not in os.environ:
            os.environ[key] = str(val)
    except Exception:
        pass

os.environ["DASHBOARD_MODE"] = "remote"
# ── FORCE your unique topic — ignore secrets/config ──
os.environ["MQTT_TOPIC_PREFIX"] = "tuma206grp1bvg_escanes0723"

st.set_page_config(page_title="Cloud Monitor", page_icon="⏣")
st.title("Beverage Line — Cloud Monitor")

@st.cache_resource(show_spinner="Connecting to MQTT broker...")
def connect_engine():
    from engine.remote import RemoteEngineProxy
    return RemoteEngineProxy(use_mqtt=True)

engine = connect_engine()
import config

bus = type(engine.bus).__name__
st.caption(f"Bus: {bus} | Broker: {config.MQTT_HOST}:{config.MQTT_PORT} | Topic: {config.MQTT_TOPIC_TAGS}")

# Wait up to 15 seconds for the first MQTT message
# (local_backend publishes every ~5 seconds)
placeholder = st.empty()
latest = None
for i in range(15):
    latest = engine.latest()
    if latest:
        break
    placeholder.info(f"Waiting for data from local_backend.py... ({i+1}s)")
    time.sleep(1)

if not latest:
    placeholder.error("No data received after 15s. Is local_backend.py running on your computer?")
    st.markdown(f"""
    **Check:**
    1. Run `python local_backend.py` on your machine
    2. Make sure it prints "[OK] Connected via MqttBus"
    3. Broker: `{config.MQTT_HOST}:{config.MQTT_PORT}`
    4. Topic: `{config.MQTT_TOPIC_TAGS}`
    """)
else:
    placeholder.empty()
    alarm_code = int(latest.get("alarm_code", 0))
    plc = latest.get("plc_state", "?")
    temp = float(latest.get("pasteur_temp", 0))
    cool = float(latest.get("cooler_temp", 0))
    level = float(latest.get("tank_level", 0))
    flow = float(latest.get("flow_rate", 0))
    buf = int(latest.get("conveyor_queue", 0))
    bottles = int(latest.get("bottles_completed", 0))
    tick = int(latest.get("tick", 0))
    alarm_label = config.ALARM_LABELS.get(alarm_code, "None")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Pasteur Temp", f"{temp:.1f}°C")
    c2.metric("Cooler Temp", f"{cool:.1f}°C")
    c3.metric("Tank Level", f"{level:.1f}%")
    c4.metric("Flow Rate", f"{flow:.1f} L/min")

    c5, c6, c7, c8 = st.columns(4)
    c5.metric("PLC State", plc)
    c6.metric("Alarm", alarm_label)
    c7.metric("Bottles", bottles)
    c8.metric("Tick", tick)

    st.caption(f"Auto-refreshes every 5s | Tick: {tick}")
    time.sleep(5)
    st.rerun()
