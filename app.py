"""Streamlit user interface for the LegalEase document generator."""

import os

import requests
import streamlit as st
from dotenv import load_dotenv

from utils.document_formatter import LOGO, format_docx, format_html_preview
from utils.pdf_generator import format_pdf
from utils.text_utils import sanitize_text

load_dotenv()
st.set_page_config(page_title="LegalEase", page_icon="⚖️", layout="wide")
st.markdown(
    """
    <style>
      .brand { color:#79c8d4; font-size:2.5rem; font-weight:750; letter-spacing:-.04em; }
      .subtle { color:#aab8c5; }
      .legal-card { background:#111c28; color:#edf2f7; border:1px solid #344454;
        border-radius:12px; padding:24px 30px; max-height:620px; overflow-y:auto;
        font-family:Georgia,serif; line-height:1.65; }
      .legal-card h1 { text-align:center; color:#9adce3; font-size:1.55rem; }
      .legal-card h2 { color:#b9d9e3; border-bottom:1px solid #344454; padding-bottom:5px; }
      .legal-card p { white-space:pre-wrap; }
      .disclaimer { color:#aab8c5; font-size:.85rem; }
    </style>
    """,
    unsafe_allow_html=True,
)
if LOGO.is_file():
    st.image(str(LOGO), width=260)
else:
    st.markdown('<div class="brand">⚖ LegalEase</div>', unsafe_allow_html=True)
st.markdown('<div class="subtle">Create a structured legal document draft, then review and edit it.</div>', unsafe_allow_html=True)
st.info(
    "LegalEase provides AI-generated legal information and document drafts for informational purposes only. "
    "It is not a substitute for advice from a qualified legal professional. Users should review documents "
    "for jurisdiction-specific requirements before use."
)

with st.form("document_request"):
    document_type = st.selectbox(
        "Document type",
        ["Freelance Work Contract", "Non-Disclosure Agreement (NDA)", "Employment Contract", "Lease Agreement", "Employment Offer Letter", "Agreement", "Other"],
    )
    if document_type == "Other":
        document_type = st.text_input("Enter document type", key="custom_document_type")
    parties = st.text_area("Parties involved", placeholder="Name and role for each party", height=90)
    terms = st.text_area("Terms & conditions", placeholder="Separate clauses with semicolons", height=130)
    dates = st.text_input("Effective date", placeholder="e.g. 10 April 2026")
    submitted = st.form_submit_button("Generate document", type="primary", use_container_width=True)

if submitted:
    missing = [label for label, value in (("Document type", document_type), ("Parties", parties), ("Terms", terms), ("Effective date", dates)) if not value.strip()]
    if missing:
        st.error("Please complete: " + ", ".join(missing) + ".")
    else:
        backend_url = os.getenv("BACKEND_URL", "http://127.0.0.1:8000").rstrip("/")
        with st.spinner("Generating your document with Gemini…"):
            try:
                response = requests.post(
                    f"{backend_url}/generate",
                    json={"document_type": document_type, "parties": parties, "terms": terms, "dates": dates},
                    timeout=(5, 180),
                )
                if response.ok:
                    generated = sanitize_text(response.json().get("content", ""))
                    if not generated:
                        st.error("The service returned an empty document. Please try again.")
                    else:
                        st.session_state.document_text = generated
                        st.session_state.document_type = document_type
                        st.session_state.edit_enabled = False
                else:
                    try:
                        detail = response.json().get("detail", "")
                    except ValueError:
                        detail = ""
                    st.error(detail or f"Document service returned HTTP {response.status_code}.")
            except requests.RequestException:
                st.error("Could not reach the LegalEase backend. Confirm that FastAPI is running and BACKEND_URL is correct.")

if st.session_state.get("document_text"):
    st.divider()
    st.subheader("Your document")
    edit = st.toggle("Edit document", key="edit_enabled")
    if edit:
        st.text_area("Document text (your edits are used for every download)", key="document_text", height=420)
    else:
        preview = format_html_preview(st.session_state.document_text)
        st.html(f'<div class="legal-card">{preview}</div>')

    current = sanitize_text(st.session_state.document_text)
    current_type = st.session_state.get("document_type", "Legal Document")
    columns = st.columns(3)
    columns[0].download_button("Download TXT", data=current.encode("utf-8"), file_name="legalease_document.txt", mime="text/plain; charset=utf-8", use_container_width=True)
    try:
        docx_data = format_docx(current, current_type)
        columns[1].download_button("Download DOCX", data=docx_data, file_name="legalease_document.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document", use_container_width=True)
    except Exception:
        columns[1].error("Could not create the Word document.")
    try:
        pdf_data = format_pdf(current, current_type)
        columns[2].download_button("Download PDF", data=pdf_data, file_name="legalease_document.pdf", mime="application/pdf", use_container_width=True)
    except Exception:
        columns[2].error("Could not create the PDF document.")
