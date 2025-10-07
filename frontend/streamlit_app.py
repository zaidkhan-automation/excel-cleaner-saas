import os
import requests
import streamlit as st

# Backend API URL — you’ll set this in Render environment variable later
API_BASE = os.getenv("API_BASE_URL", "http://localhost:8000")

st.set_page_config(page_title="Excel Cleaner", page_icon="🧹")
st.title("🧹 Excel Cleaner SaaS")
st.write("Upload your Excel file below and get a cleaned version instantly!")

# File uploader
uploaded_file = st.file_uploader("Choose an Excel or CSV file", type=["xlsx", "xls", "csv"])

if uploaded_file:
    st.success(f"File {uploaded_file.name} uploaded successfully!")
    if st.button("🧼 Clean File"):
        with st.spinner("Cleaning your file... please wait"):
            try:
                files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
                response = requests.post(f"{API_BASE}/clean", files=files, timeout=120)

                if response.status_code == 200:
                    st.success("✅ File cleaned successfully!")
                    st.download_button(
                        label="⬇ Download Cleaned File",
                        data=response.content,
                        file_name="cleaned_" + uploaded_file.name,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                else:
                    st.error(f"❌ Error: {response.status_code}")
                    st.text(response.text[:300])
            except Exception as e:
                st.error(f"⚠ Something went wrong: {e}")
else:
    st.info("Please upload a file to begin cleaning.")
