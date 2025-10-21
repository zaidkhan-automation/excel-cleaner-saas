# Excel Cleaner SaaS — Streamlit app (freemium + Razorpay unlock)
# ---------------------------------------------------------------
# Env (Render): API_BASE, CLEAN_ENDPOINT=/clean, FREE_LIMIT_PER_DAY=3, DEMO_MAX_MB=2
# Start: streamlit run app.py --server.port $PORT --server.address 0.0.0.0

import os, datetime as dt, requests, streamlit as st

st.set_page_config(page_title="Excel Cleaner SaaS", page_icon="🧹", layout="centered")

API_BASE = os.getenv("API_BASE", "http://localhost:8000")
CLEAN_ENDPOINT = os.getenv("CLEAN_ENDPOINT", "/clean")
FREE_LIMIT_PER_DAY = int(os.getenv("FREE_LIMIT_PER_DAY", "3"))
MAX_MB = float(os.getenv("DEMO_MAX_MB", "2"))
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "180"))
PAYMENT_URL = "https://rzp.io/rzp/taskmindai-payment"
CONTACT = "mailto:contact@taskmindai.net"

if "usage_count" not in st.session_state:
    st.session_state.usage_count = 0
if "last_reset" not in st.session_state:
    st.session_state.last_reset = dt.date.today()
if st.session_state.last_reset != dt.date.today():
    st.session_state.usage_count = 0
    st.session_state.last_reset = dt.date.today()

st.markdown(f"""
<div style="background:#0f1425;border:1px solid #1d2b48;padding:12px;border-radius:12px;margin:4px 0 16px">
  <b>Demo mode:</b> {st.session_state['usage_count']} / {FREE_LIMIT_PER_DAY} free runs today.
  <div style="margin-top:6px">
    Need unlimited runs? <a href="{PAYMENT_URL}" target="_blank" style="color:#9cc9ff;font-weight:600">Unlock via Razorpay</a> ·
    <a href="{CONTACT}" style="color:#9cc9ff">Contact</a>
  </div>
</div>
""", unsafe_allow_html=True)

def guard_or_stop():
    if st.session_state.usage_count >= FREE_LIMIT_PER_DAY:
        st.error("Daily demo limit reached. Unlock full access to continue.")
        st.link_button("💳 Unlock via Razorpay", PAYMENT_URL, use_container_width=True)
        st.stop()

with st.sidebar:
    st.subheader("Usage")
    st.progress(min(st.session_state.usage_count / FREE_LIMIT_PER_DAY, 1.0))
    st.caption(f"API: {API_BASE}{CLEAN_ENDPOINT}")
    st.caption(f"Max size: {MAX_MB:.0f} MB")

st.title("🧹 Excel Cleaner")
st.write("Upload an Excel/CSV and get a cleaned XLSX back in seconds.")

file = st.file_uploader("Choose an Excel or CSV file", type=["xlsx","xls","csv"],
                        help=f"Limit: {int(MAX_MB)}MB")

if file:
    if st.button("🧼 Clean File", type="primary", use_container_width=True):
        guard_or_stop()
        size_mb = file.size / (1024*1024)
        if size_mb > MAX_MB:
            st.error(f"File is {size_mb:.2f} MB. Demo cap is {MAX_MB:.0f} MB.")
            st.stop()

        with st.spinner("Cleaning…"):
            try:
                resp = requests.post(f"{API_BASE}{CLEAN_ENDPOINT}",
                                     files={"file": (file.name, file.getvalue())},
                                     timeout=REQUEST_TIMEOUT)
            except Exception as e:
                st.error(f"Backend unreachable: {e}")
                st.stop()

        if resp.status_code == 200:
            st.success("✅ Cleaned file ready")
            st.download_button("📥 Download XLSX", resp.content,
                               file_name=f"cleaned_{file.name.rsplit('.',1)[0]}.xlsx",
                               mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                               use_container_width=True)
            st.caption("Generated via TaskMindAI · taskmindai.net")
            st.session_state.usage_count += 1
        else:
            st.error(f"Cleaning failed ({resp.status_code}). {resp.text[:300] or ''}")
else:
    st.info("Upload a file to begin.")
