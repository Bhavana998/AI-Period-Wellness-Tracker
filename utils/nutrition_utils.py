import pandas as pd
import numpy as np
from datetime import datetime
from collections import Counter

def analyze_nutrition(food_df, period_df):
    """
    Analyze nutrition patterns in relation to menstrual cycle
    
    Parameters:
    - food_df: DataFrame with food entries
    - period_df: DataFrame with period entries
    
    Returns:
    - Dictionary with nutrition analysis insights
    """
    if food_df.empty or period_df.empty:
        return {}
    
    # Merge data on date
    merged = pd.merge(period_df, food_df, on='date', how='inner')
    if merged.empty:
        return {}
    
    analysis = {}
    
    # 1. Calculate correlations with pain
    nutrition_cols = ['calories', 'protein', 'fiber', 'sugar', 'water_intake', 'caffeine', 'alcohol']
    correlations = {}
    
    for col in nutrition_cols:
        if col in merged.columns:
            # Only calculate if we have enough data points
            valid_data = merged[[col, 'pain_level']].dropna()
            if len(valid_data) > 3:
                corr = valid_data[col].corr(valid_data['pain_level'])
                if not pd.isna(corr):
                    correlations[col] = round(corr, 2)
    
    analysis['pain_correlations'] = correlations
    
    # 2. Find optimal ranges for low pain days
    low_pain = merged[merged['pain_level'] <= 3]
    if len(low_pain) > 2:
        optimal_ranges = {}
        
        for col in ['calories', 'water_intake', 'fiber', 'protein']:
            if col in low_pain.columns:
                mean_val = low_pain[col].mean()
                std_val = low_pain[col].std()
                
                if not pd.isna(mean_val) and not pd.isna(std_val):
                    optimal_ranges[col] = {
                        'mean': round(mean_val, 1),
                        'optimal_range': (
                            round(max(0, mean_val - std_val), 1),
                            round(mean_val + std_val, 1)
                        ),
                        'unit': 'g' if col != 'water_intake' else 'cups',
                        'note': get_nutrition_note(col, mean_val)
                    }
        
        analysis['optimal_nutrition'] = optimal_ranges
    
    # 3. Analyze high pain days
    high_pain = merged[merged['pain_level'] >= 7]
    if len(high_pain) > 2:
        high_pain_analysis = {}
        
        for col in ['caffeine', 'alcohol', 'sugar']:
            if col in high_pain.columns:
                avg_high = high_pain[col].mean()
                avg_all = merged[col].mean()
                
                if not pd.isna(avg_high) and not pd.isna(avg_all):
                    if avg_high > avg_all * 1.2:  # 20% higher than average
                        high_pain_analysis[col] = {
                            'avg_on_high_pain': round(avg_high, 1),
                            'avg_normal': round(avg_all, 1),
                            'increase_percent': round((avg_high/avg_all - 1) * 100, 0)
                        }
        
        analysis['high_pain_factors'] = high_pain_analysis
    
    # 4. Craving patterns by cycle phase
    if 'cravings' in merged.columns and 'cycle_phase' in merged.columns:
        cravings_by_phase = {}
        
        for phase in merged['cycle_phase'].unique():
            phase_data = merged[merged['cycle_phase'] == phase]
            all_cravings = []
            
            for cravings in phase_data['cravings'].dropna():
                if cravings and cravings != 'None':
                    # Split by comma and clean
                    craving_list = [c.strip() for c in cravings.split(',') if c.strip()]
                    all_cravings.extend(craving_list)
            
            if all_cravings:
                craving_counts = Counter(all_cravings)
                top_cravings = craving_counts.most_common(3)
                cravings_by_phase[phase] = top_cravings
        
        analysis['cravings_by_phase'] = cravings_by_phase
    
    # 5. Hydration analysis
    if 'water_intake' in merged.columns:
        water_by_phase = merged.groupby('cycle_phase')['water_intake'].mean().to_dict()
        water_by_phase = {k: round(v, 1) for k, v in water_by_phase.items() if not pd.isna(v)}
        analysis['hydration_by_phase'] = water_by_phase
    
    # 6. Bloating analysis
    if 'bloating' in merged.columns:
        bloating_by_food = {}
        
        # Convert bloating to numeric
        bloating_map = {'None': 0, 'Mild': 1, 'Moderate': 2, 'Severe': 3}
        merged['bloating_score'] = merged['bloating'].map(bloating_map)
        
        # Find foods associated with bloating
        for idx, row in merged.iterrows():
            if row['bloating_score'] >= 2 and not pd.isna(row['food_items']):
                foods = [f.strip() for f in str(row['food_items']).split(',')]
                for food in foods:
                    if food not in bloating_by_food:
                        bloating_by_food[food] = []
                    bloating_by_food[food].append(row['bloating_score'])
        
        # Calculate average bloating score for each food
        food_bloating = {}
        for food, scores in bloating_by_food.items():
            if len(scores) >= 2:  # Only if seen multiple times
                avg_bloating = np.mean(scores)
                food_bloating[food] = round(avg_bloating, 1)
        
        if food_bloating:
            # Sort by bloating score
            analysis['bloating_triggers'] = dict(
                sorted(food_bloating.items(), key=lambda x: x[1], reverse=True)[:5]
            )
    
    return analysis

