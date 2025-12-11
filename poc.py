import os
import re
import time
import streamlit as st
import pdfplumber
from pdf2image import convert_from_path
import pytesseract
import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted

# -----------------------------
# 1️⃣ Configure Gemini API key
# -----------------------------
API_KEY = ""  # replace if needed
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("models/gemini-flash-latest")

# -----------------------------
# 2️⃣ PDF text extraction
# -----------------------------
def extract_pdf_text(pdf_file):
    try:
        with pdfplumber.open(pdf_file) as pdf:
            text = "\n".join([page.extract_text() or "" for page in pdf.pages])
        if text.strip():
            return text
        else:
            raise ValueError("Empty text, switching to OCR")
    except Exception:
        pages = convert_from_path(pdf_file, 300)
        text = "\n".join([pytesseract.image_to_string(page) for page in pages])
        return text

# -----------------------------
# 3️⃣ Safe generate function with retry
# -----------------------------
def safe_generate(prompt):
    while True:
        try:
            response = model.generate_content(prompt)
            return response.text.strip()
        except ResourceExhausted as e:
            retry_seconds = getattr(e, "retry_delay", 10)
            st.warning(f"Quota exceeded. Retrying in {retry_seconds} seconds...")
            time.sleep(retry_seconds)

# -----------------------------
# 4️⃣ Extract multiple fields in one request
# -----------------------------
def extract_fields(text):
    prompt = f"""
Extract the following from the document text:

1. Net salary
2. Pay date
3. Bank salary
4. Bank deposit date

Document:
{text}
"""
    result_text = safe_generate(prompt)
    net_salary_match = re.search(r"£[\d,]+\.\d{2}", result_text)
    date_match = re.search(r"\d{2} \w{3} \d{4}", result_text)
    net_salary = net_salary_match.group() if net_salary_match else ""
    pay_date = date_match.group() if date_match else ""
    return net_salary.replace(",", ""), pay_date

# -----------------------------
# 5️⃣ Validation function
# -----------------------------
def validate_salary_and_date(payslip_salary, bank_salary, payslip_date, bank_date):
    salary_match = payslip_salary.strip() == bank_salary.strip()
    date_match = payslip_date.strip() == bank_date.strip()
    overall_pass = salary_match and date_match
    return overall_pass, salary_match, date_match

# -----------------------------
# 6️⃣ Streamlit UI
# -----------------------------
st.set_page_config(page_title="Payslip vs Bank Validation", layout="wide")

# Custom CSS for background and cards
st.markdown(
    """
    <style>
    .stApp { background-color: #e6f0ea; color: #000; }
    h1 { color: #00843D; }
    .pass-card { background-color: #00843D; color: white; padding: 10px; border-radius: 8px; margin-bottom: 10px; font-weight: bold; }
    .fail-card { background-color: #D32F2F; color: white; padding: 10px; border-radius: 8px; margin-bottom: 10px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True
)

st.title("💷 Payslip vs Bank Statement Validation")

col1, col2 = st.columns(2)
with col1:
    payslip_file = st.file_uploader("📄 Upload Payslip PDF", type="pdf")
with col2:
    bank_file = st.file_uploader("🏦 Upload Bank Statement PDF", type="pdf")

if payslip_file and bank_file:
    with st.spinner("Extracting text from PDFs..."):
        payslip_text = extract_pdf_text(payslip_file)
        bank_text = extract_pdf_text(bank_file)

    with st.spinner("Extracting fields via Gemini LLM..."):
        payslip_salary, payslip_date = extract_fields(payslip_text)
        bank_salary, bank_date = extract_fields(bank_text)

    overall_pass, salary_match, date_match = validate_salary_and_date(
        payslip_salary, bank_salary, payslip_date, bank_date
    )

    # Display extracted data
    st.subheader("📊 Extracted Data")
    st.markdown(f"""
    **Payslip Salary:** {payslip_salary}  
    **Bank Salary:** {bank_salary}  
    **Payslip Date:** {payslip_date}  
    **Bank Date:** {bank_date}  
    """)

    # Display validation results
    st.subheader("✅ Validation Results")
    if overall_pass:
        st.markdown(f"<div class='pass-card'>All fields match: PASS 🎉</div>", unsafe_allow_html=True)
        st.balloons()
    else:
        st.markdown(f"<div class='fail-card'>Inconsistencies detected ❌</div>", unsafe_allow_html=True)
        # Show individual mismatches without animation
        if not salary_match:
            st.markdown(f"<div class='fail-card'>Salary mismatch</div>", unsafe_allow_html=True)
        if not date_match:
            st.markdown(f"<div class='fail-card'>Date mismatch</div>", unsafe_allow_html=True)