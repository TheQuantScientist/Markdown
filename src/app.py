# /Users/admin/LG/Markdown/src/main.py
import os 
import sys

sys.path.append('.')

import streamlit as st
import pandas as pd
import io

from extraction.csv_to_markdown import extract_text_from_csv   # keep if you want fallback
from extraction.excel_to_markdown import extract_text_from_excel

# But we can also define simpler pandas-based versions if desired

st.set_page_config(page_title="File → Markdown", layout="wide")
st.title("File to Markdown Converter (Japanese support)")

uploaded = st.file_uploader("Upload CSV or Excel", type=["csv", "xlsx", "xls"])

if uploaded:
    try:
        bytes_data = uploaded.getvalue()
        name = uploaded.name.lower()

        if name.endswith(".csv"):
            md = extract_text_from_csv(bytes_data)
            source_type = "CSV"
        else:
            md = extract_text_from_excel(bytes_data)
            source_type = "Excel"

        st.success(f"Converted: **{uploaded.name}** ({source_type})")

        col1, col2 = st.columns([1, 1])

        with col1:
            st.subheader("Markdown")
            st.code(md, language="markdown")

        with col2:
            st.subheader("Preview")
            st.markdown(md)

    except Exception as e:
        st.error("Could not process file")
        st.code(str(e), language="text")