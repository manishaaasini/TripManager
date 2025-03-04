import pandas as pd
import numpy as np
from datetime import timedelta, datetime
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from statsmodels.tsa.arima.model import ARIMA
from sklearn.linear_model import LinearRegression
import warnings
import traceback
from sklearn.metrics import mean_absolute_error, mean_squared_error

warnings.filterwarnings('ignore')

class VisitorPredictor:
    def __init__(self):
        # Define peak seasons and seasonal factors
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
        
        # Scaling factors to convert normalized predictions into actual visitor counts.
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
        
        self.model_hw = None          # Holt-Winters model
        self.calibration_model = None # Linear regression calibration
        self.model_arima = None       # Alternative ARIMA model

        # Define holidays for 2025 (using dd-mm-YYYY format)
        self.holidays = [
            datetime.strptime("01-01-2025", "%d-%m-%Y").date(),
            datetime.strptime("26-01-2025", "%d-%m-%Y").date(),
            datetime.strptime("26-02-2025", "%d-%m-%Y").date(),
            datetime.strptime("20-03-2025", "%d-%m-%Y").date(),
            datetime.strptime("31-03-2025", "%d-%m-%Y").date(),
            datetime.strptime("10-04-2025", "%d-%m-%Y").date(),
            datetime.strptime("12-05-2025", "%d-%m-%Y").date(),
            datetime.strptime("07-06-2025", "%d-%m-%Y").date(),
            datetime.strptime("06-07-2025", "%d-%m-%Y").date(),
            datetime.strptime("15-08-2025", "%d-%m-%Y").date(),
            datetime.strptime("16-08-2025", "%d-%m-%Y").date(),
            datetime.strptime("02-10-2025", "%d-%m-%Y").date(),
            datetime.strptime("28-10-2025", "%d-%m-%Y").date(),
            datetime.strptime("20-10-2025", "%d-%m-%Y").date(),
            datetime.strptime("05-11-2025", "%d-%m-%Y").date(),
            datetime.strptime("25-12-2025", "%d-%m-%Y").date()
        ]
        # Holiday adjustment factor (e.g., 1.2 means 20% more visitors on a holiday)
        self.holiday_factor = 1.2

    def is_holiday(self, forecast_date):
        """Check if the forecast date falls on a holiday."""
        return forecast_date.date() in self.holidays

    def load_data(self, filename, place_name):
        df = pd.read_csv(filename)
        if 'Week' not in df.columns:
            raise ValueError("Date column 'Week' not found in the CSV.")
        if place_name not in df.columns:
            raise ValueError(f"Could not find data for '{place_name}'. Available places: {df.columns.tolist()[1:]}")
        
        df['Week'] = pd.to_datetime(df['Week'], format='%d-%m-%Y', errors='coerce')
        df = df.sort_values('Week')
        df[place_name] = pd.to_numeric(df[place_name], errors='coerce')
        df = df.dropna().reset_index(drop=True)
        return df

    def train_hw_model(self, series):
        """Train Holt-Winters exponential smoothing model on the given series."""
        try:
            if len(series) < 12:
                raise ValueError("Insufficient data points for seasonal modeling. Provide at least 12 data points.")
            self.model_hw = ExponentialSmoothing(
                series,
                seasonal_periods=4,
                trend='add',
                seasonal='add',
                damped_trend=True
            ).fit()
        except Exception as e:
            print("Error in training Holt-Winters model:")
            print(traceback.format_exc())
            self.model_hw = None

    def calibrate_scaling(self, series):
        """
        Calibrate the relationship between the model's fitted values and actual visitor counts.
        We use linear regression: actual = intercept + slope * fitted.
        """
        if self.model_hw is None:
            raise ValueError("Holt-Winters model not trained.")
        fitted = self.model_hw.fittedvalues.values.reshape(-1, 1)
        actual = series.values.reshape(-1, 1)
        reg = LinearRegression()
        reg.fit(fitted, actual)
        self.calibration_model = reg
        print(f"Calibration model: Intercept = {reg.intercept_[0]:.4f}, Slope = {reg.coef_[0][0]:.4f}")

    def get_multi_year_average(self, df, forecast_date, place_name):
        """
        For the given forecast_date, compute the average Google Trends value for that same day-month
        across previous years (e.g., for 09-02-2025, use data from 09-02 of past years).
        """
        md = forecast_date.strftime("%d-%m")
        df["month_day"] = df["Week"].dt.strftime("%d-%m")
        hist = df[(df["month_day"] == md) & (df["Week"].dt.year < forecast_date.year)]
        if hist.empty:
            return None
        return hist[place_name].mean()

    def format_count(self, count):
        """Format visitor counts into thousands (K) or lakhs (L)."""
        if count < 1000:
            return f"{count}"
        elif count < 100000:
            return f"{count/1000:.1f}K"
        else:
            return f"{count/100000:.2f}L"

    def predict_future(self, filename, place_name, forecast_start_date_str, steps=4):
        """
        Generate forecasts for upcoming 'steps' weeks starting from forecast_start_date_str.
        Uses Holt-Winters with calibration and ARIMA as alternatives.
        For each forecast date, look up historical averages (same day-month over previous years)
        and blend them with the model forecast. Then convert the normalized forecast into actual 
        visitor counts using the scaling factor.
        Additionally, if the forecast date is a holiday, the predicted visitor count is increased
        by a holiday factor.
        """
        df = self.load_data(filename, place_name)
        series = df.set_index('Week')[place_name]
        
        # Train and calibrate Holt-Winters model.
        self.train_hw_model(series)
        if self.model_hw is None:
            raise ValueError("Holt-Winters model training failed.")
        self.calibrate_scaling(series)
        
        scaling_factor = self.scaling_factors.get(place_name, 500)
        forecast_start_date = pd.to_datetime(forecast_start_date_str, format='%d-%m-%Y')
        
        # Generate Holt-Winters forecasts.
        raw_forecast = self.model_hw.forecast(steps)
        hw_predictions = []
        for i, raw in enumerate(raw_forecast):
            predicted_week = forecast_start_date + timedelta(weeks=i)
            current_season = self.peak_seasons.get(predicted_week.month, 'regular')
            seasonal_factor = self.seasonal_factors[current_season]
            raw_adj = raw / seasonal_factor
            calibrated = self.calibration_model.predict(np.array([[raw_adj]]))[0][0]
            hist_avg = self.get_multi_year_average(df, predicted_week, place_name)
            if hist_avg is not None:
                final_forecast = (calibrated + hist_avg) / 2
            else:
                final_forecast = calibrated
            # Convert the normalized final forecast into actual visitor count.
            predicted_visitors = int(round(final_forecast * scaling_factor / 100))
            # If the forecast date is a holiday, apply the holiday factor.
            if self.is_holiday(predicted_week):
                predicted_visitors = int(round(predicted_visitors * self.holiday_factor))
            ci = {'lower': max(0, int(round(predicted_visitors * 0.8))),
                  'upper': int(round(predicted_visitors * 1.2))}
            hw_predictions.append({
                'predicted_week': predicted_week.strftime("%d-%m-%Y"),
                'predicted_visitors': predicted_visitors,
                'confidence_interval': ci,
                'historical_avg': hist_avg
            })
        
        # Generate ARIMA forecasts.
        self.model_arima = ARIMA(series, order=(1,1,0)).fit()
        arima_forecast = self.model_arima.forecast(steps)
        arima_predictions = []
        for i, fc in enumerate(arima_forecast):
            predicted_week = forecast_start_date + timedelta(weeks=i)
            hist_avg = self.get_multi_year_average(df, predicted_week, place_name)
            if hist_avg is not None:
                final_fc = (fc + hist_avg) / 2
            else:
                final_fc = fc
            predicted_visitors = int(round(final_fc * scaling_factor / 100))
            if self.is_holiday(predicted_week):
                predicted_visitors = int(round(predicted_visitors * self.holiday_factor))
            arima_predictions.append({
                'predicted_week': predicted_week.strftime("%d-%m-%Y"),
                'predicted_visitors': predicted_visitors,
                'historical_avg': hist_avg
            })
        
        return {
            'hw_predictions': hw_predictions,
            'arima_predictions': arima_predictions
        }

