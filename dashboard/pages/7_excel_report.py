import streamlit as st

from reports.excel_report import generate_excel_report



st.title("📊 Excel Report Generator")

st.markdown(
    """
    Generate and download the latest
    Executive Excel Report.
    """
)

if st.button("Generate Excel Report"):

    file_path = generate_excel_report()

    st.success("Excel Report Generated Successfully")

    with open(file_path, "rb") as file:

        st.download_button(
            label="📥 Download Excel Report",
            data=file,
            file_name="executive_report.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
