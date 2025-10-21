# streamlit_app.py  — Excel Cleaner SaaS (demo + unlock CTA)
# -----------------------------------------------------------
# Features:
# - Daily free limit (session-based) + banner
# - Editable-amount Razorpay unlock CTA
# - File-size guard
# - Calls FastAPI backend: POST {API_BASE}/clean
# - Returns cleaned file for download

import os
import io
import datetime as dt
import requests
import streamlit as st

# ------------------- CONFIG -------------------
st.set_page_config(page_title="Excel Cleaner SaaS", page_icon="🧹", layout="centered")

API_BASE = os.getenv("API_BASE", "http://localhost:8000")
FREE_LIMIT_PER_DAY = int(os.getenv("FREE_LIMIT_PER_DAY", "3"))
RAZORPAY_LINK = os.getenv("RAZORPAY_LINK", "https://razorpay.me/@taskmindai")  # editable amount
CONTACT_MAILTO = os.getenv(
    "CONTACT_MAILTO",
    "mailto:contact@taskmindai.net?subject=TaskMindAI%20Excel%20Cleaner%20Access"
)
MAX_MB = float(os.getenv("DEMO_MAX_MB", "2"))  # demo file-size cap

# ------------------- DEMO LIMIT (BANNER) -------------------
if "usage_count" not in st.session_state:
    st.session_state.usage_count = 0
if "last_reset" not in st.session_state:
    st.session_state.last_reset = dt.date.today()

# daily reset
if st.session_state.last_reset != dt.date.today():
    st.session_state.usage_count = 0
    st.session_state.last_reset = dt.date.today()

st.markdown(
    f"""
    <div style="background:#111a3a;border:1px solid #223060;padding:10px 12px;border-radius:10px;margin-bottom:12px;">
      ⚙ <b>Daily usage:</b> {st.session_state['usage_count']} / {FREE_LIMIT_PER_DAY} free runs.<br>
      🔓 <span style="color:#9fb7ff">Need full unlimited access?</span><br>
      <a href="{RAZORPAY_LINK}" target="_blank" style="color:#9cf;font-weight:700;">Pay to Unlock (amount editable)</a> ·
      <a href="{CONTACT_MAILTO}" style="color:#9cf;">Contact us</a>
    </div>
    """,
    unsafe_allow_html=True,
)

def check_limit_or_stop():
    """Stop processing if today's free quota is over."""
    if st.session_state.usage_count >= FREE_LIMIT_PER_DAY:
        st.error("Demo limit reached for today. Unlock full access below.")
        st.link_button("💳 Pay to Unlock (Editable Amount)", RAZORPAY_LINK, use_container_width=True)
        st.link_button("📧 Contact for custom pricing", CONTACT_MAILTO, use_container_width=True)
        st.stop()

# Optional sidebar meter
with st.sidebar:
    st.subheader("Usage")
    st.progress(min(st.session_state.usage_count / FREE_LIMIT_PER_DAY, 1.0))
    st.caption(f"{st.session_state.usage_count} of {FREE_LIMIT_PER_DAY} free runs today")
    st.caption(f"Demo file-size cap: {MAX_MB:.0f} MB")
    st.markdown("---")
    st.caption(f"API: {API_BASE}")

# ------------------- UI -------------------
st.title("🧹 Excel Cleaner SaaS")
st.write("Upload your Excel or CSV file below and get a cleaned version instantly.")

uploaded_file = st.file_uploader(
    "Choose an Excel or CSV file",
    type=["xlsx", "xls", "csv"],
    accept_multiple_files=False,
    help=f"Limit: {int(MAX_MB)}MB per file"
)

# ------------------- PROCESS -------------------
if uploaded_file:
    st.success(f"File {uploaded_file.name} uploaded successfully!")
    if st.button("🧼 Clean File", type="primary", use_container_width=True):

        # 1) check demo limit
        check_limit_or_stop()

        # 2) size guard
        size_mb = uploaded_file.size / (1024 * 1024)
        if size_mb > MAX_MB:
            st.error(f"⚠ Demo limit: file must be under {MAX_MB:.0f} MB. Your file is {size_mb:.2f} MB.")
            st.stop()

        # 3) call backend
        with st.spinner("Cleaning your file... please wait"):
            try:
                files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
                resp = requests.post(f"{API_BASE}/clean", files=files, timeout=180)
            except Exception as e:
                st.error(f"Backend unreachable. Check API_BASE. Error: {e}")
                st.stop()

        # 4) handle response
        if resp.status_code == 200:
            st.success("✅ File cleaned successfully!")
            out_name = f"cleaned_{uploaded_file.name.rsplit('.',1)[0]}.xlsx"
            st.download_button(
                "📥 Download Cleaned File",
                data=resp.content,
                file_name=out_name,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )
            # increment quota usage only on success
            st.session_state.usage_count += 1
            st.caption("Generated via TaskMindAI · taskmindai.net")
        else:
            # try to extract error
            msg = ""
            try:
                msg = resp.json().get("detail", "")
            except Exception:
                msg = resp.text[:500]
            st.error(f"Cleaning failed (status {resp.status_code}). {msg or 'Please try another file.'}")

else:
    st.info("Please upload a file to begin cleaning.")
