# 🍦 Ice Cream Sales Predictor

A Machine Learning web application built with **Streamlit** and **Scikit-Learn** that predicts daily ice cream sales based on the weather forecast. 

The app fetches real-time weather data (maximum daily temperature and precipitation probability) from the [Open-Meteo API](https://open-meteo.com/) and feeds it into a pre-trained Linear Regression model.

## 🚀 Features

- **City Selection:** Choose from 5 major US cities (Pittsburgh, New York, Chicago, Miami, Los Angeles).
- **16-Day Forecast:** Select any date within the next 16 days.
- **Live Weather Data:** Fetches real-time weather data using the Open-Meteo API.
- **Interactive UI:** Displays forecasted high temperature, precipitation probability, and predicted sales in a clean 3-column layout.
- **Business Insights:** Provides actionable advice based on the predicted sales (e.g., "Busy day: make sure you are fully stocked").
- **Data Validation:** Safely handles missing API data and warns the user if weather conditions fall outside the model's training range.

## 🧠 The Model

The app uses a `LinearRegression` model saved as `model.pkl`. 
- **Features (X):** `temperature` (Fahrenheit) and `precip_prob` (Precipitation Probability, 0–100%).
- **Target (y):** `sales` (Predicted number of ice cream cones sold).

*Note: The current `model.pkl` expects exactly these two features. If you replace the model, ensure your new model is trained on the same features and saved using `pickle`.*

## 📁 File Structure

```text
├── app.py               # The Streamlit application code
├── model.pkl            # The pre-trained Scikit-Learn Linear Regression model
├── requirements.txt     # Python dependencies
└── README.md            # Project documentation
