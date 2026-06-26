import streamlit as st

from reports.pdf_report import generate_pdf_report



st.title("📄 PDF Report Generator")

st.markdown(
    """
    Generate and download the latest
    Executive PDF Report.
    """
)

if st.button("Generate PDF Report"):

    file_path = generate_pdf_report()

    st.success("PDF Report Generated Successfully")

    with open(file_path, "rb") as file:

        st.download_button(
            label="📥 Download PDF Report",
            data=file,
            file_name="executive_report.pdf",
            mime="application/pdf"
        )