def get_meal_suggestions(cycle_phase, time_of_day):
    """
    Get meal suggestions based on cycle phase and time of day
    
    Parameters:
    - cycle_phase: Current cycle phase (Menstrual, Follicular, etc.)
    - time_of_day: Breakfast, Lunch, Dinner, or Snack
    
    Returns:
    - List of meal suggestions
    """
    suggestions = {
        'Menstrual': {
            'Breakfast': [
                'Iron-fortified cereal with berries and almonds',
                'Spinach and mushroom omelette with whole grain toast',
                'Warm oatmeal with banana, honey, and pumpkin seeds',
                'Smoothie with spinach, banana, almond milk, and chia seeds',
                'Quinoa breakfast bowl with berries and nuts'
            ],
            'Lunch': [
                'Lentil soup with a side of whole grain bread',
                'Quinoa salad with roasted vegetables and feta',
                'Grilled salmon with sweet potato and steamed greens',
                'Bean and vegetable burrito bowl with avocado',
                'Kale and beet salad with walnuts and goat cheese'
            ],
            'Dinner': [
                'Hearty bean and vegetable stew with brown rice',
                'Stir-fried tofu with broccoli, bell peppers, and ginger',
                'Warm pasta with tomato sauce, spinach, and mushrooms',
                'Baked chicken with roasted beets and quinoa',
                'Curried lentils with sweet potato and spinach'
            ],
            'Snack': [
                'Dark chocolate (2-3 squares) with almonds',
                'Trail mix with nuts, seeds, and dried cherries',
                'Warm ginger tea with honey',
                'Apple slices with almond butter',
                'Banana with a small handful of walnuts'
            ]
        },
        'Follicular': {
            'Breakfast': [
                'Greek yogurt parfait with honey and fresh berries',
                'Green smoothie bowl with spinach, banana, and granola',
                'Poached eggs with avocado toast and microgreens',
                'Chia seed pudding with mango and coconut flakes',
                'Fresh fruit salad with mint and lime juice'
            ],
            'Lunch': [
                'Grilled chicken salad with mixed greens and citrus vinaigrette',
                'Sushi rolls with avocado, cucumber, and carrot',
                'Vegetable and hummus wrap with sprouts',
                'Quinoa bowl with roasted asparagus and lemon',
                'Turkey and avocado sandwich on whole grain'
            ],
            'Dinner': [
                'Grilled fish with lemon, asparagus, and wild rice',
                'Vegetable stir-fry with lots of colorful veggies and tofu',
                'Light pasta primavera with fresh herbs',
                'Turkey and vegetable lettuce wraps',
                'Baked salmon with quinoa and steamed broccoli'
            ],
            'Snack': [
                'Fresh berries with a dollop of yogurt',
                'Rice cakes with hummus and cucumber slices',
                'Handful of almonds and an orange',
                'Vegetable sticks with tzatziki dip',
                'Apple slices with cinnamon'
            ]
        },
        'Ovulation': {
            'Breakfast': [
                'Green detox smoothie with spinach, pineapple, and ginger',
                'Chia pudding with kiwi and coconut',
                'Fresh fruit bowl with pomegranate seeds',
                'Oatmeal with turmeric, berries, and almonds',
                'Egg white scramble with spinach and tomatoes'
            ],
            'Lunch': [
                'Kale and quinoa salad with lemon-tahini dressing',
                'Vegetable soup with lentils and fresh herbs',
                'Light sandwich with turkey, avocado, and sprouts',
                'Buddha bowl with leafy greens, chickpeas, and tahini',
                'Arugula salad with grilled chicken and pomegranate'
            ],
            'Dinner': [
                'Steamed veggies with grilled tofu and ginger sauce',
                'White fish with steamed broccoli and lemon',
                'Light coconut curry with vegetables and brown rice',
                'Zucchini noodles with pesto and cherry tomatoes',
                'Grilled shrimp with asparagus and quinoa'
            ],
            'Snack': [
                'Celery sticks with almond butter',
                'Fresh berries or cherries',
                'Green tea with a touch of honey',
                'Handful of walnuts and goji berries',
                'Cucumber slices with lemon and salt'
            ]
        },
        'Luteal': {
            'Breakfast': [
                'Warm oatmeal with nuts, banana, and cinnamon',
                'Whole grain toast with peanut butter and sliced banana',
                'Protein smoothie with spinach, almond butter, and dates',
                'Scrambled eggs with sweet potato hash',
                'Buckwheat pancakes with berries'
            ],
            'Lunch': [
                'Sweet potato and black bean bowl with avocado',
                'Brown rice bowl with roasted vegetables and tahini',
                'Hearty minestrone soup with whole grain bread',
                'Quinoa salad with roasted sweet potato and pumpkin seeds',
                'Warm grain bowl with mushrooms and kale'
            ],
            'Dinner': [
                'Complex carb bowl with roasted veggies and chickpeas',
                'Baked sweet potato with black beans and salsa',
                'Whole grain pasta with roasted vegetables',
                'Lentil and vegetable shepherd\'s pie',
                'Stuffed bell peppers with quinoa and vegetables'
            ],
            'Snack': [
                'Banana with almond butter',
                'Dark chocolate (2 squares) with sea salt',
                'Handful of pumpkin seeds',
                'Chamomile tea with honey',
                'Dates stuffed with almond butter'
            ]
        },
        'Late Luteal': {
            'Breakfast': [
                'Warm oatmeal with banana and walnuts',
                'Scrambled eggs with whole grain toast',
                'Smoothie with almond butter, banana, and dates',
                'Whole grain cereal with warm milk',
                'Apple cinnamon oatmeal'
            ],
            'Lunch': [
                'Comforting tomato soup with grilled cheese',
                'Mashed potato bowl with roasted vegetables',
                'Warm grain bowl with mushrooms',
                'Grilled cheese with tomato soup',
                'Creamy vegetable soup with bread'
            ],
            'Dinner': [
                'Warm pasta with creamy mushroom sauce',
                'Lentil shepherd\'s pie with mashed potatoes',
                'Roasted vegetable bowl with tahini',
                'Mac and cheese with broccoli',
                'Creamy risotto with mushrooms'
            ],
            'Snack': [
                'Warm milk with honey and cinnamon',
                'Dark chocolate',
                'Banana',
                'Herbal tea with honey',
                'Small bowl of warm oatmeal'
            ]
        },
        'Pre-period': {
            'Breakfast': [
                'Oatmeal with banana and honey',
                'Scrambled eggs with toast',
                'Smoothie with dates and almond milk',
                'Warm cereal with berries',
                'French toast with cinnamon'
            ],
            'Lunch': [
                'Warm soup with bread',
                'Comfort bowl with rice and vegetables',
                'Simple sandwich with soup',
                'Mashed potatoes with gravy',
                'Warm grain bowl'
            ],
            'Dinner': [
                'Comforting pasta dish',
                'Shepherd\'s pie',
                'Warm stew with bread',
                'Casserole with vegetables',
                'Rice bowl with warm toppings'
            ],
            'Snack': [
                'Warm milk',
                'Dark chocolate',
                'Banana',
                'Herbal tea',
                'Small bowl of cereal'
            ]
        },
        'Unknown': {
            'Breakfast': [
                'Balanced breakfast with protein, healthy fats, and fiber',
                'Fresh fruit with Greek yogurt and granola',
                'Whole grain toast with avocado and eggs',
                'Green smoothie with spinach and fruit',
                'Oatmeal with berries and nuts'
            ],
            'Lunch': [
                'Balanced meal with lean protein and colorful vegetables',
                'Grain bowl with roasted vegetables and chickpeas',
                'Hearty soup with a side salad',
                'Wrap with lean protein and fresh veggies',
                'Quinoa salad with vegetables and feta'
            ],
            'Dinner': [
                'Lean protein with roasted vegetables',
                'Whole grain with sautéed vegetables',
                'Stir-fry with tofu or chicken and lots of veggies',
                'Fish with quinoa and steamed greens',
                'Vegetable curry with brown rice'
            ],
            'Snack': [
                'Fresh seasonal fruit',
                'Handful of mixed nuts',
                'Greek yogurt with honey',
                'Vegetable sticks with hummus',
                'Apple with nut butter'
            ]
        }
    }
    
    # Return suggestions for the given phase and time of day
    phase_suggestions = suggestions.get(cycle_phase, suggestions['Unknown'])
    return phase_suggestions.get(time_of_day, phase_suggestions.get('Breakfast', []))

