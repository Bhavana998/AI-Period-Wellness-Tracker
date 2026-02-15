import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import joblib
from pathlib import Path

class PainPredictor:
    def __init__(self, model_dir='ml_models/saved_models'):
        self.model_dir = Path(model_dir)
        self.model_dir.mkdir(exist_ok=True, parents=True)
        self.model_file = self.model_dir / 'pain_predictor.pkl'
        self.scaler_file = self.model_dir / 'pain_scaler.pkl'
        
        self.model = None
        self.scaler = StandardScaler()
        self.load_model()
    
    def load_model(self):
        """Load trained model if exists"""
        if self.model_file.exists():
            self.model = joblib.load(self.model_file)
        if self.scaler_file.exists():
            self.scaler = joblib.load(self.scaler_file)
    
    def save_model(self):
        """Save trained model"""
        joblib.dump(self.model, self.model_file)
        joblib.dump(self.scaler, self.scaler_file)
    
    def prepare_features(self, df):
        """Prepare features for training/prediction"""
        features = pd.DataFrame()
        
        # Basic features
        features['sleep_hours'] = df['sleep_hours']
        features['stress_level'] = df['stress_level']
        features['exercise_minutes'] = df['exercise_minutes']
        
        # Time-based features
        df['date'] = pd.to_datetime(df['date'])
        features['day_of_month'] = df['date'].dt.day
        features['month'] = df['date'].dt.month
        
        # Cycle-based features (if available)
        if 'cycle_day' in df.columns:
            features['cycle_day'] = df['cycle_day']
            # Sin/cos encoding of cycle day
            features['cycle_day_sin'] = np.sin(2 * np.pi * df['cycle_day'] / 28)
            features['cycle_day_cos'] = np.cos(2 * np.pi * df['cycle_day'] / 28)
        
        # Rolling averages
        features['pain_rolling_3d'] = df['pain_level'].rolling(3, min_periods=1).mean()
        features['pain_rolling_7d'] = df['pain_level'].rolling(7, min_periods=1).mean()
        
        # Sleep quality encoding
       