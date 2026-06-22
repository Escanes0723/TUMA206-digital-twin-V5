"""Cloud Monitoring Dashboard — deploy this on Streamlit Cloud.

Data flow:  local_backend.py  --MQTT-->  HiveMQ Cloud  --MQTT-->  this app
           (your laptop)                (cloud broker)           (Streamlit Cloud)
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ── Force YOUR unique topic BEFORE anything else imports config ──
os.environ["MQTT_TOPIC_PREFIX"] = "tuma206grp1bvg_escanes0723"
os.environ["DASHBOARD_MODE"] = "remote"

# Load .env for local testing (wont override our forced values above)
try:
    from dotenv import load_dotenv
    load_dotenv(override=False)
except ImportError:
    pass

# Load Streamlit Cloud secrets
try:
    import streamlit as st
    for key in ["MQTT_HOST", "MQTT_PORT", "MQTT_TLS", "MQTT_USERNAME",
                "MQTT_PASSWORD",
                "OPENAI_API_KEY", "ANTHROPIC_API_KEY"]:
        try:
            val = st.secrets.get(key)
            if val is not None and key not in os.environ:
                os.environ[key] = str(val)
        except Exception:
            pass
except Exception:
    pass

# Re-apply in case secrets or .env overwrote them
os.environ["MQTT_TOPIC_PREFIX"] = "tuma206grp1bvg_escanes0723"
os.environ["DASHBOARD_MODE"] = "remote"

import dashboard.cloud  # noqa: F401 — full beautiful dashboard