def calculate_nutrition_score(food_entry):
    """
    Calculate a nutrition score for a food entry (0-100)
    
    Parameters:
    - food_entry: Dictionary with food data
    
    Returns:
    - Nutrition score (0-100)
    """
    score = 50  # Start at neutral
    
    # Factors that increase score (healthy)
    # Fiber (good for digestion and hormone balance)
    if food_entry.get('fiber', 0) > 8:
        score += 15
    elif food_entry.get('fiber', 0) > 5:
        score += 10
    elif food_entry.get('fiber', 0) > 3:
        score += 5
    
    # Protein (important for hormone production)
    if food_entry.get('protein', 0) > 25:
        score += 10
    elif food_entry.get('protein', 0) > 15:
        score += 7
    elif food_entry.get('protein', 0) > 10:
        score += 5
    
    # Water intake (hydration)
    if food_entry.get('water_intake', 0) > 8:
        score += 15
    elif food_entry.get('water_intake', 0) > 6:
        score += 10
    elif food_entry.get('water_intake', 0) > 4:
        score += 5
    
    # Healthy fats (important for hormone balance)
    if food_entry.get('fat', 0) < 30:  # Not too much fat
        if 'avocado' in str(food_entry.get('food_items', '')).lower() or \
           'nuts' in str(food_entry.get('food_items', '')).lower() or \
           'salmon' in str(food_entry.get('food_items', '')).lower():
            score += 5
    
    # Factors that decrease score (unhealthy)
    # Sugar
    if food_entry.get('sugar', 0) > 30:
        score -= 20
    elif food_entry.get('sugar', 0) > 20:
        score -= 15
    elif food_entry.get('sugar', 0) > 10:
        score -= 5
    
    # Caffeine (can increase anxiety and cramps)
    if food_entry.get('caffeine', 0) > 3:
        score -= 15
    elif food_entry.get('caffeine', 0) > 1:
        score -= 5
    
    # Alcohol (can worsen PMS symptoms)
    if food_entry.get('alcohol', 0) > 2:
        score -= 20
    elif food_entry.get('alcohol', 0) > 1:
        score -= 10
    
    # Processed foods (simple heuristic based on keywords)
    food_text = str(food_entry.get('food_items', '')).lower()
    processed_keywords = ['processed', 'packaged', 'instant', 'fast food', 'soda', 'chips']
    for keyword in processed_keywords:
        if keyword in food_text:
            score -= 5
            break
    
    # Ensure score is within 0-100 range
    return max(0, min(100, score))

