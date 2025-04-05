import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

DESTINATIONS = {
    'Winter (Dec-Feb)': [
        {'name': 'Rajasthan', 'reason': 'Mild weather, desert festivals'},
        {'name': 'Kerala', 'reason': 'Pleasant climate, backwater tours'},
        {'name': 'Goa', 'reason': 'Beach season, Christmas celebrations'},
        {'name': 'Kashmir', 'reason': 'Snowfall, winter sports'},
        {'name': 'Uttarakhand', 'reason': 'Adventure sports, cold weather'}
    ],
    'Summer (Mar-May)': [
        {'name': 'Ladakh', 'reason': 'Accessible mountain routes'},
        {'name': 'Shimla', 'reason': 'Cool mountain retreat'},
        {'name': 'Northeast India', 'reason': 'Lush landscapes, moderate temperatures'},
        {'name': 'Manali', 'reason': 'Adventure activities, mountain landscapes'},
        {'name': 'Darjeeling', 'reason': 'Tea gardens, cool weather'}
    ],
    'Monsoon (Jun-Sep)': [
        {'name': 'Kerala', 'reason': 'Ayurveda, green landscapes'},
        {'name': 'Meghalaya', 'reason': 'Waterfalls, scenic beauty'},
        {'name': 'Goa', 'reason': 'Fewer tourists, lush scenery'},
        {'name': 'Coorg', 'reason': 'Coffee plantations, lush greenery'},
        {'name': 'Konkan Coast', 'reason': 'Beaches and monsoon beauty'}
    ],
    'Post-Monsoon (Oct-Nov)': [
        {'name': 'Rajasthan', 'reason': 'Pleasant weather, cultural festivals'},
        {'name': 'Hampi', 'reason': 'Archaeological sites, comfortable climate'},
        {'name': 'North India', 'reason': 'Festival season, mild temperatures'},
        {'name': 'Varanasi', 'reason': 'Festivals, religious experiences'},
        {'name': 'Taj Mahal, Agra', 'reason': 'Cultural heritage, festivals'}
    ]
}

# Load the uploaded file to get the tourism data
file_path = 'tourism_data.csv'
tourism_data = pd.read_csv(file_path)

# Convert the 'Week' column to datetime
tourism_data['Week'] = pd.to_datetime(tourism_data['Week'], format='%d-%m-%Y')

# Extract month from the 'Week' column
tourism_data['Month'] = tourism_data['Week'].dt.month

def get_seasonal_recommendations(current_month=None):
    if current_month is None:
        current_month = datetime.now().month
    seasons = {
        'Winter': [12, 1, 2],
        'Summer': [3, 4, 5],
        'Monsoon': [6, 7, 8, 9],
        'Post-Monsoon': [10, 11]
    }
    current_season = next((season for season, months in seasons.items() if current_month in months), 'Winter')
    return DESTINATIONS.get(f"{current_season} (Dec-Feb)" if current_season == 'Winter' else
                            f"{current_season} (Mar-May)" if current_season == 'Summer' else
                            f"{current_season} (Jun-Sep)" if current_season == 'Monsoon' else
                            f"{current_season} (Oct-Nov)", [])

def predict_next_month_tourism():
    current_month = datetime.now().month
    latest_month_data = tourism_data[tourism_data['Month'] == current_month]
    next_month = (current_month % 12) + 1  # next month
    latest_month_avg = latest_month_data['Tourism in India'].mean()
    return latest_month_avg

def plot_tourism_trends():
    fig = px.line(tourism_data, x='Week', y='Tourism in India', title='Tourism Interest Over Time')
    fig.update_layout(xaxis_title='Week', yaxis_title='Tourism Interest')

    # Mark the predicted tourism interest as a red dot on the plot
    next_month_prediction = predict_next_month_tourism()
    prediction_date = datetime(datetime.now().year, (datetime.now().month % 12) + 1, 1)
    
    fig.add_trace(go.Scatter(
        x=[prediction_date],
        y=[next_month_prediction],
        mode='markers',
        marker=dict(color='red', size=12),
        name='Predicted Interest'
    ))

    return fig

def run():
    st.title("📅 Seasonal Tourism Insights")

    current_date = datetime(2025, 1, 7)
    next_month_prediction = predict_next_month_tourism()
    recommendations = get_seasonal_recommendations(current_date.month)

    st.header("📈 Tourism Trend Prediction")
    st.metric("Next Month Tourism Interest", f"{next_month_prediction:.2f}")

    st.header("🗺️ Seasonal Travel Recommendations")
    for dest in recommendations:
        st.write(f"🌍 **{dest['name']}**: {dest['reason']}")

    # Plot the tourism trends
    st.header("📊 Tourism Interest Trends")
    fig = plot_tourism_trends()
    st.plotly_chart(fig)

    st.markdown("**Recommendation:** Consider these destinations for your next month's travel plans.")
