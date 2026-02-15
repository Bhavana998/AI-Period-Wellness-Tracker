import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import os

# Import custom modules
from models.pain_predictor import PainPredictor
from models.cycle_predictor import CyclePredictor
from models.nutrition_predictor import NutritionPredictor
from data.data_manager import DataManager
from data.food_database import FoodDatabase
from utils.helpers import calculate_cycle_phases, generate_insights
from utils.nutrition_utils import analyze_nutrition, get_meal_suggestions

# Page configuration
st.set_page_config(
    page_title="AI Period & Wellness Tracker",
    page_icon="🌸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        color: #FF69B4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #4A4A4A;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
    }
    .pain-high {
        color: #ff4444;
        font-weight: bold;
    }
    .pain-medium {
        color: #ff8800;
        font-weight: bold;
    }
    .pain-low {
        color: #00C851;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'data_manager' not in st.session_state:
    st.session_state.data_manager = DataManager()
if 'pain_predictor' not in st.session_state:
    st.session_state.pain_predictor = PainPredictor()
if 'cycle_predictor' not in st.session_state:
    st.session_state.cycle_predictor = CyclePredictor()
if 'nutrition_predictor' not in st.session_state:
    st.session_state.nutrition_predictor = NutritionPredictor()

def main():
    # Header
    st.markdown("<h1 class='main-header'>🌸 AI Period & Wellness Tracker</h1>", unsafe_allow_html=True)
    
    # Sidebar navigation
    st.sidebar.image("https://img.icons8.com/color/96/000000/periods.png", width=100)
    st.sidebar.title("Navigation")
    page = st.sidebar.radio(
        "Go to",
        ["Dashboard", "Log Period Data", "Log Food", "Predictions", "Insights & Analytics", "Sleep Analysis", "Settings"]
    )
    
    if page == "Dashboard":
        show_dashboard()
    elif page == "Log Period Data":
        show_log_period_data()
    elif page == "Log Food":
        show_food_tracking()
    elif page == "Predictions":
        show_predictions()
    elif page == "Insights & Analytics":
        show_insights()
    elif page == "Sleep Analysis":
        show_sleep_analysis()
    elif page == "Settings":
        show_settings()

def show_dashboard():
    st.markdown("<h2 class='sub-header'>📊 Your Wellness Dashboard</h2>", unsafe_allow_html=True)
    
    # Get latest data
    df = st.session_state.data_manager.get_all_data()
    
    if df.empty:
        st.info("Welcome! Start by logging your first period cycle in the 'Log Period Data' section.")
        return
    
    # Current cycle status
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        next_period = st.session_state.cycle_predictor.predict_next_period(df)
        if next_period:
            days_until = (next_period - datetime.now().date()).days
            display_text = f"{days_until} days"
        else:
            display_text = "N/A"
        
        st.markdown(
            f"""<div class='metric-card'>
                <h3>Next Period</h3>
                <h2>{display_text}</h2>
            </div>""", 
            unsafe_allow_html=True
        )
    
    with col2:
        current_phase = calculate_cycle_phases(df, datetime.now().date())
        st.markdown(
            f"""<div class='metric-card'>
                <h3>Current Phase</h3>
                <h2>{current_phase}</h2>
            </div>""", 
            unsafe_allow_html=True
        )
    
    with col3:
        if 'cycle_length' in df.columns and not df['cycle_length'].isna().all():
            avg_cycle = df['cycle_length'].mean()
            display_cycle = f"{avg_cycle:.1f} days"
        else:
            display_cycle = "N/A"
        
        st.markdown(
            f"""<div class='metric-card'>
                <h3>Avg Cycle Length</h3>
                <h2>{display_cycle}</h2>
            </div>""", 
            unsafe_allow_html=True
        )
    
    with col4:
        pain_today = predict_today_pain(df)
        pain_class = "pain-low" if pain_today < 3 else "pain-medium" if pain_today < 6 else "pain-high"
        st.markdown(
            f"""<div class='metric-card'>
                <h3>Pain Risk Today</h3>
                <h2 class='{pain_class}'>{pain_today:.1f}/10</h2>
            </div>""", 
            unsafe_allow_html=True
        )
    
    # Cycle visualization
    st.markdown("### 📈 Cycle History")
    fig = create_cycle_visualization(df)
    st.plotly_chart(fig, use_container_width=True)
    
    # Recent symptoms
    st.markdown("### 📝 Recent Symptoms")
    recent_data = df.tail(7)
    if not recent_data.empty:
        cols = st.columns(len(recent_data))
        for i, (idx, row) in enumerate(recent_data.iterrows()):
            with cols[i]:
                st.markdown(f"**{row['date']}**")
                st.markdown(f"Pain: {row['pain_level']}/10")
                st.markdown(f"Sleep: {row['sleep_hours']:.1f}h")
                st.markdown(f"Stress: {row['stress_level']}/10")

def show_log_period_data():
    st.markdown("<h2 class='sub-header'>📝 Log Your Period Data</h2>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Period Information")
        date = st.date_input("Date", datetime.now())
        period_start = st.checkbox("Period started today?")
        
        if period_start:
            bleeding = st.select_slider(
                "Bleeding intensity",
                options=["Spotting", "Light", "Medium", "Heavy"]
            )
        else:
            bleeding = "None"
        
        pain_level = st.slider("Pain level (0-10)", 0, 10, 0)
        cramps = st.checkbox("Cramps")
        
    with col2:
        st.markdown("### Lifestyle Factors")
        sleep_hours = st.slider("Sleep hours", 0.0, 12.0, 7.0, 0.5)
        sleep_quality = st.select_slider(
            "Sleep quality",
            options=["Very Poor", "Poor", "Fair", "Good", "Excellent"]
        )
        
        stress_level = st.slider("Stress level (0-10)", 0, 10, 5)
        exercise_minutes = st.number_input("Exercise (minutes)", 0, 300, 30)
        
        mood = st.selectbox(
            "Mood",
            ["Happy", "Calm", "Anxious", "Irritable", "Sad", "Energetic", "Tired"]
        )
        
        notes = st.text_area("Additional notes")
    
    if st.button("Save Entry", type="primary"):
        data = {
            'date': date,
            'period_start': period_start,
            'bleeding': bleeding,
            'pain_level': pain_level,
            'cramps': cramps,
            'sleep_hours': sleep_hours,
            'sleep_quality': sleep_quality,
            'stress_level': stress_level,
            'exercise_minutes': exercise_minutes,
            'mood': mood,
            'notes': notes
        }
        
        st.session_state.data_manager.save_entry(data)
        
        # Train/update models with new data
        df = st.session_state.data_manager.get_all_data()
        if len(df) >= 10:
            st.session_state.pain_predictor.train(df)
            st.session_state.cycle_predictor.train(df)
        
        st.success("Entry saved successfully!")

def show_food_tracking():
    st.markdown("<h2 class='sub-header'>🍽️ Food & Nutrition Tracking</h2>", unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4 = st.tabs(["Log Food", "Daily Nutrition", "Cycle-Based Nutrition", "Food Insights"])
    
    with tab1:
        st.markdown("### Log Your Meals")
        
        col1, col2 = st.columns(2)
        
        with col1:
            date = st.date_input("Date", datetime.now())
            meal_type = st.selectbox("Meal Type", ["Breakfast", "Lunch", "Dinner", "Snack", "Drink"])
            
            use_quick_add = st.checkbox("Use quick food database")
            
            if use_quick_add:
                category = st.selectbox("Food Category", list(FoodDatabase.PERIOD_FRIENDLY_FOODS.keys()))
                foods = FoodDatabase.PERIOD_FRIENDLY_FOODS[category]
                food_names = [f['name'] for f in foods]
                selected_food = st.selectbox("Select Food", food_names)
                
                food_info = next(f for f in foods if f['name'] == selected_food)
                quantity = st.number_input("Quantity (servings)", 0.25, 5.0, 1.0, 0.25)
                
                calories = food_info['calories'] * quantity
                protein = food_info['protein'] * quantity
                carbs = food_info['carbs'] * quantity
                fat = food_info['fat'] * quantity
                fiber = food_info.get('fiber', 0) * quantity
                
                food_items = f"{quantity}x {selected_food}"
                sugar = food_info.get('sugar', 0) * quantity
                
            else:
                food_items = st.text_area("Food Items (comma separated)")
                
                col_nut1, col_nut2, col_nut3 = st.columns(3)
                with col_nut1:
                    calories = st.number_input("Calories", 0, 2000, 0)
                    protein = st.number_input("Protein (g)", 0.0, 100.0, 0.0, 0.1)
                with col_nut2:
                    carbs = st.number_input("Carbs (g)", 0.0, 200.0, 0.0, 0.1)
                    fat = st.number_input("Fat (g)", 0.0, 100.0, 0.0, 0.1)
                with col_nut3:
                    fiber = st.number_input("Fiber (g)", 0.0, 50.0, 0.0, 0.1)
                    sugar = st.number_input("Sugar (g)", 0.0, 100.0, 0.0, 0.1)
        
        with col2:
            st.markdown("### Hydration & Extras")
            
            water_intake = st.number_input("Water intake (cups)", 0.0, 20.0, 4.0, 0.5)
            caffeine = st.selectbox("Caffeine", ["None", "Low", "Medium", "High"])
            caffeine_map = {"None": 0, "Low": 1, "Medium": 2, "High": 3}
            
            alcohol = st.selectbox("Alcohol", ["None", "1 drink", "2-3 drinks", "4+ drinks"])
            alcohol_map = {"None": 0, "1 drink": 1, "2-3 drinks": 2, "4+ drinks": 3}
            
            st.markdown("### Symptoms")
            cravings = st.multiselect(
                "Cravings",
                ["Sweet", "Salty", "Chocolate", "Carbs", "None"]
            )
            
            bloating = st.select_slider(
                "Bloating level",
                options=["None", "Mild", "Moderate", "Severe"]
            )
            
            digestion = st.select_slider(
                "Digestion quality",
                options=["Poor", "Fair", "Good", "Excellent"]
            )
        
        if st.button("Save Food Entry", type="primary"):
            food_data = {
                'date': date,
                'meal_type': meal_type,
                'food_items': food_items,
                'calories': calories,
                'protein': protein,
                'carbs': carbs,
                'fat': fat,
                'fiber': fiber,
                'sugar': sugar,
                'water_intake': water_intake,
                'caffeine': caffeine_map[caffeine],
                'alcohol': alcohol_map[alcohol],
                'cravings': ', '.join(cravings),
                'bloating': bloating,
                'digestion_quality': digestion
            }
            
            st.session_state.data_manager.save_food_entry(food_data)
            st.success("Food entry saved successfully!")
    
    with tab2:
        st.markdown("### Daily Nutrition Summary")
        
        food_df = st.session_state.data_manager.get_food_data()
        if not food_df.empty:
            daily_nutrition = food_df.groupby('date').agg({
                'calories': 'sum',
                'protein': 'sum',
                'carbs': 'sum',
                'fat': 'sum',
                'fiber': 'sum',
                'water_intake': 'sum'
            }).reset_index()
            
            st.dataframe(daily_nutrition.tail(7))
            
            col1, col2 = st.columns(2)
            
            with col1:
                latest = daily_nutrition.iloc[-1] if not daily_nutrition.empty else None
                if latest is not None:
                    protein_cals = latest['protein'] * 4
                    carbs_cals = latest['carbs'] * 4
                    fat_cals = latest['fat'] * 9
                    
                    if protein_cals + carbs_cals + fat_cals > 0:
                        fig = go.Figure(data=[go.Pie(
                            labels=['Protein', 'Carbs', 'Fat'],
                            values=[protein_cals, carbs_cals, fat_cals],
                            hole=.3
                        )])
                        fig.update_layout(title="Today's Calorie Distribution")
                        st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=daily_nutrition['date'].tail(14),
                    y=daily_nutrition['water_intake'].tail(14),
                    mode='lines+markers',
                    name='Water Intake',
                    line=dict(color='#33b5e5', width=3)
                ))
                fig.add_hline(y=8, line_dash="dash", line_color="green", annotation_text="Recommended")
                fig.update_layout(title="Water Intake Trend")
                st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.markdown("### Cycle-Based Nutrition Recommendations")
        
        df = st.session_state.data_manager.get_all_data()
        if not df.empty:
            current_phase = calculate_cycle_phases(df, datetime.now().date())
            recommendations = FoodDatabase.get_recommendations(current_phase)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"#### 🌸 {current_phase} Phase")
                st.markdown(f"**Focus on:** {', '.join(recommendations['focus'])}")
                
                st.markdown("**Recommended Foods:**")
                for food in recommendations['foods']:
                    st.markdown(f"✅ {food}")
            
            with col2:
                st.markdown("**Foods to Avoid:**")
                for food in recommendations['avoid']:
                    st.markdown(f"❌ {food}")
    
    with tab4:
        st.markdown("### Food & Symptom Insights")
        
        df = st.session_state.data_manager.get_all_data()
        food_df = st.session_state.data_manager.get_food_data()
        
        if not df.empty and not food_df.empty:
            merged = pd.merge(df, food_df, on='date', how='inner')
            
            if not merged.empty:
                corr_cols = ['pain_level', 'calories', 'protein', 'fiber', 'sugar', 'water_intake', 'caffeine', 'alcohol']
                available_cols = [col for col in corr_cols if col in merged.columns]
                
                if len(available_cols) > 1:
                    corr_data = merged[available_cols].corr()
                    
                    fig = px.imshow(
                        corr_data,
                        text_auto=True,
                        aspect="auto",
                        color_continuous_scale='RdBu_r'
                    )
                    fig.update_layout(title="Nutrition-Symptom Correlations")
                    st.plotly_chart(fig, use_container_width=True)
                
                st.markdown("### 🔍 Key Findings")
                
                low_pain = merged[merged['pain_level'] <= 3]
                high_pain = merged[merged['pain_level'] >= 7]
                
                if not low_pain.empty and not high_pain.empty:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**On Low Pain Days You Had:**")
                        st.metric("Avg Water", f"{low_pain['water_intake'].mean():.1f} cups")
                        st.metric("Avg Fiber", f"{low_pain['fiber'].mean():.1f}g")
                        st.metric("Avg Protein", f"{low_pain['protein'].mean():.1f}g")
                    
                    with col2:
                        st.markdown("**On High Pain Days You Had:**")
                        st.metric("Avg Water", f"{high_pain['water_intake'].mean():.1f} cups")
                        st.metric("Avg Fiber", f"{high_pain['fiber'].mean():.1f}g")
                        st.metric("Avg Protein", f"{high_pain['protein'].mean():.1f}g")

