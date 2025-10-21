# app.py — Excel Cleaner SaaS (Freemium → Fixed ₹10k Unlock)
# ----------------------------------------------------------
# - 3 free runs/day (session)
# - Fixed ₹10,000 unlock via Razorpay Payment Page
# - File-size guard
# - Calls FastAPI: POST {API_BASE}{CLEAN_ENDPOINT}
# - Returns cleaned XLSX for download

import os, datetime as dt, requests, streamlit as st

st.set_page_config(page_title="Excel Cleaner SaaS", page_icon="🧹", layout="centered")

# ---------- CONFIG ----------
API_BASE = os.getenv("API_BASE", "http://localhost:8000")
CLEAN_ENDPOINT = os.getenv("CLEAN_ENDPOINT", "/clean")
FREE_LIMIT_PER_DAY = int(os.getenv("FREE_LIMIT_PER_DAY", "3"))
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "180"))
MAX_MB = float(os.getenv("DEMO_MAX_MB", "2"))

# Razorpay Payment Page URL (fixed ₹10,000)
RAZORPAY_PAGE = os.getenv("RAZORPAY_PAGE", "https://pages.razorpay.com/REPLACE_EXCEL_10K")
CONTACT_MAILTO = os.getenv("CONTACT_MAILTO",
                           "mailto:contact@taskmindai.net?subject=TaskMindAI%20Excel%20Cleaner%20Access")

# ---------- DEMO LIMIT ----------
if "usage_count" not in st.session_state:
    st.session_state.usage_count = 0
if "last_reset" not in st.session_state:
    st.session_state.last_reset = dt.date.today()
if st.session_state.last_reset != dt.date.today():
    st.session_state.usage_count = 0
    st.session_state.last_reset = dt.date.today()

st.markdown(
    f"""
    <div style="background:#111a3a;border:1px solid #223060;padding:10px 12px;border-radius:10px;margin-bottom:12px;">
      ⚙ <b>Daily usage:</b> {st.session_state['usage_count']} / {FREE_LIMIT_PER_DAY} free runs.<br>
      🔓 <span style="color:#9fb7ff">Need full unlimited access?</span><br>
      <a href="{RAZORPAY_PAGE}" target="_blank" style="color:#9cf;font-weight:700;">
        Pay ₹10,000 to Unlock Lifetime Access
      </a> ·
      <a href="{CONTACT_MAILTO}" style="color:#9cf;">Contact us</a>
    </div>
    """,
    unsafe_allow_html=True,
)

def check_limit_or_stop():
    if st.session_state.usage_count >= FREE_LIMIT_PER_DAY:
        st.error("Demo limit reached for today. Unlock full access below.")
        st.link_button("💳 Pay ₹10,000 to Unlock", RAZORPAY_PAGE, use_container_width=True)
        st.link_button("📧 Contact for custom plan", CONTACT_MAILTO, use_container_width=True)
        st.stop()

# Sidebar meter
with st.sidebar:
    st.subheader("Usage")
    st.progress(min(st.session_state.usage_count / FREE_LIMIT_PER_DAY, 1.0))
    st.caption(f"{st.session_state.usage_count} of {FREE_LIMIT_PER_DAY} free runs today")
    st.caption(f"Demo file-size cap: {MAX_MB:.0f} MB")
    st.markdown("---")
    st.caption(f"API: {API_BASE}{CLEAN_ENDPOINT}")

# ---------- UI ----------
st.title("🧹 Excel Cleaner SaaS")
st.write("Upload an Excel/CSV file and get a cleaned version instantly.")

uploaded_file = st.file_uploader(
    "Choose an Excel or CSV file",
    type=["xlsx","xls","csv"],
    accept_multiple_files=False,
    help=f"Limit: {int(MAX_MB)}MB per file"
)

# ---------- PROCESS ----------
if uploaded_file:
    st.success(f"File {uploaded_file.name} uploaded successfully!")
    if st.button("🧼 Clean File", type="primary", use_container_width=True):

        check_limit_or_stop()

        size_mb = uploaded_file.size / (1024 * 1024)
        if size_mb > MAX_MB:
            st.error(f"⚠ Demo limit: file must be under {MAX_MB:.0f} MB. Your file is {size_mb:.2f} MB.")
            st.stop()

        with st.spinner("Cleaning your file..."):
            try:
                files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
                resp = requests.post(f"{API_BASE}{CLEAN_ENDPOINT}", files=files, timeout=REQUEST_TIMEOUT)
            except Exception as e:
                st.error(f"Backend unreachable. Check API_BASE. Error: {e}")
                st.stop()

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
            st.caption("Generated via TaskMindAI · taskmindai.net")
            st.session_state.usage_count += 1
        else:
            msg = ""
            try: msg = resp.json().get("detail", "")
            except Exception: msg = resp.text[:500]
            st.error(f"Cleaning failed (status {resp.status_code}). {msg or 'Please try another file.'}")
else:
    st.info("Please upload a file to begin cleaning.")
