import pickle
from datetime import date, timedelta

import pandas as pd
import requests
import streamlit as st

# ---- Settings ---------------
CITIES = {
    "Pittsburgh": (40.44, -79.99),
    "New York": (40.71, -74.01),
    "Chicago": (41.88, -87.63),
    "Miami": (25.76, -80.19),
    "Los Angeles": (34.05, -118.24),
}
LOW_TEMP, HIGH_TEMP = 40, 100        # temperatures (F) the model learned from
LOW_PRECIP, HIGH_PRECIP = 0, 100     # precipitation probability (%) the model learned from
LOW_SALES, HIGH_SALES = 170, 215     # below LOW_SALES is slow, above HIGH_SALES is busy
URL = "https://api.open-meteo.com/v1/forecast"
# ------------------------------------------------------------------------

# Load the trained model
with open("model.pkl", "rb") as f:
    model = pickle.load(f)

st.set_page_config(page_title="Ice Cream Sales Predictor", page_icon="🍦")
st.title("🍦 Ice Cream Sales Predictor")
st.caption(
    "Pick a city and a date. The app gets the weather forecast "
    "(high temperature + precipitation probability) and predicts how many cones you will sell."
)

city = st.selectbox("City", list(CITIES))
selected_date = st.date_input(
    "Date",
    value=date.today() + timedelta(days=1),
    min_value=date.today(),
    max_value=date.today() + timedelta(days=16),    # forecast reaches ~16 days ahead
)

if st.button("Predict sales", type="primary"):
    # 1. Ask the weather API for the forecast
    latitude, longitude = CITIES[city]
    response = requests.get(
        URL,
        params={
            "latitude": latitude,
            "longitude": longitude,
            "daily": "temperature_2m_max,precipitation_probability_max",
            "temperature_unit": "fahrenheit",
            "timezone": "auto",
            "start_date": str(selected_date),
            "end_date": str(selected_date),
        },
        timeout=30,
    )
    response.raise_for_status()
    data = response.json()
    
    # --- NEW: Safely extract API data and prevent NaNs ---
    daily = data.get("daily")
    if not daily or not daily.get("temperature_2m_max"):
        st.error("⚠️ Weather forecast is not available for this date. Please pick an earlier date.")
        st.stop()

    temperature = daily["temperature_2m_max"][0]
    
    # Safely grab precipitation, fallback to 0 if missing
    precip_list = daily.get("precipitation_probability_max") or [None]
    precip_prob = precip_list[0]

    # Stop the app if temperature is null
    if temperature is None:
        st.error("⚠️ The weather API returned an empty temperature for this date. Try selecting a date closer to today.")
        st.stop()
        
    if precip_prob is None:
        precip_prob = 0
        st.caption("⚠️ Precipitation probability was not available; assuming 0 %.")

    # Ensure they are valid floats
    temperature = float(temperature)
    precip_prob = float(precip_prob)
    # -----------------------------------------------------

    # 2. Give the model the SAME two features it was trained on
    features = pd.DataFrame({
        "temperature": [temperature],
        "precip_prob": [precip_prob],
    })
    prediction = max(0, model.predict(features)[0])

    # 3. Show the result
    col1, col2, col3 = st.columns(3)
    col1.metric("Forecast high",        f"{temperature:.0f} °F")
    col2.metric("Precip probability",   f"{precip_prob:.0f} %")
    col3.metric("Predicted sales",      f"{prediction:.0f} cones")

    # 4. Caveats
    if temperature < LOW_TEMP or temperature > HIGH_TEMP:
        st.warning(
            f"Temperature is outside the range the model learned from "
            f"({LOW_TEMP}–{HIGH_TEMP} °F). Treat the number with caution."
        )
    if precip_prob < LOW_PRECIP or precip_prob > HIGH_PRECIP:
        st.warning(
            f"Precipitation probability is outside the model's training range "
            f"({LOW_PRECIP}–{HIGH_PRECIP} %)."
        )

    # 5. Business hint
    if prediction > HIGH_SALES:
        st.info("Busy day: make sure you are fully stocked.")
    elif prediction > LOW_SALES:
        st.info("A normal day is expected.")
    else:
        st.info("A slow day: consider a promotion, or order less.")
