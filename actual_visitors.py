import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from statsmodels.tsa.holtwinters import ExponentialSmoothing
import warnings
import traceback
warnings.filterwarnings('ignore')

class VisitorPredictor:
    def __init__(self):
        self.peak_seasons = {
            11: 'winter_peak', 12: 'winter_peak', 1: 'winter_peak',
            6: 'summer_peak', 7: 'summer_peak',
            8: 'monsoon', 9: 'monsoon',
            3: 'spring', 4: 'spring',
            5: 'pre_summer', 10: 'autumn'
        }
        
        self.seasonal_factors = {
            'winter_peak': 1.2,
            'summer_peak': 0.9,
            'monsoon': 0.8,
            'spring': 1.1,
            'pre_summer': 1.05,
            'autumn': 1.0,
            'regular': 1.0
        }
        
        self.scaling_factors = {
            "Taj Mahal": 145000,
            "Red Fort": 50000,
            "Jaipur": 70000,
            "Varanasi": 80000,
            "Goa": 60000,
            "Kerala": 75000,
            "Munnar": 45000,
            "Hyderabad": 90000,
            "Coorg": 40000,
            "Golden Temple": 100000,
            "Maha Kumbh": 3000000,
            "Manali": 85000,
            "Shimla": 90000,
            "Darjeeling": 75000,
            "Ooty": 70000,
            "Leh-Ladakh": 60000,
            "Nainital": 80000,
            "Gulmarg": 50000,
            "Hampi": 55000,
            "Ajanta & Ellora Caves": 70000,
            "Khajuraho": 50000,
            "Jaisalmer": 60000,
            "Amer Fort": 75000,
            "Mysore Palace": 80000,
            "Konark Sun Temple": 65000,
            "Rameswaram": 85000,
            "Vaishno Devi": 100000,
            "Tirupati": 150000,
            "Somnath Temple": 70000,
            "Dwarka": 60000,
            "Puri Jagannath Temple": 120000,
            "Ujjain Mahakaleshwar Temple": 95000,
            "Andaman & Nicobar Islands": 50000,
            "Lakshadweep": 30000,
            "Gokarna": 45000,
            "Pondicherry": 60000
        }
        
        self.maha_kumbh_years = [2001, 2013, 2025, 2037, 2049]
        self.model = None
        
    def load_and_predict(self, filename, place_name):
        try:
            df = pd.read_csv(filename)
            
            if 'Week' not in df.columns:
                raise ValueError("Date column 'Week' not found in the CSV.")
            
            if place_name not in df.columns:
                raise ValueError(f"Could not find data for '{place_name}'. Available places: {df.columns.tolist()[1:]}")

            df['Week'] = pd.to_datetime(df['Week'], format='%d-%m-%Y', errors='coerce')
            df = df.sort_values('Week')
            
            df[place_name] = pd.to_numeric(df[place_name], errors='coerce')
            df = df.dropna()
            
            if len(df) < 12:
                raise ValueError(f"Not enough valid data points. Found only {len(df)} valid rows after processing.")
            
            self._train_prediction_model(df.set_index('Week')[place_name])
            
            return self.predict_visitors(place_name, df['Week'].max())
            
        except Exception as e:
            print("Error encountered:")
            print(traceback.format_exc())
            return None
        
    def _train_prediction_model(self, values):
        try:
            if len(values) < 12:
                raise ValueError("Insufficient data points for seasonal modeling. Provide at least 12 data points.")
            
            self.model = ExponentialSmoothing(
                values,
                seasonal_periods=4,
                trend='add',
                seasonal='add',
                damped_trend=True
            ).fit()
        except Exception as e:
            print("Error in training model:")
            print(traceback.format_exc())
            self.model = None
        
    def predict_visitors(self, place_name, last_date):
        try:
            if self.model is None:
                raise ValueError("Model has not been trained successfully.")
            
            predicted_values = self.model.forecast(4)
            
            if len(predicted_values) == 0:
                raise ValueError("Forecasting returned an empty result.")
            
            predictions = []
            for i, pred_gtrends in enumerate(predicted_values):
                pred_gtrends = max(0, pred_gtrends)
                predicted_week = last_date + timedelta(weeks=i+1)
                
                current_month = predicted_week.month
                current_year = predicted_week.year
                current_season = self.peak_seasons.get(current_month, 'regular')
                seasonal_factor = self.seasonal_factors[current_season]
                adjusted_ratio = 1.0 * seasonal_factor
                
                scaling_factor = self.scaling_factors.get(place_name, 500)
                
                if place_name == "Maha Kumbh" and current_year not in self.maha_kumbh_years:
                    predicted_visitors_actual = 0
                else:
                    predicted_visitors_normalized = pred_gtrends / adjusted_ratio
                    predicted_visitors_actual = predicted_visitors_normalized * scaling_factor / 100
                
                confidence_interval = {
                    'lower': max(0, predicted_visitors_actual * 0.8),
                    'upper': predicted_visitors_actual * 1.2
                }
                
                predictions.append({
                    'predicted_week': predicted_week.strftime("%d-%m-%Y"),
                    'predicted_gtrends': pred_gtrends,
                    'predicted_visitors_actual': int(predicted_visitors_actual),
                    'confidence_interval': confidence_interval
                })
            
            return predictions
        
        except Exception as e:
            print("Error in forecasting:")
            print(traceback.format_exc())
            return None

def main():
    predictor = VisitorPredictor()
    place_name = input("Enter the location name: ")
    filename = "Google_Trends_past_5.csv"
    
    predictions = predictor.load_and_predict(filename, place_name)
    
    if predictions:
        print(f"\nPrediction Results for {place_name}:")
        for pred in predictions:
            print(f"Week: {pred['predicted_week']}, Predicted Visitors: {pred['predicted_visitors_actual']:,}")
            print(f"Confidence Interval: {int(pred['confidence_interval']['lower']):,} - "
                  f"{int(pred['confidence_interval']['upper']):,} visitors\n")

if __name__ == "__main__":
    main()
