"""Cloud Monitoring Dashboard — Streamlit Cloud entry point.

Data flow:  local_backend.py  --MQTT-->  HiveMQ Cloud  --MQTT-->  this app
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ── Force YOUR unique topic BEFORE anything else ──
os.environ["MQTT_TOPIC_PREFIX"] = "tuma206grp1bvg_escanes0723"
os.environ["DASHBOARD_MODE"] = "remote"

try:
    from dotenv import load_dotenv
    load_dotenv(override=False)
except ImportError:
    pass

# Streamlit Cloud secrets (MQTT credentials)
try:
    import streamlit as st
    for key in ["MQTT_HOST", "MQTT_PORT", "MQTT_TLS", "MQTT_USERNAME",
                "MQTT_PASSWORD"]:
        try:
            val = st.secrets.get(key)
            if val is not None and key not in os.environ:
                os.environ[key] = str(val)
        except Exception:
            pass
except Exception:
    pass

# Re-apply in case something overwrote them
os.environ["MQTT_TOPIC_PREFIX"] = "tuma206grp1bvg_escanes0723"
os.environ["DASHBOARD_MODE"] = "remote"

import dashboard.cloud  # noqa: F401
