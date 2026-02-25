# /Users/admin/LG/Markdown/src/main.py

import os
import sys
import tempfile
from pathlib import Path

sys.path.append(".")

import streamlit as st
import pandas as pd

from extraction.csv_to_markdown import extract_text_from_csv
from extraction.excel_to_markdown import extract_text_from_excel

# ================================================
# Optional PDF Support (Docling)
# ================================================

try:
    from docling.document_converter import DocumentConverter
    DOCLING_AVAILABLE = True
except ImportError:
    DOCLING_AVAILABLE = False


def pdf_to_markdown_from_bytes(file_bytes: bytes) -> str:
    if not DOCLING_AVAILABLE:
        raise RuntimeError(
            "Docling is not installed. Install it with: pip install docling"
        )

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(file_bytes)
        tmp_path = tmp.name

    try:
        converter = DocumentConverter()
        result = converter.convert(tmp_path)
        return result.document.export_to_markdown()
    finally:
        try:
            os.remove(tmp_path)
        except:
            pass


# ================================================
# Streamlit UI
# ================================================

st.set_page_config(
    page_title="Document to Markdown Converter",
    layout="centered"
)

st.title("📄 File → Markdown Converter")
st.caption("Supports CSV / Excel / PDF (Japanese enabled)")

st.divider()

uploaded = st.file_uploader(
    "Upload a CSV, Excel, or PDF file",
    type=["csv", "xlsx", "xls", "pdf"]
)

# ================================================
# Main Conversion Logic
# ================================================

if uploaded:
    try:
        with st.spinner("Converting file..."):
            file_bytes = uploaded.getvalue()
            filename = uploaded.name.lower()

            if filename.endswith(".csv"):
                md = extract_text_from_csv(file_bytes)
                source_type = "CSV"

            elif filename.endswith((".xlsx", ".xls")):
                md = extract_text_from_excel(file_bytes)
                source_type = "Excel"

            elif filename.endswith(".pdf"):
                md = pdf_to_markdown_from_bytes(file_bytes)
                source_type = "PDF (Docling)"

            else:
                raise ValueError("Unsupported file type.")

        st.success(f"Converted: **{uploaded.name}** ({source_type})")

        # Download button
        st.download_button(
            label="⬇ Download Markdown",
            data=md,
            file_name=uploaded.name.rsplit(".", 1)[0] + ".md",
            mime="text/markdown"
        )

        st.divider()

        # ============================================
        # Markdown Source (Scrollable + Highlighted)
        # ============================================

        st.subheader("Markdown Output")

        source_container = st.container(height=400, border=True)
        with source_container:
            st.code(md, language="markdown")

        st.divider()

        # ============================================
        # Rendered Preview (Scrollable)
        # ============================================

        st.subheader("Live Markdown Preview")

        preview_container = st.container(height=500, border=True)
        with preview_container:
            st.markdown(md)

    except Exception as e:
        st.error("Could not process file.")
        st.code(str(e), language="text")

else:
    st.info("Upload a file to begin conversion.")