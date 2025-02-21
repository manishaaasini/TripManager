import streamlit as st
import pandas as pd
import numpy as np
from prophet import Prophet
import plotly.express as px
from datetime import datetime, timedelta

# Top Tourist Destinations with Seasonal Recommendations
DESTINATIONS = {
    'Winter (Dec-Feb)': [
        {'name': 'Rajasthan', 'reason': 'Mild weather, desert festivals'},
        {'name': 'Kerala', 'reason': 'Pleasant climate, backwater tours'},
        {'name': 'Goa', 'reason': 'Beach season, Christmas celebrations'}
    ],
    'Summer (Mar-May)': [
        {'name': 'Ladakh', 'reason': 'Accessible mountain routes'},
        {'name': 'Shimla', 'reason': 'Cool mountain retreat'},
        {'name': 'Northeast India', 'reason': 'Lush landscapes, moderate temperatures'}
    ],
    'Monsoon (Jun-Sep)': [
        {'name': 'Kerala', 'reason': 'Ayurveda, green landscapes'},
        {'name': 'Meghalaya', 'reason': 'Waterfalls, scenic beauty'},
        {'name': 'Goa', 'reason': 'Fewer tourists, lush scenery'}
    ],
    'Post-Monsoon (Oct-Nov)': [
        {'name': 'Rajasthan', 'reason': 'Pleasant weather, cultural festivals'},
        {'name': 'Hampi', 'reason': 'Archaeological sites, comfortable climate'},
        {'name': 'North India', 'reason': 'Festival season, mild temperatures'}
    ]
}

# Simulated Google Trends-like Data
TRENDS_DATA = {
    'Year': [2020, 2021, 2022, 2023, 2024],
    'Tourism_Interest': [30, 45, 65, 80, 90]
}

def get_seasonal_recommendations(current_month=None):
    """Determine seasonal recommendations based on current month"""
    if current_month is None:
        current_month = datetime.now().month
    
    # Define seasonal months
    seasons = {
        'Winter': [12, 1, 2],
        'Summer': [3, 4, 5],
        'Monsoon': [6, 7, 8, 9],
        'Post-Monsoon': [10, 11]
    }
    
    # Find current season
    current_season = next(
        (season for season, months in seasons.items() if current_month in months), 
        'Winter'
    )
    
    return DESTINATIONS.get(current_season + ' (Dec-Feb)' if current_season == 'Winter' else current_season + ' (Mar-May)' if current_season == 'Summer' else current_season + ' (Jun-Sep)' if current_season == 'Monsoon' else current_season + ' (Oct-Nov)', [])

def predict_tourism_trends():
    """Predict tourism trends using Prophet"""
    df = pd.DataFrame(TRENDS_DATA)
    df['ds'] = pd.to_datetime(df['Year'].astype(str) + '-07-01')
    df['y'] = df['Tourism_Interest']
    
    model = Prophet(yearly_seasonality=True)
    model.fit(df)
    
    future = model.make_future_dataframe(periods=5, freq='Y')
    forecast = model.predict(future)
    
    return forecast

def main():
    st.title("Tourism Prediction & Recommendations")
    
    # Set current date to 7th Jan 2025
    current_date = datetime(2025, 1, 7)
    
    # Predict next month's tourism trends
    forecast = predict_tourism_trends()
    next_month_prediction = forecast[forecast['ds'] > current_date]['yhat'].iloc[0]
    
    # Get seasonal recommendations
    recommendations = get_seasonal_recommendations(current_date.month)
    
    # Display predictions
    st.header("Tourism Trend Prediction")
    st.metric("Next Month Tourism Interest", f"{next_month_prediction:.2f}")
    
    # Display recommendations
    st.header("Seasonal Travel Recommendations")
    for dest in recommendations:
        st.write(f"🌍 **{dest['name']}**: {dest['reason']}")
    
    # Visualization of trends
    fig = px.line(
        forecast, 
        x='ds', 
        y=['yhat', 'yhat_lower', 'yhat_upper'],
        title='Tourism Interest Trend'
    )
    st.plotly_chart(fig)
    
    # Add recommendation note
    st.markdown("**Recommendation:** Consider these destinations for January 2025 travel plans.")

if __name__ == "__main__":
    main()