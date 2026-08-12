import streamlit as st
import joblib
import pandas as pd
import os
from modules.weather_service import get_weather_data, get_location_suggestions, get_weather_by_ip
from utils.database import get_db_connection
from modules.soil_diagnosis import get_diagnosis_strings_for_db


def load_crop_model():
    model_path = "models/crop_model.pkl"
    if os.path.exists(model_path):
        return joblib.load(model_path)
    return None


def save_analysis_history(user_id, data, top_3, selected_crop, diag_str=None, warn_str=None, adv_str=None):
    conn = get_db_connection()
    c = conn.cursor()
    try:
        top_preds_str = ", ".join([f"{crop} ({prob*100:.1f}%)" for crop, prob in top_3])
        c.execute("""
            INSERT INTO analysis_history
            (user_id, location, nitrogen, phosphorus, potassium, ph,
             temperature, humidity, rainfall,
             recommended_crop, prediction_confidence, top_predictions,
             soil_diagnosis, warnings, improvement_advice)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id, data["location"], data["N"], data["P"], data["K"], data["ph"],
            data["temperature"], data["humidity"], data["rainfall"],
            selected_crop, top_3[0][1], top_preds_str,
            diag_str, warn_str, adv_str
        ))
        conn.commit()
    except Exception as e:
        st.error(f"Error saving analysis: {e}")
    finally:
        conn.close()


def _render_weather_card(weather: dict):
    desc = weather.get("weather_description", "N/A")
    t = weather.get("temperature", "--")
    h = weather.get("humidity", "--")
    w = weather.get("wind_speed", "--")
    rain = weather.get("rainfall", "--")
    tmax = weather.get("temp_max", "--")
    tmin = weather.get("temp_min", "--")
    name = weather.get("resolved_name", "Unknown Location")
    ts = weather.get("timestamp", "")

    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #0d3b26 0%, #1b5e20 50%, #2e7d32 100%);
        border-radius: 16px; padding: 20px 24px; color: #fff; margin: 8px 0 16px 0;
        box-shadow: 0 4px 24px rgba(0,0,0,0.35);">
        <div style="font-size:1.1em; font-weight:600; margin-bottom:12px; color:#a5d6a7;">
            📍 {name}
        </div>
        <div style="font-size:3em; font-weight:700; line-height:1; margin-bottom:6px;">
            {t}°C
        </div>
        <div style="font-size:1em; color:#c8e6c9; margin-bottom:14px;">{desc}</div>
        <div style="display:flex; gap:24px; flex-wrap:wrap;">
            <div><span style="color:#a5d6a7;">💧 Humidity</span><br/><b>{h}%</b></div>
            <div><span style="color:#a5d6a7;">🌬️ Wind</span><br/><b>{w} km/h</b></div>
            <div><span style="color:#a5d6a7;">🌧️ Rainfall</span><br/><b>{rain} mm</b></div>
            <div><span style="color:#a5d6a7;">🌡️ Max/Min</span><br/><b>{tmax}° / {tmin}°</b></div>
        </div>
        <div style="font-size:0.75em; color:#81c784; margin-top:12px;">
            🕐 Last updated: {ts}
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_crop_recommendation(user):
    st.markdown(
        "<h2 style='color:#2e7d32;margin-bottom:4px;'>Crop Recommendation Engine</h2>"
        "<p style='color:#666;margin-top:0;'>Enter your location and soil parameters to get real-time AI-powered crop predictions.</p>",
        unsafe_allow_html=True
    )

    # ── Session state init ─────────────────────────────────────────────────
    for key, val in [("current_weather", None), ("weather_fetched", False),
                     ("location_query", ""), ("pred_result", None)]:
        if key not in st.session_state:
            st.session_state[key] = val

    model = load_crop_model()
    if model is None:
        st.error("❌ Model not found. Run `python ml/train_crop_model.py` first.")
        return

    # ── Layout ────────────────────────────────────────────────────────────
    left, right = st.columns([1, 1], gap="large")

    # ══════════════════════════════════════════════════════════════════════
    # LEFT COLUMN: Location + Weather
    # ══════════════════════════════════════════════════════════════════════
    with left:
        st.markdown("### 📡 Step 1 — Real-Time Weather")
        
        from streamlit_geolocation import streamlit_geolocation
        from modules.weather_service import get_weather_exact_coords
        
        c_live, c_or = st.columns([1.5, 1])
        with c_live:
            st.markdown("<div style='margin-bottom:-10px; font-size:14px; color:#555;'>📍 Exact GPS Location:</div>", unsafe_allow_html=True)
            location = streamlit_geolocation()
            
            if location and location.get('latitude') and location.get('longitude'):
                lat = location['latitude']
                lon = location['longitude']
                
                # Only fetch weather if this is a newly fetched coordinate
                if st.session_state.get("last_lat") != lat or st.session_state.get("last_lon") != lon:
                    with st.spinner("Fetching weather for exact GPS location..."):
                        ok, result = get_weather_exact_coords(lat, lon)
                        if ok:
                            st.session_state["current_weather"] = result
                            st.session_state["weather_fetched"] = True
                            st.session_state["location_query"] = result.get('resolved_name', 'Exact GPS Location')
                            st.session_state["last_lat"] = lat
                            st.session_state["last_lon"] = lon
                            st.rerun()
                        else:
                            st.error(result)
        
        st.caption("Or enter a **city name** (e.g. *Chennai*, *Madurai*):")

        loc_input = st.text_input(
            "🔍 Location",
            value=st.session_state["location_query"],
            placeholder="e.g. Chennai",
            label_visibility="collapsed"
        )

        c1, c2 = st.columns([3, 1])
        with c1:
            fetch = st.button("🌐 Search & Fetch Weather", use_container_width=True, type="primary")
        with c2:
            if st.button("🔄 Reset", use_container_width=True):
                st.session_state["current_weather"] = None
                st.session_state["weather_fetched"] = False
                st.session_state["location_query"] = ""
                st.rerun()

        if fetch:
            if not loc_input.strip():
                st.warning("⚠️ Please enter a location name first.")
            else:
                st.session_state["location_query"] = loc_input.strip()
                with st.spinner(f"Fetching real-time weather for **{loc_input.strip()}**…"):
                    ok, result = get_weather_data(loc_input.strip())
                if ok:
                    st.session_state["current_weather"] = result
                    st.session_state["weather_fetched"] = True
                else:
                    st.session_state["current_weather"] = None
                    st.session_state["weather_fetched"] = False
                    st.error(result)
                    suggestions = get_location_suggestions(loc_input.strip())
                    if suggestions:
                        st.markdown("**💡 Did you mean one of these?**")
                        for s in suggestions[:5]:
                            st.markdown(f"→ `{s['label']}`")
                st.rerun()

        weather = st.session_state["current_weather"]
        if weather:
            _render_weather_card(weather)
            if weather.get("rainfall", 0) == 0.0:
                st.caption(
                    "ℹ️ No precipitation today. The model uses seasonal averages — "
                    "you may want to adjust the Rainfall field in Step 2."
                )
        elif st.session_state["weather_fetched"] is False and st.session_state["location_query"]:
            pass  # error already shown
        else:
            st.info("🌐 Click 'Use Live Location' or enter a city name to auto-fill temperature & humidity.")

    # ══════════════════════════════════════════════════════════════════════
    # RIGHT COLUMN: Soil Parameters + Prediction
    # ══════════════════════════════════════════════════════════════════════
    with right:
        st.markdown("### 🧪 Step 2 — Soil Parameters")

        weather = st.session_state["current_weather"]
        default_temp = float(weather["temperature"]) if weather and weather.get("temperature") is not None else 25.0
        default_hum  = float(weather["humidity"])    if weather and weather.get("humidity")    is not None else 70.0
        # Estimate seasonal rainfall based on live humidity to provide a dynamic default
        default_rain = 100.0
        if weather and weather.get("humidity") is not None:
            hum_val = float(weather["humidity"])
            if hum_val > 85:
                default_rain = 220.0  # High humidity -> tropical/wet
            elif hum_val > 70:
                default_rain = 150.0  # Moderate-high humidity
            elif hum_val > 50:
                default_rain = 100.0  # Average
            else:
                default_rain = 60.0   # Low humidity -> dry/arid

        with st.form("crop_form", clear_on_submit=False):
            s1, s2 = st.columns(2)
            with s1:
                n = st.number_input("Nitrogen — N (kg/ha)",   value=50, min_value=0, max_value=300,
                                    help="Nitrogen content in your soil sample.")
                p = st.number_input("Phosphorus — P (kg/ha)", value=50, min_value=0, max_value=300,
                                    help="Phosphorus content in your soil sample.")
            with s2:
                k  = st.number_input("Potassium — K (kg/ha)", value=50, min_value=0, max_value=300,
                                     help="Potassium content in your soil sample.")
                ph = st.number_input("Soil pH",               value=6.5, min_value=0.0, max_value=14.0, step=0.1,
                                     help="0=very acidic · 7=neutral · 14=very alkaline")

            st.markdown("---")
            st.markdown("**🌦️ Environmental Parameters** *(auto-filled from weather — you may adjust)*")

            e1, e2, e3 = st.columns(3)
            with e1:
                temp = st.number_input("Temperature (°C)", value=default_temp, format="%.1f")
            with e2:
                hum  = st.number_input("Humidity (%)", min_value=0.0, max_value=100.0,
                                       value=default_hum, format="%.1f")
            with e3:
                rain = st.number_input("Rainfall (mm)\nSeasonal avg", min_value=0.0, max_value=500.0,
                                       value=default_rain, format="%.1f",
                                       help="Enter seasonal/annual average. Today's reading is a fallback.")

            submitted = st.form_submit_button("🚀 Predict Best Crop", type="primary", use_container_width=True)

        # ── Prediction ───────────────────────────────────────────────────
        if submitted:
            if n < 0 or p < 0 or k < 0 or ph < 0:
                st.session_state["pred_result"] = None
                st.error("🚫 **Invalid Input:** Soil parameters (Nitrogen, Phosphorus, Potassium, and pH) cannot be negative. Please enter positive values.")
            else:
                input_df = pd.DataFrame({
                    "N": [n], "P": [p], "K": [k],
                    "temperature": [temp], "humidity": [hum], "ph": [ph], "rainfall": [rain]
                })

                with st.spinner("🤖 Running ML model…"):
                    if hasattr(model, "predict_proba"):
                        proba = model.predict_proba(input_df)[0]
                        classes = model.classes_
                        top_idx = proba.argsort()[-3:][::-1]
                        top_3 = [(classes[i], float(proba[i])) for i in top_idx]
                    else:
                        pred = model.predict(input_df)[0]
                        top_3 = [(pred, 1.0), ("—", 0.0), ("—", 0.0)]

                best_crop, best_prob = top_3[0]
                st.session_state["pred_result"] = top_3
                st.session_state["latest_crop"] = best_crop

                loc_label = weather["resolved_name"] if weather else (st.session_state["location_query"] or "Manual")
                db_data = {
                    "location": loc_label,
                    "N": n, "P": p, "K": k, "ph": ph,
                    "temperature": temp, "humidity": hum, "rainfall": rain
                }
                
                # Automatically generate diagnosis to save to DB for PDF reports
                diag_str, warn_str, adv_str = get_diagnosis_strings_for_db(db_data, best_crop)
                save_analysis_history(user["id"], db_data, top_3, best_crop, diag_str, warn_str, adv_str)
                st.session_state["latest_analysis"] = db_data
                st.rerun()

    # ── Prediction Results (full width) ──────────────────────────────────
    if st.session_state.get("pred_result"):
        top_3 = st.session_state["pred_result"]
        best_crop, best_prob = top_3[0]

        st.markdown("---")
        st.markdown(f"""
        <div style="background: rgba(10, 40, 25, 0.7); backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px);
                    border-radius:12px;padding:20px 28px;border-left:6px solid #69f0ae;margin-bottom:8px;box-shadow: 0 4px 15px rgba(0,0,0,0.5); border: 1px solid rgba(105,240,174,0.2); text-align: center;">
            <h2 style="color:#69f0ae !important;margin:0; text-shadow: 0 0 10px rgba(105,240,174,0.4);">🏆 Recommended Crop: <span style="color:#ffffff !important">{best_crop.capitalize()}</span></h2>
            <p style="color:#a5d6a7 !important;margin:4px 0 0 0;font-size:1.1em;">
                Model Confidence: <b>{best_prob*100:.1f}%</b>
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("#### 📊 Top 3 Crop Predictions")
        medals = ["🥇", "🥈", "🥉"]
        for i, (crop, prob) in enumerate(top_3):
            c1, c2 = st.columns([3, 1])
            with c1:
                st.progress(float(prob), text=f"{medals[i]} **{crop.capitalize()}**")
            with c2:
                st.metric("Confidence", f"{prob*100:.1f}%")

        st.success("✅ Analysis saved to History. Navigate to **Soil Analysis** for detailed diagnosis.")

        if st.button("🧪 Go to Soil Analysis →", type="primary"):
            st.session_state["current_page"] = "Soil Analysis"
            st.rerun()
