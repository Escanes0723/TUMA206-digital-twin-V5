"""Cloud Monitoring Dashboard — minimal bootstrap, no heavy imports at startup."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load .env for local testing
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Load Streamlit Cloud secrets
try:
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
except Exception:
    pass

os.environ.setdefault("DASHBOARD_MODE", "remote")

# Show a simple loading page first so the user sees something immediately
import streamlit as st
st.set_page_config(page_title="Beverage Line Monitor", page_icon="⏣")
st.title("Beverage Line Cloud Monitor")
st.caption("Connecting to MQTT broker...")

# Now try to load the dashboard
try:
    import dashboard.cloud  # noqa: F401
except Exception as e:
    st.error(f"Failed to load dashboard: {e}")
    import traceback
    st.code(traceback.format_exc())