def identify_trigger_foods(df, food_df):
    """
    Identify foods that may trigger pain or symptoms
    
    Parameters:
    - df: Period data DataFrame
    - food_df: Food data DataFrame
    
    Returns:
    - Dictionary with potential trigger foods
    """
    if df.empty or food_df.empty:
        return {}
    
    # Merge data
    merged = pd.merge(df, food_df, on='date', how='inner')
    if merged.empty:
        return {}
    
    triggers = {}
    
    # 1. Look at high pain days (pain >= 7)
    high_pain = merged[merged['pain_level'] >= 7]
    if len(high_pain) >= 2:
        # Check common foods on high pain days
        all_foods = []
        for foods in high_pain['food_items'].dropna():
            if isinstance(foods, str):
                # Split by comma and clean
                food_list = [f.strip().lower() for f in foods.split(',') if f.strip()]
                all_foods.extend(food_list)
        
        if all_foods:
            food_counts = Counter(all_foods)
            total_days = len(high_pain)
            
            # Find foods that appear on >40% of high pain days
            potential_triggers = [
                {'food': food, 'frequency': f"{count}/{total_days} days", 'percentage': round(count/total_days*100, 1)}
                for food, count in food_counts.items() 
                if count / total_days > 0.4
            ]
            
            if potential_triggers:
                triggers['high_pain_triggers'] = potential_triggers
    
    # 2. Look at bloating triggers
    if 'bloating' in merged.columns:
        # Convert bloating to numeric
        bloating_map = {'None': 0, 'Mild': 1, 'Moderate': 2, 'Severe': 3}
        merged['bloating_score'] = merged['bloating'].map(bloating_map)
        
        high_bloating = merged[merged['bloating_score'] >= 2]
        if len(high_bloating) >= 2:
            bloating_foods = []
            for foods in high_bloating['food_items'].dropna():
                if isinstance(foods, str):
                    food_list = [f.strip().lower() for f in foods.split(',') if f.strip()]
                    bloating_foods.extend(food_list)
            
            if bloating_foods:
                food_counts = Counter(bloating_foods)
                total_bloating_days = len(high_bloating)
                
                bloating_triggers = [
                    {'food': food, 'frequency': f"{count}/{total_bloating_days} days"}
                    for food, count in food_counts.items() 
                    if count / total_bloating_days > 0.4
                ]
                
                if bloating_triggers:
                    triggers['bloating_triggers'] = bloating_triggers
    
    # 3. Correlation between specific foods and symptoms
    # This is a simplified version - in reality you'd want more sophisticated analysis
    food_symptom_corr = {}
    
    # Get all unique foods
    all_foods = set()
    for foods in merged['food_items'].dropna():
        if isinstance(foods, str):
            all_foods.update([f.strip().lower() for f in foods.split(',') if f.strip()])
    
    for food in all_foods:
        # Days with this food
        food_days = merged[merged['food_items'].str.contains(food, case=False, na=False)]
        if len(food_days) >= 2:
            avg_pain_with_food = food_days['pain_level'].mean()
            avg_pain_without = merged[~merged['food_items'].str.contains(food, case=False, na=False)]['pain_level'].mean()
            
            if not pd.isna(avg_pain_with_food) and not pd.isna(avg_pain_without):
                difference = avg_pain_with_food - avg_pain_without
                if abs(difference) > 1:  # More than 1 point difference
                    food_symptom_corr[food] = {
                        'avg_pain_with': round(avg_pain_with_food, 1),
                        'avg_pain_without': round(avg_pain_without, 1),
                        'difference': round(difference, 1),
                        'effect': 'Worsens' if difference > 0 else 'May help'
                    }
    
    if food_symptom_corr:
        triggers['food_symptom_correlations'] = food_symptom_corr
    
    return triggers

