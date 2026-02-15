import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import joblib
from pathlib import Path

class NutritionPredictor:
    def __init__(self, model_dir='ml_models/saved_models'):
        self.model_dir = Path(model_dir)
        self.model_dir.mkdir(exist_ok=True, parents=True)
        self.model_file = self.model_dir / 'nutrition_predictor.pkl'
        self.scaler_file = self.model_dir / 'nutrition_scaler.pkl'
        
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
    
    def prepare_features(self, df, food_df):
        """Prepare nutrition features for ML"""
        features = pd.DataFrame()
        
        # Merge data
        merged = pd.merge(df, food_df, on='date', how='left')
        
        # Nutrition features
        features['calories'] = merged['calories'].fillna(0)
        features['protein'] = merged['protein'].fillna(0)
        features['carbs'] = merged['carbs'].fillna(0)
        features['fat'] = merged['fat'].fillna(0)
        features['fiber'] = merged['fiber'].fillna(0)
        features['sugar'] = merged['sugar'].fillna(0)
        features['water_intake'] = merged['water_intake'].fillna(0)
        features['caffeine'] = merged['caffeine'].fillna(0)
        features['alcohol'] = merged['alcohol'].fillna(0)
        
        # Ratios (healthy indicators)
        features['protein_ratio'] = features['protein'] * 4 / features['calories'].replace(0, 1)
        features['fiber_ratio'] = features['fiber'] / features['carbs'].replace(0, 1)
        
        # Rolling averages (3-day nutrition patterns)
        for col in ['calories', 'protein', 'fiber', 'water_intake']:
            features[f'{col}_rolling_3d'] = features[col].rolling(3, min_periods=1).mean()
        
        return features.fillna(0)
    
    def train(self, df, food_df):
        """Train nutrition-pain correlation model"""
        if df.empty or food_df.empty or len(df) < 10:
            return False
        
        # Prepare features and target
        X = self.prepare_features(df, food_df)
        y = df['pain_level']
        
        # Remove rows with missing target
        valid_idx = ~y.isna()
        X = X[valid_idx]
        y = y[valid_idx]
        
        if len(X) < 10:
            return False
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train model
        self.model = RandomForestRegressor(
            n_estimators=50,
            max_depth=5,
            random_state=42
        )
        self.model.fit(X_scaled, y)
        
        # Save model
        self.save_model()
        return True
    
    def predict_pain_from_nutrition(self, nutrition_features):
        """Predict how nutrition affects pain"""
        if self.model is None:
            return None
        
        features_scaled = self.scaler.transform(nutrition_features)
        prediction = self.model.predict(features_scaled)
        return max(0, min(10, prediction[0]))
    
    def get_nutrition_insights(self, df, food_df):
        """Generate insights about nutrition and symptoms"""
        merged = pd.merge(df, food_df, on='date', how='inner')
        
        if merged.empty:
            return {}
        
        insights = {}
        
        # Correlation between nutrients and pain
        corr_cols = ['pain_level', 'calories', 'protein', 'fiber', 'sugar', 'water_intake', 'caffeine']
        available_cols = [col for col in corr_cols if col in merged.columns]
        
        if len(available_cols) > 1:
            corr_matrix = merged[available_cols].corr()
            insights['pain_correlations'] = corr_matrix['pain_level'].drop('pain_level').to_dict()
        
        # Optimal nutrition levels for low pain days
        low_pain_days = merged[merged['pain_level'] <= 3]
        if not low_pain_days.empty:
            insights['optimal_nutrition'] = {
                'avg_calories': low_pain_days['calories'].mean(),
                'avg_protein': low_pain_days['protein'].mean(),
                'avg_fiber': low_pain_days['fiber'].mean(),
                'avg_water': low_pain_days['water_intake'].mean(),
                'avg_caffeine': low_pain_days['caffeine'].mean() if 'caffeine' in low_pain_days.columns else 0
            }
        
        return insights
    
    def get_feature_importance(self):
        """Get feature importance for nutrition factors"""
        if self.model is None:
            return None
        
        feature_names = [
            'calories', 'protein', 'carbs', 'fat', 'fiber', 'sugar',
            'water_intake', 'caffeine', 'alcohol',
            'protein_ratio', 'fiber_ratio',
            'calories_rolling_3d', 'protein_rolling_3d',
            'fiber_rolling_3d', 'water_intake_rolling_3d'
        ]
        
        importance = self.model.feature_importances_
        return dict(zip(feature_names[:len(importance)], importance))