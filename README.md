AI Document Validator — Payslip vs Bank Statement Consistency Checker

A lightweight and intelligent document verification system that extracts salary and date information from payslips and bank statements using Gemini LLM, compares the values, and determines whether the financial records are consistent.

This project automates manual validation workflows commonly used in mortgage underwriting, risk assessment, and income verification.

 **Workflow Overview**
	1.	User uploads a payslip and bank statement
	2.	Text is extracted (OCR used automatically if needed)
	3.	Gemini extracts salary and dates
	4.	System cross-validates the fields
	5.	User sees a Pass/Fail decision with breakdown

Features

🔍 PDF Text Extraction
	•	Extracts text using pdfplumber
	•	Falls back to OCR using pytesseract + pdf2image

 LLM-Powered Field Extraction

Uses Google Gemini to extract:
	•	Net salary
	•	Pay date
	•	Bank salary
	•	Deposit date

All via a single optimized prompt.

Intelligent Validation

Compares:
	•	Payslip salary vs bank deposit
	•	Payslip date vs bank date

Returns PASS / FAIL with reasons.

Streamlit UI
	•	Clean & interactive dashboard
	•	Real-time extraction + validation
	•	Pass/Fail cards with helpful visual indicators

Dependencies needed to be installed - pip install **streamlit pdfplumber pdf2image pytesseract google-generativeai**