def get_nutrition_note(nutrient, value):
    """
    Get a note about a nutrient value
    
    Parameters:
    - nutrient: Name of the nutrient
    - value: Average value
    
    Returns:
    - String with explanation
    """
    notes = {
        'calories': {
            'low': 'You might need more energy during this phase',
            'medium': 'Good calorie intake for maintaining energy',
            'high': 'Higher calorie intake may be needed during luteal phase'
        },
        'fiber': {
            'low': 'Fiber helps with digestion and hormone balance',
            'medium': 'Good fiber intake for gut health',
            'high': 'Excellent fiber intake! This helps eliminate excess estrogen'
        },
        'water_intake': {
            'low': 'Try to increase water intake, especially during periods',
            'medium': 'Good hydration',
            'high': 'Excellent hydration! This helps with bloating'
        },
        'protein': {
            'low': 'Protein is important for hormone production',
            'medium': 'Good protein intake for hormone health',
            'high': 'Great protein intake!'
        }
    }
    
    # Determine if value is low, medium, or high
    ranges = {
        'calories': {'low': 1500, 'medium': 2000, 'high': 2500},
        'fiber': {'low': 15, 'medium': 25, 'high': 35},
        'water_intake': {'low': 4, 'medium': 6, 'high': 8},
        'protein': {'low': 40, 'medium': 60, 'high': 80}
    }
    
    if nutrient in ranges:
        if value < ranges[nutrient]['low']:
            return notes[nutrient]['low']
        elif value < ranges[nutrient]['medium']:
            return notes[nutrient]['medium']
        else:
            return notes[nutrient]['high']
    
    return ""

