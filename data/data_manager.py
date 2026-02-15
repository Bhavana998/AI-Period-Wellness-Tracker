import pandas as pd
import numpy as np
from datetime import datetime
import json
import os
from pathlib import Path

class DataManager:
    def __init__(self, data_dir='user_data'):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.data_file = self.data_dir / 'period_data.csv'
        self.food_file = self.data_dir / 'food_data.csv'
        self.load_data()
    
    def load_data(self):
        """Load existing data or create new dataframe"""
        try:
            if self.data_file.exists():
                self.df = pd.read_csv(self.data_file)
                # Parse dates with dayfirst=True for DD-MM-YYYY format
                try:
                    self.df['date'] = pd.to_datetime(self.df['date'], format='%Y-%m-%d').dt.date
                except:
                    try:
                        self.df['date'] = pd.to_datetime(self.df['date'], format='%d-%m-%Y').dt.date
                    except:
                        self.df['date'] = pd.to_datetime(self.df['date'], dayfirst=True).dt.date
            else:
                self.df = pd.DataFrame(columns=[
                    'date', 'period_start', 'bleeding', 'pain_level', 
                    'cramps', 'sleep_hours', 'sleep_quality', 'stress_level',
                    'exercise_minutes', 'mood', 'notes'
                ])
            
            # Load food data
            if self.food_file.exists():
                self.food_df = pd.read_csv(self.food_file)
                try:
                    self.food_df['date'] = pd.to_datetime(self.food_df['date'], format='%Y-%m-%d').dt.date
                except:
                    try:
                        self.food_df['date'] = pd.to_datetime(self.food_df['date'], format='%d-%m-%Y').dt.date
                    except:
                        self.food_df['date'] = pd.to_datetime(self.food_df['date'], dayfirst=True).dt.date
            else:
                self.food_df = pd.DataFrame(columns=[
                    'date', 'meal_type', 'food_items', 'calories', 
                    'protein', 'carbs', 'fat', 'fiber', 'sugar',
                    'water_intake', 'caffeine', 'alcohol', 'cravings',
                    'bloating', 'digestion_quality'
                ])
        except Exception as e:
            print(f"Error loading data: {e}")
            # Create empty dataframes if loading fails
            self.df = pd.DataFrame(columns=[
                'date', 'period_start', 'bleeding', 'pain_level', 
                'cramps', 'sleep_hours', 'sleep_quality', 'stress_level',
                'exercise_minutes', 'mood', 'notes'
            ])
            self.food_df = pd.DataFrame(columns=[
                'date', 'meal_type', 'food_items', 'calories', 
                'protein', 'carbs', 'fat', 'fiber', 'sugar',
                'water_intake', 'caffeine', 'alcohol', 'cravings',
                'bloating', 'digestion_quality'
            ])
    
    def save_entry(self, data):
        """Save a new period entry"""
        try:
            new_row = pd.DataFrame([data])
            
            if self.df.empty:
                self.df = new_row
            else:
                # Check if entry for this date already exists
                if data['date'] in self.df['date'].values:
                    # Update existing entry
                    self.df.loc[self.df['date'] == data['date']] = new_row.iloc[0]
                else:
                    # Add new entry
                    self.df = pd.concat([self.df, new_row], ignore_index=True)
            
            # Sort by date
            self.df = self.df.sort_values('date')
            
            # Calculate cycle lengths
            self.calculate_cycle_lengths()
            
            # Save to file
            self.df.to_csv(self.data_file, index=False)
            return True
        except Exception as e:
            print(f"Error saving entry: {e}")
            return False
    
    def save_food_entry(self, data):
        """Save a new food entry"""
        try:
            new_row = pd.DataFrame([data])
            
            if self.food_df.empty:
                self.food_df = new_row
            else:
                # Check if entry for this date/meal exists
                mask = (self.food_df['date'] == data['date']) & (self.food_df['meal_type'] == data['meal_type'])
                if mask.any():
                    # Update existing entry
                    self.food_df.loc[mask] = new_row.iloc[0]
                else:
                    # Add new entry
                    self.food_df = pd.concat([self.food_df, new_row], ignore_index=True)
            
            # Sort by date
            self.food_df = self.food_df.sort_values('date')
            
            # Save to file
            self.food_df.to_csv(self.food_file, index=False)
            return True
        except Exception as e:
            print(f"Error saving food entry: {e}")
            return False
    
    def calculate_cycle_lengths(self):
        """Calculate cycle lengths based on period start dates"""
        try:
            if 'period_start' not in self.df.columns:
                return
            
            # Convert to datetime for calculations
            period_starts = []
            for date in self.df[self.df['period_start'] == True]['date']:
                if isinstance(date, str):
                    period_starts.append(pd.to_datetime(date).date())
                else:
                    period_starts.append(date)
            
            if len(period_starts) > 1:
                cycle_lengths = []
                for i in range(1, len(period_starts)):
                    days = (period_starts[i] - period_starts[i-1]).days
                    if 20 <= days <= 45:  # Only store realistic cycles
                        cycle_lengths.append(days)
                
                # Add cycle lengths to dataframe
                self.df['cycle_length'] = None
                for i, start_date in enumerate(period_starts[1:], 1):
                    if i-1 < len(cycle_lengths):
                        self.df.loc[self.df['date'] == start_date, 'cycle_length'] = cycle_lengths[i-1]
        except Exception as e:
            print(f"Error calculating cycle lengths: {e}")
    
    def get_all_data(self):
        """Get all period data as dataframe"""
        return self.df.copy()
    
    def get_food_data(self, date=None):
        """Get food data, optionally filtered by date"""
        if date:
            return self.food_df[self.food_df['date'] == date].copy()
        return self.food_df.copy()
    
    def merge_period_food_data(self):
        """Merge period and food data for analysis"""
        if self.df.empty or self.food_df.empty:
            return self.df.copy()
        
        try:
            # Aggregate food data by date
            daily_nutrition = self.food_df.groupby('date').agg({
                'calories': 'sum',
                'protein': 'sum',
                'carbs': 'sum',
                'fat': 'sum',
                'fiber': 'sum',
                'sugar': 'sum',
                'water_intake': 'sum',
                'caffeine': 'mean',
                'alcohol': 'mean'
            }).reset_index()
            
            # Merge with period data
            merged = pd.merge(self.df, daily_nutrition, on='date', how='left')
            return merged
        except Exception as e:
            print(f"Error merging data: {e}")
            return self.df.copy()
    
    def get_data_range(self, start_date, end_date):
        """Get data within date range"""
        try:
            mask = (self.df['date'] >= start_date) & (self.df['date'] <= end_date)
            return self.df[mask].copy()
        except Exception as e:
            print(f"Error getting data range: {e}")
            return pd.DataFrame()
    
    def get_statistics(self):
        """Get basic statistics"""
        if self.df.empty:
            return {}
        
        try:
            stats = {
                'total_entries': len(self.df),
                'avg_pain': self.df['pain_level'].mean(),
                'avg_sleep': self.df['sleep_hours'].mean(),
                'avg_stress': self.df['stress_level'].mean(),
                'total_periods': len(self.df[self.df['period_start'] == True])
            }
            
            if 'cycle_length' in self.df.columns:
                valid_cycles = self.df['cycle_length'].dropna()
                if not valid_cycles.empty:
                    stats['avg_cycle'] = valid_cycles.mean()
                    stats['cycle_regularity'] = valid_cycles.std()
            
            return stats
        except Exception as e:
            print(f"Error getting statistics: {e}")
            return {}
    
    def import_from_csv(self, csv_file_path):
        """
        Import period data from a CSV file
        
        Parameters:
        - csv_file_path: Path to the CSV file
        
        Returns:
        - Number of records imported
        """
        try:
            # Read the CSV file
            print(f"📂 Reading file: {csv_file_path}")
            import_df = pd.read_csv(csv_file_path)
            
            print(f"📊 CSV Shape: {import_df.shape}")
            print(f"📋 Columns found: {list(import_df.columns)}")
            
            # Standardize column names (handle different naming conventions)
            column_mapping = {
                'date': 'date',
                'Date': 'date',
                'DATE': 'date',
                'start_date': 'date',
                'Start Date': 'date',
                'period_date': 'date',
                'Period Date': 'date',
                'Cycle Start Date': 'date',
                'cycle_start_date': 'date',
                'pain': 'pain_level',
                'Pain': 'pain_level',
                'pain_level': 'pain_level',
                'pain score': 'pain_level',
                'pain_score': 'pain_level',
                'sleep': 'sleep_hours',
                'Sleep': 'sleep_hours',
                'sleep_hours': 'sleep_hours',
                'sleep hours': 'sleep_hours',
                'stress': 'stress_level',
                'Stress': 'stress_level',
                'stress_level': 'stress_level',
                'stress level': 'stress_level',
                'exercise': 'exercise_minutes',
                'Exercise': 'exercise_minutes',
                'exercise_minutes': 'exercise_minutes',
                'exercise minutes': 'exercise_minutes',
                'mood': 'mood',
                'Mood': 'mood',
                'cramps': 'cramps',
                'Cramps': 'cramps',
                'bleeding': 'bleeding',
                'Bleeding': 'bleeding',
                'period_start': 'period_start',
                'Period Start': 'period_start',
                'period start': 'period_start',
                'sleep_quality': 'sleep_quality',
                'Sleep Quality': 'sleep_quality',
                'sleep quality': 'sleep_quality',
                'notes': 'notes',
                'Notes': 'notes'
            }
            
            # Rename columns to match our format
            import_df.rename(columns=column_mapping, inplace=True)
            print(f"✅ After mapping: {list(import_df.columns)}")
            
            # Ensure required columns exist
            if 'date' not in import_df.columns:
                print("❌ Error: No 'date' column found")
                print(f"   Available columns: {list(import_df.columns)}")
                return 0
            
            # Print first few dates for debugging
            print(f"📅 First few dates before conversion: {import_df['date'].head(3).tolist()}")
            
            # Convert date column - handle multiple formats
            try:
                # Try DD-MM-YYYY format (day first) - common in many datasets
                import_df['date'] = pd.to_datetime(import_df['date'], format='%d-%m-%Y', errors='raise').dt.date
                print("✅ Dates parsed as DD-MM-YYYY format")
            except:
                try:
                    # Try YYYY-MM-DD format
                    import_df['date'] = pd.to_datetime(import_df['date'], format='%Y-%m-%d', errors='raise').dt.date
                    print("✅ Dates parsed as YYYY-MM-DD format")
                except:
                    try:
                        # Try MM-DD-YYYY format (month first)
                        import_df['date'] = pd.to_datetime(import_df['date'], format='%m-%d-%Y', errors='raise').dt.date
                        print("✅ Dates parsed as MM-DD-YYYY format")
                    except:
                        try:
                            # Try with dayfirst=True for mixed formats
                            import_df['date'] = pd.to_datetime(import_df['date'], dayfirst=True, errors='coerce').dt.date
                            print("✅ Dates parsed with dayfirst=True")
                        except:
                            # Last resort - let pandas guess
                            import_df['date'] = pd.to_datetime(import_df['date'], errors='coerce').dt.date
                            print("⚠️ Dates parsed with auto-detection")
            
            # Check for any NaT values (failed parsing)
            if import_df['date'].isna().any():
                print(f"⚠️ Warning: {import_df['date'].isna().sum()} dates could not be parsed")
                # Drop rows with invalid dates
                import_df = import_df.dropna(subset=['date'])
                print(f"📊 After dropping invalid dates: {len(import_df)} rows")
            
            print(f"✅ Date range: {import_df['date'].min()} to {import_df['date'].max()}")
            
            # Fill missing columns with defaults
            for col in self.df.columns:
                if col not in import_df.columns:
                    print(f"⚠️ Adding missing column: {col} with default values")
                    if col == 'period_start':
                        import_df[col] = False
                    elif col == 'pain_level':
                        import_df[col] = 0
                    elif col == 'sleep_hours':
                        import_df[col] = 7.0
                    elif col == 'stress_level':
                        import_df[col] = 5
                    elif col == 'sleep_quality':
                        import_df[col] = 'Fair'
                    elif col == 'mood':
                        import_df[col] = 'Calm'
                    elif col == 'cramps':
                        import_df[col] = False
                    elif col == 'bleeding':
                        import_df[col] = 'None'
                    elif col == 'exercise_minutes':
                        import_df[col] = 0
                    elif col == 'notes':
                        import_df[col] = ''
                    else:
                        import_df[col] = 0
            
            # Convert boolean columns
            if 'period_start' in import_df.columns:
                # Handle various true/false representations
                true_values = ['TRUE', 'True', 'true', '1', 'YES', 'Yes', 'yes', 'Y', 'y', 1, True]
                false_values = ['FALSE', 'False', 'false', '0', 'NO', 'No', 'no', 'N', 'n', 0, False]
                
                # Convert to string first to handle mixed types
                import_df['period_start'] = import_df['period_start'].astype(str).str.upper()
                import_df['period_start'] = import_df['period_start'].isin(['TRUE', '1', 'YES', 'Y'])
                print(f"✅ Period_start converted")
            
            if 'cramps' in import_df.columns:
                import_df['cramps'] = import_df['cramps'].astype(str).str.upper()
                import_df['cramps'] = import_df['cramps'].isin(['TRUE', '1', 'YES', 'Y'])
            
            # Append to existing data
            print(f"📊 Existing data: {len(self.df)} rows")
            self.df = pd.concat([self.df, import_df[self.df.columns]], ignore_index=True)
            print(f"✅ After concat: {len(self.df)} total rows")
            
            # Remove duplicates (keep latest based on date)
            before_dedup = len(self.df)
            self.df = self.df.drop_duplicates(subset=['date'], keep='last')
            after_dedup = len(self.df)
            print(f"✅ Removed {before_dedup - after_dedup} duplicates")
            
            # Sort by date
            self.df = self.df.sort_values('date')
            
            # Recalculate cycle lengths
            self.calculate_cycle_lengths()
            
            # Save to file
            self.df.to_csv(self.data_file, index=False)
            print(f"✅ Saved to {self.data_file}")
            
            return len(import_df)
        
        except Exception as e:
            print(f"❌ Error importing CSV: {str(e)}")
            import traceback
            traceback.print_exc()
            return 0
    
    def generate_sample_data(self, num_cycles=3):
        """Generate sample period data for testing/demo"""
        np.random.seed(42)  # For reproducible results
        
        sample_data = []
        
        # Start date (90 days ago)
        start_date = datetime.now().date() - timedelta(days=90)
        
        # Cycle parameters
        cycle_lengths = np.random.normal(28, 2, num_cycles).astype(int)
        period_lengths = np.random.normal(5, 1, num_cycles).astype(int)
        
        current_date = start_date
        
        for cycle in range(num_cycles):
            cycle_length = max(21, min(35, cycle_lengths[cycle]))
            period_length = max(3, min(7, period_lengths[cycle]))
            
            # Period days
            for day in range(period_length):
                date = current_date + timedelta(days=day)
                
                # Pain varies during period
                if day == 0 or day == period_length - 1:
                    pain = np.random.randint(2, 5)
                elif day == 1 or day == 2:
                    pain = np.random.randint(5, 9)
                else:
                    pain = np.random.randint(3, 7)
                
                sample_data.append({
                    'date': date,
                    'period_start': day == 0,
                    'bleeding': ['Light', 'Medium', 'Heavy'][min(day, 2)],
                    'pain_level': pain,
                    'cramps': pain > 3,
                    'sleep_hours': np.random.normal(7, 1),
                    'sleep_quality': np.random.choice(['Poor', 'Fair', 'Good', 'Excellent']),
                    'stress_level': np.random.randint(3, 8),
                    'exercise_minutes': np.random.randint(0, 60),
                    'mood': np.random.choice(['Happy', 'Calm', 'Anxious', 'Irritable', 'Tired']),
                    'notes': ''
                })
            
            # Non-period days
            for day in range(period_length, cycle_length):
                date = current_date + timedelta(days=day)
                
                # Cycle phase affects symptoms
                cycle_day = day + 1
                
                if 6 <= cycle_day <= 13:  # Follicular
                    pain = np.random.randint(0, 2)
                    mood = 'Happy'
                elif 14 <= cycle_day <= 16:  # Ovulation
                    pain = np.random.randint(1, 3)
                    mood = 'Energetic'
                elif 17 <= cycle_day <= 25:  # Luteal
                    pain = np.random.randint(2, 5)
                    mood = np.random.choice(['Calm', 'Anxious', 'Irritable'])
                else:  # Late luteal
                    pain = np.random.randint(3, 6)
                    mood = np.random.choice(['Irritable', 'Tired', 'Anxious'])
                
                sample_data.append({
                    'date': date,
                    'period_start': False,
                    'bleeding': 'None',
                    'pain_level': pain,
                    'cramps': pain > 4,
                    'sleep_hours': np.random.normal(7.5, 1),
                    'sleep_quality': np.random.choice(['Fair', 'Good', 'Excellent']),
                    'stress_level': np.random.randint(2, 7),
                    'exercise_minutes': np.random.randint(15, 90),
                    'mood': mood,
                    'notes': ''
                })
            
            # Move to next cycle
            current_date += timedelta(days=cycle_length)
        
        return pd.DataFrame(sample_data)
    
    def load_sample_data(self):
        """Load sample data for testing"""
        sample_df = self.generate_sample_data(4)  # Generate 4 cycles
        self.df = sample_df
        self.calculate_cycle_lengths()
        self.df.to_csv(self.data_file, index=False)
        return len(self.df)
    
    def clear_data(self):
        """Clear all data"""
        try:
            if self.data_file.exists():
                os.remove(self.data_file)
            if self.food_file.exists():
                os.remove(self.food_file)
            self.df = pd.DataFrame(columns=self.df.columns)
            self.food_df = pd.DataFrame(columns=self.food_df.columns)
            return True
        except Exception as e:
            print(f"Error clearing data: {e}")
            return False