def main():
    predictor = VisitorPredictor()
    place_name = input("Enter the location name: ")
    forecast_start_date = input("Enter the forecast start date (dd-mm-YYYY): ")
    filename = "Google_Trends_past_5.csv"
    
    future_preds = predictor.predict_future(filename, place_name, forecast_start_date, steps=4)
    
    print(f"\nFuture Forecasts for {place_name} starting from {forecast_start_date}:")
    
    print("\nHolt-Winters Forecast (with multi-year historical & holiday adjustment):")
    for pred in future_preds['hw_predictions']:
        formatted_visitors = predictor.format_count(pred['predicted_visitors'])
        print(f"Week: {pred['predicted_week']}, Predicted Visitors: {formatted_visitors}", end="")
        if pred['historical_avg'] is not None:
            print(f" (Historical Avg: {pred['historical_avg']:.2f})", end="")
        print(f"\nConfidence Interval: {predictor.format_count(pred['confidence_interval']['lower'])} - {predictor.format_count(pred['confidence_interval']['upper'])}")
    
    print("\nARIMA Forecast (with multi-year historical & holiday adjustment):")
    for pred in future_preds['arima_predictions']:
        formatted_visitors = predictor.format_count(pred['predicted_visitors'])
        print(f"Week: {pred['predicted_week']}, Predicted Visitors: {formatted_visitors}", end="")
        if pred['historical_avg'] is not None:
            print(f" (Historical Avg: {pred['historical_avg']:.2f})", end="")
        print("")
    
if __name__ == "__main__":
    main()
