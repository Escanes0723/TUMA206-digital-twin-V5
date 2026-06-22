"""Cloud Monitoring Dashboard — diagnostic: find which import hangs."""
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

# Load secrets
for key in ["MQTT_HOST", "MQTT_PORT", "MQTT_TLS", "MQTT_USERNAME",
            "MQTT_PASSWORD"]:
    try:
        val = st.secrets.get(key)
        if val is not None and key not in os.environ:
            os.environ[key] = str(val)
    except Exception:
        pass

st.set_page_config(page_title="Cloud Monitor", page_icon="⏣")
st.title("Beverage Line — Cloud Monitor")

tests = [
    ("pandas", "import pandas as pd"),
    ("plotly", "import plotly.graph_objects as go"),
    ("config", "import config"),
    ("engine.remote", "from engine.remote import RemoteEngineProxy"),
    ("dashboard.cloud", "import dashboard.cloud"),
]

results = []
for name, code in tests:
    try:
        exec(code)
        results.append((name, "OK", ""))
    except Exception as e:
        results.append((name, "FAIL", str(e)))

for name, status, err in results:
    if status == "OK":
        st.success(f"✓ {name}")
    else:
        st.error(f"✗ {name}: {err}")

st.caption(f"Python: {sys.version}")
