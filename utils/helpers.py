from datetime import datetime, timedelta
import pandas as pd
import numpy as np

def calculate_cycle_phases(df, current_date):
    """
    Calculate which phase of menstrual cycle a given date falls into
    """
    if df.empty:
        return "Unknown"
    
    # Find last period start
    period_starts = df[df['period_start'] == True]['date'].tolist()
    if not period_starts:
        return "Unknown"
    
    last_period = period_starts[-1]
    days_since = (current_date - last_period).days
    
    # Define phases (typical 28-day cycle)
    if days_since < 0:
        return "Pre-period"
    elif days_since <= 5:
        return "Menstrual"
    elif days_since <= 13:
        return "Follicular"
    elif days_since <= 16:
        return "Ovulation"
    elif days_since <= 25:
        return "Luteal"
    elif days_since <= 28:
        return "Late Luteal"
    else:
        return "Pre-period"

def generate_insights(df):
    """
    Generate personalized insights from the data
    """
    insights = []
    
    if df.empty:
        return insights
    
    # Sleep insight
    avg_sleep = df['sleep_hours'].mean()
    if avg_sleep < 7:
        insights.append("💤 You're averaging less than 7 hours of sleep. Try to get more rest, especially before your period.")
    elif avg_sleep > 9:
        insights.append("😴 You're sleeping a lot. This could be due to fatigue from your cycle.")
    
    # Stress insight
    avg_stress = df['stress_level'].mean()
    if avg_stress > 6:
        insights.append("😰 Your stress levels are consistently high. Consider meditation, deep breathing, or light exercise.")
    elif avg_stress < 3:
        insights.append("😊 Great job managing stress! This likely helps with your period symptoms.")
    
    # Pain insight
    avg_pain = df['pain_level'].mean()
    if avg_pain > 5:
        insights.append("💊 You experience moderate to severe pain. Track if certain foods or activities help reduce it.")
    elif avg_pain < 2:
        insights.append("✨ Your pain levels are low! Keep up whatever you're doing.")
    
    # Cycle regularity
    if 'cycle_length' in df.columns and len(df['cycle_length'].dropna()) > 1:
        cycle_std = df['cycle_length'].std()
        if cycle_std < 2:
            insights.append("📅 Your cycle is very regular! This makes predictions more accurate.")
        elif cycle_std > 5:
            insights.append("📊 Your cycle varies quite a bit. This is normal, especially with lifestyle changes.")
    
    return insights

def calculate_fertile_window(last_period, cycle_length=28):
    """
    Calculate fertile window based on last period and cycle length
    """
    if not last_period:
        return None
    
    # Ovulation typically occurs 14 days before next period
    ovulation_day = cycle_length - 14
    
    # Fertile window is ~5 days before ovulation through day of ovulation
    fertile_start = last_period + timedelta(days=max(0, ovulation_day - 5))
    fertile_end = last_period + timedelta(days=ovulation_day)
    
    return fertile_start, fertile_end

def get_mood_recommendations(mood, cycle_phase):
    """
    Get recommendations based on mood and cycle phase
    """
    recommendations = {
        'Anxious': {
            'Menstrual': 'Try gentle yoga and deep breathing. Warm tea can help.',
            'Follicular': 'Channel this energy into creative projects or exercise.',
            'Ovulation': 'Practice grounding exercises. Avoid overcommitting.',
            'Luteal': 'Limit caffeine. Try meditation and calming activities.',
            'default': 'Take deep breaths. Go for a walk if possible.'
        },
        'Irritable': {
            'Menstrual': 'Rest when needed. Warm baths can help.',
            'Luteal': 'This is common. Give yourself grace and space.',
            'default': 'Take a break. Listen to calming music.'
        },
        'Sad': {
            'Menstrual': 'Be gentle with yourself. Connect with supportive friends.',
            'Luteal': 'Light exposure and movement might help. Reach out to others.',
            'default': 'Self-care is important. Do something you enjoy today.'
        },
        'Tired': {
            'Menstrual': 'Your body needs rest. Honor that with early bedtimes.',
            'Luteal': 'Fatigue is common. Prioritize sleep and gentle movement.',
            'default': "Make sure you're getting enough iron and B vitamins."  # FIXED: Used double quotes around string with apostrophe
        }
    }
    
    if mood in recommendations:
        phase_rec = recommendations[mood].get(cycle_phase, recommendations[mood]['default'])
        return phase_rec
    return "Listen to your body and do what feels good today."

def calculate_symptom_patterns(df):
    """
    Calculate patterns in symptoms over cycles
    """
    if df.empty or 'cycle_day' not in df.columns:
        return {}
    
    patterns = {}
    
    # Group by cycle day
    for day in range(1, 29):
        day_data = df[df['cycle_day'] == day]
        if not day_data.empty:
            patterns[f'Day {day}'] = {
                'avg_pain': day_data['pain_level'].mean(),
                'avg_sleep': day_data['sleep_hours'].mean(),
                'avg_stress': day_data['stress_level'].mean(),
                'sample_size': len(day_data)
            }
    
    return patterns