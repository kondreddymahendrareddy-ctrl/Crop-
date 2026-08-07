import streamlit as st
import pandas as pd
import joblib
import os

def load_fertilizer_model():
    model_path = 'models/fertilizer_model.pkl'
    encoder_path = 'models/fertilizer_encoders.pkl'
    if os.path.exists(model_path) and os.path.exists(encoder_path):
        return joblib.load(model_path), joblib.load(encoder_path)
    return None, None

def render_fertilizer_guidance(user):
    st.error("🚨 DEBUG MESSAGE: IF YOU CAN SEE THIS, THE NEW CODE IS RUNNING. PLEASE LET ME KNOW IF YOU SEE THIS!")
    st.markdown(
        "<h2 style='color:#2e7d32;margin-bottom:4px;'>💧 Fertilizer Recommendation Engine</h2>"
        "<p style='color:#666;margin-top:0;'>Get intelligent fertilizer recommendations based on soil health and crop type.</p>",
        unsafe_allow_html=True
    )
    
    model, encoders = load_fertilizer_model()
    
    if model is None or encoders is None:
        st.error("❌ Fertilizer Model not found. Please train the fertilizer model first.")
        return
        
    st.markdown("### Provide Soil & Environmental Details")
    
    # --- Real-Time Weather Section ---
    st.markdown("##### 📡 Optional: Auto-fill via Real-Time Weather")
    from streamlit_geolocation import streamlit_geolocation
    from modules.weather_service import get_weather_exact_coords, get_weather_data
    
    c_live, c_or = st.columns([1.5, 1])
    with c_live:
        st.markdown("<div style='margin-bottom:-10px; font-size:14px; color:#555;'>📍 Exact GPS Location:</div>", unsafe_allow_html=True)
        location = streamlit_geolocation()
        
        if location and location.get('latitude') and location.get('longitude'):
            lat = location['latitude']
            lon = location['longitude']
            if st.session_state.get("fert_last_lat") != lat or st.session_state.get("fert_last_lon") != lon:
                with st.spinner("Fetching weather for exact GPS location..."):
                    ok, result = get_weather_exact_coords(lat, lon)
                    if ok:
                        st.session_state["fert_weather"] = result
                        st.session_state["fert_loc_query"] = result.get('resolved_name', 'Exact GPS Location')
                        st.session_state["fert_last_lat"] = lat
                        st.session_state["fert_last_lon"] = lon
                        st.rerun()
                    else:
                        st.error(result)
                        
    st.caption("Or enter a **city name** (e.g. *Chennai*, *Madurai*):")
    
    loc_input = st.text_input("🔍 Location", value=st.session_state.get("fert_loc_query", ""), placeholder="e.g. Chennai", label_visibility="collapsed")
    
    c1, c2 = st.columns([3, 1])
    with c1:
        fetch = st.button("🌐 Search & Fetch Weather", use_container_width=True, type="primary")
    with c2:
        if st.button("🔄 Reset Weather", use_container_width=True):
            st.session_state["fert_weather"] = None
            st.session_state["fert_loc_query"] = ""
            st.rerun()

    if fetch:
        if not loc_input.strip():
            st.warning("⚠️ Please enter a location name first.")
        else:
            st.session_state["fert_loc_query"] = loc_input.strip()
            with st.spinner(f"Fetching real-time weather for **{loc_input.strip()}**…"):
                ok, result = get_weather_data(loc_input.strip())
                if ok:
                    st.session_state["fert_weather"] = result
                    st.rerun()
                else:
                    st.error(result)

    weather = st.session_state.get("fert_weather")
    if weather:
        st.success(f"🌦️ Weather updated for **{weather['resolved_name']}**")
        st.info(f"**Temp:** {weather['temperature']}°C | **Humidity:** {weather['humidity']}% | **Rainfall:** {weather['rainfall']}mm")
    
    st.markdown("---")
    
    # Pre-fill from latest crop analysis if available
    latest_analysis = st.session_state.get('latest_analysis', {})
    latest_crop = st.session_state.get('latest_crop', 'Wheat')
    
    default_n = int(latest_analysis.get('N', 50))
    default_p = int(latest_analysis.get('P', 50))
    default_k = int(latest_analysis.get('K', 50))
    default_temp = float(latest_analysis.get('temperature', 25.0))
    default_hum = float(latest_analysis.get('humidity', 70.0))
    
    if weather:
        default_temp = float(weather.get("temperature", default_temp))
        default_hum = float(weather.get("humidity", default_hum))
    
    with st.form("fertilizer_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Soil Nutrients & Properties**")
            n = st.number_input("Nitrogen (N)", value=default_n)
            p = st.number_input("Phosphorus (P)", value=default_p)
            k = st.number_input("Potassium (K)", value=default_k)
            soil_types = encoders['Soil Type'].classes_
            soil_type = st.selectbox("Soil Type", soil_types)
            
        with col2:
            st.markdown("**Environment & Crop**")
            temp = st.number_input("Temperature (°C)", value=default_temp)
            hum = st.number_input("Humidity (%)", min_value=0.0, max_value=100.0, value=default_hum)
            moisture = st.number_input("Soil Moisture (%)", min_value=0, max_value=100, value=40)
            crop_types = encoders['Crop Type'].classes_
            
            # Default to the predicted crop if it exists in the fertilizer dataset
            default_crop_idx = 0
            capitalized_crop = latest_crop.capitalize()
            if capitalized_crop in crop_types:
                default_crop_idx = list(crop_types).index(capitalized_crop)
            
            crop_type = st.selectbox("Crop Type", crop_types, index=default_crop_idx)
            
        submit = st.form_submit_button("🧪 Predict Fertilizer", type="primary", use_container_width=True)
        
        if submit:
            if n < 0 or p < 0 or k < 0 or temp < 0 or hum < 0 or moisture < 0:
                st.session_state["fert_prediction"] = None
                st.error("🚫 **Invalid Input:** Soil parameters and environmental metrics cannot be negative. Please enter valid positive values.")
            else:
                # Encode categorical features
                encoded_soil = encoders['Soil Type'].transform([soil_type])[0]
                encoded_crop = encoders['Crop Type'].transform([crop_type])[0]
                
                # Create DataFrame matching dataset structure:
                # Temparature,Humidity,Moisture,Soil Type,Crop Type,Nitrogen,Potassium,Phosphorous
                input_df = pd.DataFrame({
                    'Temparature': [int(temp)],
                    'Humidity': [int(hum)],
                    'Moisture': [int(moisture)],
                    'Soil Type': [encoded_soil],
                    'Crop Type': [encoded_crop],
                    'Nitrogen': [n],
                    'Potassium': [k],
                    'Phosphorous': [p]
                })
                
                with st.spinner("Analyzing soil and environment data..."):
                    prediction = model.predict(input_df)[0]
                    st.session_state["fert_prediction"] = prediction
                    
                    loc_label = st.session_state.get("location_query", "Manual")
                    db_data = {
                        "location": loc_label,
                        "N": n, "P": p, "K": k, "temperature": temp, "humidity": hum,
                        "soil_type": soil_type, "crop_type": crop_type
                    }
                    
                st.rerun()

    if st.session_state.get("fert_prediction"):
        st.markdown("---")
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#e1f5fe,#b3e5fc);
                    border-radius:12px;padding:20px 28px;border-left:6px solid #0288d1;margin-bottom:8px;">
            <h2 style="color:#01579b;margin:0;">🧪 Recommended Fertilizer: <span style="color:#0288d1">{st.session_state["fert_prediction"]}</span></h2>
            <p style="color:#0277bd;margin:4px 0 0 0;font-size:1.1em;">
                Based on your specific soil metrics and crop selection.
            </p>
        </div>
        """, unsafe_allow_html=True)
        st.success("Analysis complete! This recommendation replaces the previous rule-based heuristic.")
