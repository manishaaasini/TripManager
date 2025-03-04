🌍 Tourist Package Recommender

Welcome to the Tourist Package Recommender — a smart recommendation system that helps travelers find the best tour packages based on their preferences! ✈️🏖️🏞️

🔎 Overview

This project scrapes tour package details from the web, processes the data into a structured format, and provides personalized package recommendations using Streamlit.

📚 Project Structure

Tourist Package Recommender/

├── recommendation_system.py   # Streamlit-based recommendation logic

├── tourism_recommendation.py  # Backend logic for recommendations

├── scraper.py                 # Scrapes tour package details

├── formater.py                # Converts raw data into JSON format

├── tour_packages.json         # Stores structured package details

🔄 Workflow

🔍 Scraping Data: scraper.py collects raw data from various sources.

📏 Formatting Data: formater.py processes and converts raw data into a structured JSON format.

💡 Recommendation Logic: tourism_recommendation.py filters and recommends packages.

📱 User Interface: recommendation_system.py provides an interactive UI using Streamlit.