def show_predictions():
    st.markdown("<h2 class='sub-header'>🔮 AI Predictions</h2>", unsafe_allow_html=True)
    
    df = st.session_state.data_manager.get_all_data()
    
    if df.empty or len(df) < 10:
        st.warning("Need at least 10 days of data to make predictions. Keep logging!")
        return
    
    st.markdown("### 📅 Period Predictions")
    
    next_period = st.session_state.cycle_predictor.predict_next_period(df)
    if next_period:
        days_until = (next_period - datetime.now().date()).days
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Next period", next_period.strftime("%B %d, %Y"))
        with col2:
            st.metric("Days until", days_until)
        with col3:
            confidence = min(95, len(df) * 2)
            st.metric("Prediction confidence", f"{confidence}%")
        
        fertile_start = next_period - timedelta(days=14)
        fertile_end = fertile_start + timedelta(days=5)
        st.info(f"🌱 Likely fertile window: {fertile_start.strftime('%B %d')} - {fertile_end.strftime('%B %d')}")
    
    st.markdown("### 💊 Pain Predictions")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Next 7 Days Pain Forecast")
        
        future_dates = [datetime.now().date() + timedelta(days=i) for i in range(7)]
        
        predictions = []
        for date in future_dates:
            days_from_now = (date - datetime.now().date()).days
            last_date = df['date'].iloc[-1]
            cycle_day = (last_date - datetime.now().date()).days + days_from_now
            cycle_day = abs(cycle_day) % 28
            
            if 0 <= cycle_day <= 5:
                base_pain = 6
            elif 6 <= cycle_day <= 13:
                base_pain = 2
            elif 14 <= cycle_day <= 16:
                base_pain = 3
            else:
                base_pain = 4
            
            pain = base_pain + np.random.normal(0, 1)
            pain = max(0, min(10, pain))
            predictions.append(pain)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=future_dates,
            y=predictions,
            mode='lines+markers',
            name='Predicted Pain',
            line=dict(color='#FF69B4', width=3)
        ))
        fig.update_layout(
            title="Pain Forecast",
            xaxis_title="Date",
            yaxis_title="Pain Level (0-10)",
            yaxis=dict(range=[0, 10])
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("#### Risk Factors")
        
        avg_sleep = df['sleep_hours'].tail(7).mean()
        avg_stress = df['stress_level'].tail(7).mean()
        
        if avg_sleep < 7:
            st.warning(f"⚠️ Low sleep ({avg_sleep:.1f}h) may increase pain risk")
        if avg_stress > 6:
            st.warning(f"⚠️ High stress ({avg_stress:.1f}/10) may worsen symptoms")
        
        st.markdown("#### 💡 Recommendations")
        if avg_sleep < 7:
            st.markdown("- Try to get 7-9 hours of sleep")
        if avg_stress > 6:
            st.markdown("- Consider stress-reduction techniques like meditation")
        
        st.markdown("- Stay hydrated during your period")
        st.markdown("- Light exercise may help reduce cramps")

def show_insights():
    st.markdown("<h2 class='sub-header'>📊 Insights & Analytics</h2>", unsafe_allow_html=True)
    
    df = st.session_state.data_manager.get_all_data()
    
    if df.empty:
        st.info("No data available yet. Start logging to see insights!")
        return
    
    st.markdown("### 📈 Key Statistics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        avg_pain = df['pain_level'].mean()
        st.metric("Average Pain", f"{avg_pain:.1f}/10")
    
    with col2:
        avg_sleep = df['sleep_hours'].mean()
        st.metric("Average Sleep", f"{avg_sleep:.1f}h")
    
    with col3:
        avg_stress = df['stress_level'].mean()
        st.metric("Average Stress", f"{avg_stress:.1f}/10")
    
    with col4:
        if 'cycle_length' in df.columns:
            cycle_std = df['cycle_length'].std()
            if not pd.isna(cycle_std):
                st.metric("Cycle Regularity", f"{cycle_std:.1f} days")
            else:
                st.metric("Cycle Regularity", "N/A")
        else:
            st.metric("Cycle Regularity", "N/A")
    
    st.markdown("### 🔗 Correlations with Pain")
    
    numeric_cols = ['pain_level', 'sleep_hours', 'stress_level', 'exercise_minutes']
    available_numeric = [col for col in numeric_cols if col in df.columns]
    
    if len(available_numeric) > 1:
        corr_data = df[available_numeric].corr()['pain_level'].drop('pain_level')
        
        fig = go.Figure(data=[
            go.Bar(
                x=corr_data.index,
                y=corr_data.values,
                marker_color=['#00C851' if x < 0 else '#ff4444' for x in corr_data.values]
            )
        ])
        fig.update_layout(
            title="Factors Affecting Pain",
            xaxis_title="Factor",
            yaxis_title="Correlation with Pain"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("### 📅 Pain by Cycle Phase")
    
    df['cycle_phase'] = df['date'].apply(
        lambda x: calculate_cycle_phases(df, x)
    )
    
    phase_pain = df.groupby('cycle_phase')['pain_level'].mean().reset_index()
    phase_pain = phase_pain.dropna()
    
    if not phase_pain.empty:
        fig = px.bar(
            phase_pain,
            x='cycle_phase',
            y='pain_level',
            color='pain_level',
            color_continuous_scale='Reds'
        )
        fig.update_layout(
            title="Average Pain by Cycle Phase",
            xaxis_title="Cycle Phase",
            yaxis_title="Average Pain Level"
        )
        st.plotly_chart(fig, use_container_width=True)

def show_sleep_analysis():
    st.markdown("<h2 class='sub-header'>😴 Sleep & Period Connection</h2>", unsafe_allow_html=True)
    
    df = st.session_state.data_manager.get_all_data()
    
    if df.empty:
        st.info("No data available yet. Start logging to see sleep analysis!")
        return
    
    st.markdown("### Sleep Patterns Throughout Cycle")
    
    period_starts = df[df['period_start'] == True]['date'].tolist()
    last_period = period_starts[-1] if period_starts else None
    
    if last_period:
        df['cycle_day'] = (pd.to_datetime(df['date']) - pd.to_datetime(last_period)).dt.days
        df['cycle_day'] = df['cycle_day'].apply(lambda x: x if x >= 0 else x + 28)
        
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=("Sleep Hours by Cycle Day", "Sleep Quality by Cycle Day")
        )
        
        fig.add_trace(
            go.Scatter(
                x=df['cycle_day'],
                y=df['sleep_hours'],
                mode='markers',
                marker=dict(color=df['pain_level'], colorscale='Reds', showscale=True),
                text=df['date'],
                name='Sleep Hours'
            ),
            row=1, col=1
        )
        
        quality_map = {'Very Poor': 1, 'Poor': 2, 'Fair': 3, 'Good': 4, 'Excellent': 5}
        df['sleep_quality_num'] = df['sleep_quality'].map(quality_map)
        
        fig.add_trace(
            go.Scatter(
                x=df['date'],
                y=df['sleep_quality_num'],
                mode='lines+markers',
                name='Sleep Quality'
            ),
            row=2, col=1
        )
        
        fig.update_layout(height=600, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("### 💤 Personalized Sleep Recommendations")
    
    if 'cycle_day' in df.columns:
        pre_data = df[df['cycle_day'].between(-7, 0)]
        during_data = df[df['cycle_day'].between(0, 5)]
        
        avg_sleep_pre = pre_data['sleep_hours'].mean() if not pre_data.empty else None
        avg_sleep_during = during_data['sleep_hours'].mean() if not during_data.empty else None
        
        if avg_sleep_pre and avg_sleep_during:
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Sleep before period", f"{avg_sleep_pre:.1f}h")
            with col2:
                st.metric("Sleep during period", f"{avg_sleep_during:.1f}h")
            
            if avg_sleep_during < avg_sleep_pre:
                st.info("💡 Your sleep decreases during your period. Try:")
                st.markdown("- Use a heating pad for cramps")
                st.markdown("- Practice relaxation techniques before bed")
                st.markdown("- Keep your bedroom cool and dark")

def show_settings():
    st.markdown("<h2 class='sub-header'>⚙️ Settings</h2>", unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["General", "Data Management", "About"])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🔔 Notifications")
            notify_period = st.checkbox("Notify before next period", value=True)
            if notify_period:
                days_before = st.slider("Days before notification", 1, 7, 3)
            
            notify_fertile = st.checkbox("Notify during fertile window", value=True)
        
        with col2:
            st.markdown("### 🎨 Appearance")
            theme = st.selectbox("Theme", ["Light", "Dark", "Auto"])
    
    with tab2:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📤 Export Data")
            if st.button("Export to CSV"):
                df = st.session_state.data_manager.get_all_data()
                if not df.empty:
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download CSV",
                        data=csv,
                        file_name=f"period_data_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv"
                    )
                else:
                    st.warning("No data to export")
        
        with col2:
            st.markdown("### 📥 Import Data")
            uploaded_file = st.file_uploader("Upload CSV file", type=['csv'])
            if uploaded_file is not None:
                temp_path = "temp_upload.csv"
                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                records = st.session_state.data_manager.import_from_csv(temp_path)
                
                import os
                os.remove(temp_path)
                
                if records > 0:
                    st.success(f"✅ Successfully imported {records} records!")
                    st.rerun()
                else:
                    st.error("❌ Failed to import data. Check file format.")
        
        st.markdown("### ⚠️ Danger Zone")
        if st.button("Clear All Data", type="secondary"):
            if st.session_state.data_manager.clear_data():
                st.success("All data cleared!")
                st.rerun()
            else:
                st.error("Failed to clear data")
    
    with tab3:
        st.markdown("### ℹ️ About")
        st.info(
            """
            **AI Period & Wellness Tracker v1.0**
            
            This AI-powered app helps you:
            - Track your menstrual cycle
            - Predict next period dates
            - Analyze pain patterns
            - Get personalized insights
            - Track nutrition and sleep
            
            Created with ❤️ using Streamlit and Machine Learning
            """
        )

def predict_today_pain(df):
    """Simple pain prediction for today"""
    if df.empty:
        return 0
    
    recent_pain = df['pain_level'].tail(7).mean()
    last_date = df['date'].iloc[-1]
    days_since_last = (datetime.now().date() - last_date).days
    
    if days_since_last <= 5:
        return min(10, recent_pain * 1.2)
    elif 15 <= days_since_last <= 21:
        return recent_pain * 0.8
    else:
        return recent_pain * 0.5

def create_cycle_visualization(df):
    """Create cycle visualization"""
    fig = make_subplots(
        rows=3, cols=1,
        subplot_titles=("Pain Level", "Sleep Hours", "Stress Level"),
        shared_xaxes=True
    )
    
    fig.add_trace(
        go.Scatter(
            x=df['date'],
            y=df['pain_level'],
            mode='lines+markers',
            name='Pain',
            line=dict(color='#ff4444')
        ),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=df['date'],
            y=df['sleep_hours'],
            mode='lines+markers',
            name='Sleep',
            line=dict(color='#33b5e5')
        ),
        row=2, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=df['date'],
            y=df['stress_level'],
            mode='lines+markers',
            name='Stress',
            line=dict(color='#ffbb33')
        ),
        row=3, col=1
    )
    
    fig.update_layout(height=600, showlegend=False)
    return fig

if __name__ == "__main__":
    main()