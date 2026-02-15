import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestRegressor
import joblib
from pathlib import Path

class CyclePredictor:
    def __init__(self, model_dir='ml_models/saved_models'):
        self.model_dir = Path(model_dir)
        self.model_dir.mkdir(exist_ok=True, parents=True)
        self.model_file = self.model_dir / 'cycle_predictor.pkl'
        
        self.model = None
        self.avg_cycle = 28
        self.load_model()
    
    def load_model(self):
        """Load trained model if exists"""
        if self.model_file.exists():
            self.model = joblib.load(self.model_file)
    
    def save_model(self):
        """Save trained model"""
        joblib.dump(self.model, self.model_file)
    
    def train(self, df):
        """Train cycle prediction model"""
        # Get period start dates
        period_starts = df[df['period_start'] == True]['date'].tolist()
        
        if len(period_starts) < 3:
            self.avg_cycle = 28
            return False
        
        # Calculate cycle lengths
        cycle_lengths = []
        for i in range(1, len(period_starts)):
            days = (period_starts[i] - period_starts[i-1]).days
            if 20 <= days <= 45:  # Filter unrealistic cycles
                cycle_lengths.append(days)
        
        if len(cycle_lengths) < 2:
            self.avg_cycle = 28
            return False
        
        self.avg_cycle = np.mean(cycle_lengths)
        
        # Prepare features for ML model
        X = []
        y = []
        
        for i in range(1, len(period_starts)):
            # Features: previous cycle lengths, month, year
            prev_cycles = cycle_lengths[:i] if i <= len(cycle_lengths) else cycle_lengths
            features = [
                np.mean(prev_cycles[-3:]) if len(prev_cycles) >= 3 else self.avg_cycle,
                np.std(prev_cycles[-3:]) if len(prev_cycles) >= 3 else 0,
                period_starts[i-1].month,
                period_starts[i-1].year
            ]
            X.append(features)
            y.append(cycle_lengths[i-1])
        
        if len(X) >= 2:
            self.model = RandomForestRegressor(n_estimators=50, max_depth=5)
            self.model.fit(X, y)
            self.save_model()
        
        return True
    
    def predict_next_period(self, df):
        """Predict next period start date"""
        if df.empty:
            return None
        
        # Get last period start
        period_starts = df[df['period_start'] == True]['date'].tolist()
        
        if not period_starts:
            return None
        
        last_period = period_starts[-1]
        
        # Use ML model if available and enough data
        if self.model is not None and len(period_starts) >= 3:
            # Get recent cycle lengths
            cycle_lengths = []
            for i in range(1, len(period_starts)):
                days = (period_starts[i] - period_starts[i-1]).days
                if 20 <= days <= 45:
                    cycle_lengths.append(days)
            
            if len(cycle_lengths) >= 3:
                features = [[
                    np.mean(cycle_lengths[-3:]),
                    np.std(cycle_lengths[-3:]),
                    last_period.month,
                    last_period.year
                ]]
                predicted_length = self.model.predict(features)[0]
                predicted_length = max(20, min(45, int(predicted_length)))  # Clamp to realistic range
                return last_period + timedelta(days=predicted_length)
        
        # Fallback to average cycle length
        return last_period + timedelta(days=int(self.avg_cycle))
    
    def get_cycle_regularity(self, df):
        """Calculate cycle regularity score"""
        period_starts = df[df['period_start'] == True]['date'].tolist()
        
        if len(period_starts) < 3:
            return 0.5  # Default medium regularity
        
        cycle_lengths = []
        for i in range(1, len(period_starts)):
            days = (period_starts[i] - period_starts[i-1]).days
            if 20 <= days <= 45:
                cycle_lengths.append(days)
        
        if len(cycle_lengths) < 2:
            return 0.5
        
        # Coefficient of variation (lower = more regular)
        cv = np.std(cycle_lengths) / np.mean(cycle_lengths)
        
        # Convert to 0-1 score (1 = perfectly regular)
        regularity = max(0, min(1, 1 - cv))
        return regularity