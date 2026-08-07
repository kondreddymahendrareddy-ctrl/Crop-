import streamlit as st
from fpdf import FPDF
from utils.database import get_db_connection
import tempfile
import os

class PDF(FPDF):
    def header(self):
        self.set_font('helvetica', 'B', 15)
        self.cell(0, 10, 'Intelligent Crop Recommendation & Soil Diagnosis', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('helvetica', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()} - Disclaimer: Predictions are decision-support information, not professional agricultural advice.', 0, 0, 'C')

def generate_pdf_report(record, user):
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("helvetica", size=11)

    pdf.cell(0, 10, f"User: {user['full_name']} | Date: {record['created_at']}", ln=True)
    pdf.cell(0, 10, f"Location: {record['location']}", ln=True)
    pdf.ln(5)

    pdf.set_font("helvetica", 'B', 12)
    pdf.cell(0, 10, "1. Environmental & Soil Parameters", ln=True)
    pdf.set_font("helvetica", size=11)
    
    col_w = 95
    pdf.cell(col_w, 8, f"Nitrogen (N): {record['nitrogen']}", ln=0)
    pdf.cell(col_w, 8, f"Temperature: {record['temperature']} C", ln=1)
    pdf.cell(col_w, 8, f"Phosphorus (P): {record['phosphorus']}", ln=0)
    pdf.cell(col_w, 8, f"Humidity: {record['humidity']} %", ln=1)
    pdf.cell(col_w, 8, f"Potassium (K): {record['potassium']}", ln=0)
    pdf.cell(col_w, 8, f"Rainfall: {record['rainfall']} mm", ln=1)
    pdf.cell(col_w, 8, f"Soil pH: {record['ph']}", ln=1)
    pdf.ln(5)
    
    pdf.set_font("helvetica", 'B', 12)
    pdf.cell(0, 10, "2. Crop Recommendation", ln=True)
    pdf.set_font("helvetica", size=11)
    
    pdf.cell(0, 8, f"Recommended Crop: {str(record['recommended_crop']).capitalize()}", ln=True)
    if record['top_predictions']:
        pdf.cell(0, 8, f"Top Predictions: {record['top_predictions']}", ln=True)
    pdf.ln(5)

    pdf.set_font("helvetica", 'B', 12)
    pdf.cell(0, 10, "3. Soil Diagnosis & Guidance", ln=True)
    pdf.set_font("helvetica", size=11)
    
    if record['soil_diagnosis']:
        pdf.multi_cell(0, 8, f"Diagnosis: {record['soil_diagnosis']}")
    if record['warnings']:
        pdf.multi_cell(0, 8, f"Warnings:\n" + "\n".join(["- " + w for w in record['warnings'].split('|')]))
    if record['improvement_advice']:
        pdf.multi_cell(0, 8, f"Improvement Advice:\n" + "\n".join(["- " + a for a in record['improvement_advice'].split('|')]))
        
    temp_dir = tempfile.gettempdir()
    filepath = os.path.join(temp_dir, f"report_{record['id']}.pdf")
    pdf.output(filepath)
    return filepath

def render_reports(user):
    st.markdown("<h2 style='color: #2e7d32;'>Reports & Downloads 🖨️</h2>", unsafe_allow_html=True)
    
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM analysis_history WHERE user_id=? ORDER BY created_at DESC", (user['id'],))
    rows = c.fetchall()
    conn.close()
    
    if not rows:
        st.info("No analyses found. Please run a Crop Recommendation first.")
        return
        
    records = [dict(row) for row in rows]
    
    st.write("Select an analysis to download its detailed PDF report.")
    
    options = {f"Analysis ID {r['id']} on {r['created_at']} - {str(r['recommended_crop']).capitalize()}": r for r in records}
    selected_option = st.selectbox("Select Analysis Record", list(options.keys()))
    
    record = options[selected_option]
    
    if st.button("Generate PDF Report", type="primary"):
        with st.spinner("Generating PDF..."):
            try:
                pdf_path = generate_pdf_report(record, user)
                with open(pdf_path, "rb") as f:
                    pdf_bytes = f.read()
                st.download_button(
                    label="📥 Download PDF",
                    data=pdf_bytes,
                    file_name=f"Crop_Report_{record['id']}.pdf",
                    mime="application/pdf"
                )
                st.success("PDF generated successfully! Click the download button above.")
            except Exception as e:
                st.error(f"Failed to generate PDF: {e}")
