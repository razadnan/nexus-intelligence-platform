import streamlit as st
import os

from reports.excel_report import generate_excel_report
from reports.pdf_report import generate_pdf_report

st.set_page_config(
    page_title="Reports Center",
    layout="wide"
)

st.title("📄 Reports Center")

if st.button("Generate Excel Report"):

    file = generate_excel_report()

    st.success(
        f"Generated: {file}"
    )

if st.button("Generate PDF Report"):

    file = generate_pdf_report()

    st.success(
        f"Generated: {file}"
    )

if os.path.exists(
    "exports/executive_report.xlsx"
):

    with open(
        "exports/executive_report.xlsx",
        "rb"
    ) as f:

        st.download_button(
            "Download Excel",
            f,
            file_name="executive_report.xlsx"
        )

if os.path.exists(
    "exports/executive_report.pdf"
):

    with open(
        "exports/executive_report.pdf",
        "rb"
    ) as f:

        st.download_button(
            "Download PDF",
            f,
            file_name="executive_report.pdf"
        )
