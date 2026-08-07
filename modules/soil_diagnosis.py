import streamlit as st
import joblib
import os
import plotly.graph_objects as go
from utils.database import get_db_connection

def load_reference_ranges():
    path = 'models/soil_reference_ranges.pkl'
    if os.path.exists(path):
        return joblib.load(path)
    return None

def analyze_parameter(value, ranges):
    low = ranges[0.25]
    high = ranges[0.75]
    if value < low:
        return "Low", f"Value {value} is below reference range ({low:.1f} - {high:.1f})"
    elif value > high:
        return "High", f"Value {value} is above reference range ({low:.1f} - {high:.1f})"
    else:
        return "Normal", f"Value {value} is within reference range ({low:.1f} - {high:.1f})"

def render_soil_diagnosis(user):
    st.markdown("<h2 style='color: #2e7d32;'>Soil Diagnostic Engine 🧪</h2>", unsafe_allow_html=True)
    
    if 'latest_analysis' not in st.session_state or not st.session_state['latest_analysis']:
        st.warning("No recent analysis found. Please use the Crop Recommendation engine first to generate a soil profile.")
        return
        
    data = st.session_state['latest_analysis']
    crop = st.session_state['latest_crop']
    
    st.markdown(f"### Diagnosis for **{crop.capitalize()}**")
    st.write("Comparing your soil profile against the dataset-derived interquartile ranges for the recommended crop.")
    
    ref_ranges = load_reference_ranges()
    if not ref_ranges or crop not in ref_ranges:
        st.error("Reference ranges not available for this crop.")
        return
        
    crop_refs = ref_ranges[crop]
    
    # Analyze
    n_status, n_msg = analyze_parameter(data['N'], crop_refs['N'])
    p_status, p_msg = analyze_parameter(data['P'], crop_refs['P'])
    k_status, k_msg = analyze_parameter(data['K'], crop_refs['K'])
    ph_status, ph_msg = analyze_parameter(data['ph'], crop_refs['ph'])
    
    # Warnings and Advice
    warnings = []
    advice = []
    
    # Helper function for dynamic, crop-specific advice
    def get_custom_advice(crop_name, param_name, status):
        crop_lower = crop_name.lower()
        legumes = ["chickpea", "kidneybeans", "lentil", "blackgram", "mungbean", "mothbeans", "pigeonpeas"]
        cereals = ["rice", "maize", "jute", "cotton"]
        fruits = ["apple", "mango", "orange", "grapes", "pomegranate", "banana", "papaya", "watermelon", "muskmelon"]
        
        if status == "Low":
            if param_name == "Nitrogen":
                if crop_lower in legumes:
                    return f"As a legume, {crop_lower} fixes its own nitrogen, but a small starter dose of Nitrogen is recommended to boost early root growth."
                elif crop_lower in cereals:
                    return f"Nitrogen is critical for the heavy vegetative growth of {crop_lower}. Consider applying Urea or Ammonium Sulfate in split doses."
                elif crop_lower in fruits:
                    return f"{crop_lower.capitalize()} needs adequate Nitrogen for a healthy canopy and fruit size. Apply N-rich organic compost or fertilizers."
                else:
                    return f"Nitrogen is low. Apply nitrogen-based fertilizers to support the leafy growth of {crop_lower}."
                    
            elif param_name == "Phosphorus":
                if crop_lower in legumes:
                    return f"Phosphorus is essential for root nodulation in {crop_lower}. Apply Super Phosphate before sowing."
                elif crop_lower in fruits:
                    return f"Phosphorus promotes strong flower formation and fruit set in {crop_lower}. Consider adding bone meal or DAP."
                else:
                    return f"Phosphorus is vital for root development. Apply P-rich fertilizers to help {crop_lower} establish strong roots."
                    
            elif param_name == "Potassium":
                if crop_lower in fruits:
                    return f"Potassium is crucial for the sugar content, color, and quality of {crop_lower}. Apply Muriate of Potash (MOP)."
                elif crop_lower in cereals:
                    return f"Potassium improves disease resistance and stalk strength in {crop_lower}. Ensure adequate K application."
                else:
                    return f"Potassium is low. Apply K-rich fertilizers to improve the stress tolerance of {crop_lower}."
                    
            elif param_name == "pH":
                return f"The soil is too acidic for {crop_lower}. Consider applying agricultural lime to raise the pH to optimal levels."
                
        elif status == "High":
            if param_name == "pH":
                return f"The soil is too alkaline for {crop_lower}. Consider adding elemental sulfur, peat moss, or organic matter to lower the pH."
            else:
                return f"{param_name} is too high for {crop_lower}. Avoid {param_name.lower()} application to prevent nutrient lockout and environmental runoff."
                
        else: # Normal
            if param_name == "Nitrogen":
                if crop_lower in legumes:
                    return f"Excellent! Nitrogen is perfectly optimized. Since {crop_lower} is a legume, it will naturally fix additional N in the soil."
                elif crop_lower in cereals:
                    return f"Excellent! Nitrogen is perfectly optimized to support the rapid vegetative and leafy growth required by {crop_lower}."
                elif crop_lower in fruits:
                    return f"Excellent! Nitrogen is perfectly optimized to support a healthy leaf canopy for your {crop_lower} trees."
                else:
                    return f"Excellent! The Nitrogen level is perfectly optimized for growing {crop_lower}."
            elif param_name == "Phosphorus":
                if crop_lower in legumes:
                    return f"Excellent! Phosphorus is perfectly optimized, which will ensure strong root nodulation for your {crop_lower}."
                elif crop_lower in fruits:
                    return f"Excellent! Phosphorus is perfectly optimized, which will maximize blooming and fruit yield for {crop_lower}."
                else:
                    return f"Excellent! The Phosphorus level is perfectly optimized for strong root development in {crop_lower}."
            elif param_name == "Potassium":
                if crop_lower in fruits:
                    return f"Excellent! Potassium is perfectly optimized, ensuring high sugar content, firmness, and excellent fruit quality for {crop_lower}."
                elif crop_lower in cereals:
                    return f"Excellent! Potassium is perfectly optimized, giving your {crop_lower} strong stalks and superior disease resistance."
                else:
                    return f"Excellent! The Potassium level is perfectly optimized for growing {crop_lower}."
            elif param_name == "pH":
                return f"Excellent! The soil pH is perfectly optimized, ensuring maximum nutrient availability for {crop_lower}."

    for status, param_name, short_name in [
        (n_status, "Nitrogen", "N"),
        (p_status, "Phosphorus", "P"),
        (k_status, "Potassium", "K"),
        (ph_status, "pH", "ph")
    ]:
        if status == "Low":
            warnings.append(f"⚠ {short_name} is below the optimal range for {crop.capitalize()}.")
        elif status == "High":
            warnings.append(f"⚠ {short_name} is above the optimal range for {crop.capitalize()}.")
            
        advice.append(get_custom_advice(crop, param_name, status))
            
    # Layout
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Nutrient Status")
        st.info(f"**Nitrogen (N):** {n_status}\n\n{n_msg}")
        st.info(f"**Phosphorus (P):** {p_status}\n\n{p_msg}")
        st.info(f"**Potassium (K):** {k_status}\n\n{k_msg}")
        st.info(f"**Soil pH:** {ph_status}\n\n{ph_msg}")
        
    with col2:
        st.subheader("Visualization (NPK)")
        
        categories = ['Nitrogen', 'Phosphorus', 'Potassium']
        user_values = [data['N'], data['P'], data['K']]
        ref_low = [crop_refs['N'][0.25], crop_refs['P'][0.25], crop_refs['K'][0.25]]
        ref_high = [crop_refs['N'][0.75], crop_refs['P'][0.75], crop_refs['K'][0.75]]
        
        fig = go.Figure()
        fig.add_trace(go.Bar(name='Your Soil', x=categories, y=user_values, marker_color='#4caf50'))
        fig.add_trace(go.Scatter(name='Reference Low', x=categories, y=ref_low, mode='lines+markers', line=dict(color='orange', dash='dash')))
        fig.add_trace(go.Scatter(name='Reference High', x=categories, y=ref_high, mode='lines+markers', line=dict(color='red', dash='dash')))
        
        fig.update_layout(title="Your Soil NPK vs Recommended Ranges", barmode='group')
        st.plotly_chart(fig, use_container_width=True)
        
    st.markdown("---")
    st.subheader("Warning System")
    if warnings:
        for w in warnings:
            st.warning(w)
    else:
        st.success("All parameters are within the recommended reference ranges!")
        
    st.subheader("Improvement Advice")
    for a in advice:
        st.write(f"- {a}")
        
    # Store these results in session for history update (which we will handle later if needed)
    # The prompt says: "Save User Analysis after each successful analysis". We saved it in Phase 8.
    # We could update the database record with these warnings, but we already created it. 
    # For now, this dynamic diagnosis is sufficient. We can update the row if we want.
    if st.button("Update Analysis Record with Diagnosis"):
        conn = get_db_connection()
        c = conn.cursor()
        try:
            diag_str = f"N:{n_status}, P:{p_status}, K:{k_status}, pH:{ph_status}"
            warn_str = "|".join(warnings)
            adv_str = "|".join(advice)
            
            c.execute('''
                UPDATE analysis_history 
                SET soil_diagnosis=?, warnings=?, improvement_advice=?
                WHERE id = (
                    SELECT id FROM analysis_history 
                    WHERE user_id=? AND recommended_crop=? 
                    ORDER BY created_at DESC LIMIT 1
                )
            ''', (diag_str, warn_str, adv_str, user['id'], crop))
            conn.commit()
            st.success("Analysis record updated successfully!")
        except Exception as e:
            st.error(f"Failed to update record: {e}")
        finally:
            conn.close()