def suggest_meals_for_symptoms(symptoms, cycle_phase):
    """
    Suggest meals based on specific symptoms
    
    Parameters:
    - symptoms: List of symptoms (cramps, bloating, fatigue, etc.)
    - cycle_phase: Current cycle phase
    
    Returns:
    - Dictionary with meal suggestions targeting symptoms
    """
    suggestions = {}
    
    symptom_foods = {
        'cramps': [
            'Ginger tea - natural anti-inflammatory',
            'Chamomile tea - helps relax muscles',
            'Bananas - rich in potassium and magnesium',
            'Dark chocolate - magnesium for muscle relaxation',
            'Salmon - omega-3s reduce inflammation'
        ],
        'bloating': [
            'Cucumber - natural diuretic',
            'Asparagus - helps reduce bloating',
            'Pineapple - bromelain reduces inflammation',
            'Peppermint tea - soothes digestion',
            'Fennel tea - reduces gas and bloating'
        ],
        'fatigue': [
            'Oatmeal - complex carbs for sustained energy',
            'Spinach - iron for energy',
            'Eggs - B vitamins for energy',
            'Quinoa - complete protein and complex carbs',
            'Beans - iron and protein'
        ],
        'headache': [
            'Magnesium-rich foods (almonds, spinach)',
            'Stay hydrated with water',
            'Ginger tea - natural pain relief',
            'Small amounts of caffeine (if helpful for you)',
            'Fruits with high water content'
        ],
        'anxiety': [
            'Chamomile tea - calming',
            'Dark chocolate - magnesium for relaxation',
            'Oats - complex carbs stabilize mood',
            'Avocado - healthy fats for brain health',
            'Berries - antioxidants reduce stress'
        ],
        'cravings': {
            'sweet': [
                'Fresh fruit with yogurt',
                'Dates stuffed with almond butter',
                'Dark chocolate (70%+ cocoa)',
                'Berry smoothie',
                'Baked apple with cinnamon'
            ],
            'salty': [
                'Roasted chickpeas with sea salt',
                'Nuts with a pinch of salt',
                'Rice cakes with avocado and salt',
                'Olives',
                'Vegetable sticks with salted hummus'
            ],
            'carbs': [
                'Sweet potato with cinnamon',
                'Whole grain toast with almond butter',
                'Oatmeal with fruit',
                'Quinoa bowl with vegetables',
                'Brown rice with roasted veggies'
            ]
        }
    }
    
    for symptom in symptoms:
        if symptom in symptom_foods:
            if symptom == 'cravings':
                # Handle cravings separately
                pass
            else:
                suggestions[symptom] = symptom_foods[symptom][:3]  # Top 3 suggestions
    
    # Add phase-appropriate base meals
    base_meals = get_meal_suggestions(cycle_phase, 'Dinner')[:2]
    suggestions['base_meals'] = base_meals
    
    return suggestions

def calculate_weekly_nutrition_summary(food_df):
    """
    Calculate weekly nutrition summary
    
    Parameters:
    - food_df: Food data DataFrame
    
    Returns:
    - Dictionary with weekly nutrition summary
    """
    if food_df.empty:
        return {}
    
    # Get last 7 days
    food_df = food_df.copy()
    food_df['date'] = pd.to_datetime(food_df['date'])
    last_week = food_df[food_df['date'] >= food_df['date'].max() - pd.Timedelta(days=7)]
    
    if last_week.empty:
        return {}
    
    summary = {}
    
    # Daily averages
    daily_agg = last_week.groupby('date').agg({
        'calories': 'sum',
        'protein': 'sum',
        'fiber': 'sum',
        'water_intake': 'sum'
    }).mean()
    
    summary['daily_averages'] = {
        'calories': round(daily_agg.get('calories', 0), 0),
        'protein': round(daily_agg.get('protein', 0), 1),
        'fiber': round(daily_agg.get('fiber', 0), 1),
        'water': round(daily_agg.get('water_intake', 0), 1)
    }
    
    # Trends
    daily_trend = last_week.groupby('date')['calories'].sum().reset_index()
    if len(daily_trend) > 1:
        trend = np.polyfit(range(len(daily_trend)), daily_trend['calories'], 1)[0]
        summary['calorie_trend'] = 'increasing' if trend > 0 else 'decreasing' if trend < 0 else 'stable'
    
    # Most common foods
    all_foods = []
    for foods in last_week['food_items'].dropna():
        if isinstance(foods, str):
            all_foods.extend([f.strip() for f in foods.split(',') if f.strip()])
    
    if all_foods:
        food_counts = Counter(all_foods)
        summary['top_foods'] = food_counts.most_common(5)
    
    return summary