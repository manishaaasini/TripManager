import streamlit as st

# ✅ This must be the first Streamlit command
st.set_page_config(page_title="Tourism AI Suite", layout="wide")

# Import the three modules AFTER set_page_config
import arima1
import recommendation_system1
import seasonal1

# App title
st.title("🧳 Tourism AI Suite")

# Sidebar navigation
app_mode = st.sidebar.radio(
    "Choose a use case",
    [
        "Predicting Visitors Using ARIMA",
        "Tourist Package Recommender",
        "Seasonal Recommendation"
    ]
)

# Route to the correct module
if app_mode == "Predicting Visitors Using ARIMA":
    arima1.run()
elif app_mode == "Tourist Package Recommender":
    recommendation_system1.run()
elif app_mode == "Seasonal Recommendation":
    seasonal1.run()
