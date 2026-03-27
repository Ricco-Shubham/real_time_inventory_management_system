import streamlit as st
import os
from utils.insightsgenerator import DataInsightsReport

def render_insights():
    st.markdown("## 💡 Generate Insights Report")

    if not st.session_state.get('is_logged_in') or st.session_state.get('user_type') != "admin":
        st.warning("Unauthorized.")
        return

    st.markdown("""
    Click the button below to generate a comprehensive PDF insights report. 
    This report contains:
    - Total Sales & Revenue Overview (Charts)
    - Top 10 Selling Products
    - Product Category Distribution
    - Monthly Sales Trend
    - Top 5 Customers by Orders
    - Low Stock Alerts Database
    """)

    if st.button("📄 Generate Insights PDF", type="primary", use_container_width=True):
        with st.spinner("Generating Insights PDF... This translates live DB queries into High-res Charts."):
            try:
                DataInsightsReport().generate_pdf_report()
                
                # Locate the generated file
                base_dir = os.path.dirname(os.path.abspath(__file__))
                # go up from pages/admin/ to utils/ and then to Inventory_Insights
                # actually utils/insightsgenerator.py creates it relative to its own location
                pdf_path = os.path.join(base_dir, "..", "..", "Inventory_Insights", "Inventory_Insights_Report.pdf")
                pdf_path = os.path.normpath(pdf_path)

                if os.path.exists(pdf_path):
                    with open(pdf_path, "rb") as f:
                        pdf_bytes = f.read()
                    
                    st.success("Report generated successfully!")
                    st.download_button(
                        label="⬇️ Download Output PDF",
                        data=pdf_bytes,
                        file_name="Inventory_Insights_Report.pdf",
                        mime="application/pdf"
                    )
                else:
                    st.error("Error: PDF was generated but could not be located on disk.")
                    st.write("Expected Path:", pdf_path)
            except Exception as e:
                st.error(f"Failed to generate report: {e}")
