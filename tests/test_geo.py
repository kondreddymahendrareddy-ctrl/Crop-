import streamlit as st
from streamlit_geolocation import streamlit_geolocation

st.title("Geolocation Test")
location = streamlit_geolocation()

if location and location.get('latitude'):
    st.success(f"Lat: {location['latitude']}, Lon: {location['longitude']}")
    st.write(location)
else:
    st.info("Please click the location button")
