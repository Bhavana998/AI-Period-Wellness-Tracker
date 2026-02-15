import pandas as pd
import numpy as np

class FoodDatabase:
    """Common foods with nutritional information"""
    
    # Food categories beneficial for menstrual health
    PERIOD_FRIENDLY_FOODS = {
        'Iron Rich': [
            {'name': 'Spinach', 'calories': 23, 'protein': 2.9, 'carbs': 3.6, 'fat': 0.4, 'fiber': 2.2, 'iron': 2.7},
            {'name': 'Lentils', 'calories': 116, 'protein': 9, 'carbs': 20, 'fat': 0.4, 'fiber': 7.9, 'iron': 3.3},
            {'name': 'Lean Beef', 'calories': 250, 'protein': 26, 'carbs': 0, 'fat': 15, 'fiber': 0, 'iron': 2.5},
            {'name': 'Dark Chocolate', 'calories': 150, 'protein': 2, 'carbs': 13, 'fat': 10, 'fiber': 3, 'iron': 3.4},
            {'name': 'Quinoa', 'calories': 120, 'protein': 4, 'carbs': 21, 'fat': 1.9, 'fiber': 2.8, 'iron': 1.5},
            {'name': 'Tofu', 'calories': 76, 'protein': 8, 'carbs': 1.9, 'fat': 4.8, 'fiber': 0.3, 'iron': 1.1}
        ],
        'Magnesium Rich': [
            {'name': 'Bananas', 'calories': 105, 'protein': 1.3, 'carbs': 27, 'fat': 0.4, 'fiber': 3.1, 'magnesium': 32},
            {'name': 'Almonds', 'calories': 164, 'protein': 6, 'carbs': 6, 'fat': 14, 'fiber': 3.5, 'magnesium': 80},
            {'name': 'Avocado', 'calories': 160, 'protein': 2, 'carbs': 8.5, 'fat': 14.7, 'fiber': 6.7, 'magnesium': 29},
            {'name': 'Pumpkin Seeds', 'calories': 151, 'protein': 7, 'carbs': 5, 'fat': 13, 'fiber': 1.7, 'magnesium': 150},
            {'name': 'Dark Chocolate', 'calories': 150, 'protein': 2, 'carbs': 13, 'fat': 10, 'fiber': 3, 'magnesium': 64},
            {'name': 'Black Beans', 'calories': 132, 'protein': 8.9, 'carbs': 23.7, 'fat': 0.5, 'fiber': 8.7, 'magnesium': 70}
        ],
        'Anti-inflammatory': [
            {'name': 'Salmon', 'calories': 208, 'protein': 20, 'carbs': 0, 'fat': 13, 'fiber': 0, 'omega3': 2.3},
            {'name': 'Turmeric', 'calories': 8, 'protein': 0.2, 'carbs': 1.4, 'fat': 0.2, 'fiber': 0.2, 'curcumin': 0.1},
            {'name': 'Ginger', 'calories': 4, 'protein': 0.1, 'carbs': 1, 'fat': 0, 'fiber': 0.1, 'gingerol': 0.05},
            {'name': 'Blueberries', 'calories': 84, 'protein': 1.1, 'carbs': 21, 'fat': 0.5, 'fiber': 3.6, 'antioxidants': 1},
            {'name': 'Walnuts', 'calories': 185, 'protein': 4.3, 'carbs': 3.9, 'fat': 18.5, 'fiber': 1.9, 'omega3': 2.5},
            {'name': 'Green Tea', 'calories': 2, 'protein': 0.2, 'carbs': 0, 'fat': 0, 'fiber': 0, 'antioxidants': 1}
        ],
        'Hydrating': [
            {'name': 'Watermelon', 'calories': 46, 'protein': 0.9, 'carbs': 11.5, 'fat': 0.2, 'fiber': 0.6, 'water': 92},
            {'name': 'Cucumber', 'calories': 8, 'protein': 0.3, 'carbs': 1.9, 'fat': 0.1, 'fiber': 0.5, 'water': 96},
            {'name': 'Coconut Water', 'calories': 46, 'protein': 1.7, 'carbs': 9, 'fat': 0.5, 'fiber': 0, 'electrolytes': 1},
            {'name': 'Strawberries', 'calories': 49, 'protein': 1, 'carbs': 11.7, 'fat': 0.5, 'fiber': 3, 'water': 91},
            {'name': 'Celery', 'calories': 6, 'protein': 0.3, 'carbs': 1.2, 'fat': 0.1, 'fiber': 0.6, 'water': 95},
            {'name': 'Oranges', 'calories': 62, 'protein': 1.2, 'carbs': 15, 'fat': 0.2, 'fiber': 3.1, 'water': 86}
        ],
        'Complex Carbs': [
            {'name': 'Sweet Potato', 'calories': 103, 'protein': 2.3, 'carbs': 24, 'fat': 0.2, 'fiber': 4, 'vitamin_a': 1},
            {'name': 'Oats', 'calories': 158, 'protein': 5.5, 'carbs': 27, 'fat': 3.2, 'fiber': 4.1, 'beta_glucan': 1},
            {'name': 'Brown Rice', 'calories': 216, 'protein': 5, 'carbs': 45, 'fat': 1.8, 'fiber': 3.5, 'magnesium': 1},
            {'name': 'Whole Wheat Bread', 'calories': 69, 'protein': 3.6, 'carbs': 12, 'fat': 1.1, 'fiber': 1.9, 'b_vitamins': 1}
        ]
    }
    
    # Foods to avoid during period
    FOODS_TO_AVOID = {
        'High Sodium': ['Processed foods', 'Canned soups', 'Fast food', 'Chips', 'Frozen meals'],
        'High Sugar': ['Soda', 'Candy', 'Pastries', 'Sweet cereals', 'Ice cream'],
        'Caffeine': ['Coffee', 'Energy drinks', 'Black tea', 'Soda', 'Dark chocolate'],
        'Dairy': ['Milk', 'Cheese', 'Ice cream', 'Yogurt', 'Butter'],
        'Processed': ['Fast food', 'Packaged snacks', 'Processed meats', 'Instant noodles']
    }
    
    @classmethod
    def get_recommendations(cls, cycle_phase):
        """Get food recommendations based on cycle phase"""
        recommendations = {
            'Menstrual': {
                'focus': ['Iron-rich foods', 'Hydrating foods', 'Warm foods', 'Vitamin C'],
                'foods': ['Spinach', 'Lentils', 'Dark chocolate', 'Warm soups', 'Ginger tea', 'Beets', 'Berries'],
                'avoid': ['Caffeine', 'Salty foods', 'Dairy', 'Fried foods']
            },
            'Follicular': {
                'focus': ['Light proteins', 'Fermented foods', 'Fresh veggies', 'Complex carbs'],
                'foods': ['Salmon', 'Eggs', 'Yogurt', 'Leafy greens', 'Berries', 'Quinoa', 'Avocado'],
                'avoid': ['Heavy processed foods', 'Excess sugar']
            },
            'Ovulation': {
                'focus': ['Anti-inflammatory', 'Fiber-rich', 'Liver-supporting', 'Antioxidants'],
                'foods': ['Cruciferous veggies', 'Turmeric', 'Green tea', 'Berries', 'Walnuts', 'Pineapple'],
                'avoid': ['Alcohol', 'Sugar', 'Processed oils', 'Red meat']
            },
            'Luteal': {
                'focus': ['Complex carbs', 'Magnesium-rich', 'B-vitamins', 'Healthy fats'],
                'foods': ['Sweet potatoes', 'Nuts', 'Dark chocolate', 'Bananas', 'Oats', 'Pumpkin seeds'],
                'avoid': ['Salt', 'Sugar', 'Caffeine', 'Alcohol', 'Simple carbs']
            },
            'Late Luteal': {
                'focus': ['Magnesium', 'Calcium', 'B6 vitamins', 'Comfort foods'],
                'foods': ['Almonds', 'Leafy greens', 'Bananas', 'Oatmeal', 'Dark chocolate', 'Chamomile tea'],
                'avoid': ['Caffeine', 'Salty foods', 'Processed foods']
            },
            'Pre-period': {
                'focus': ['Magnesium', 'Complex carbs', 'Calcium', 'Hydration'],
                'foods': ['Almonds', 'Oats', 'Bananas', 'Leafy greens', 'Warm milk', 'Dark chocolate'],
                'avoid': ['Caffeine', 'Alcohol', 'Salty foods', 'Sugar']
            },
            'Unknown': {
                'focus': ['Balanced diet', 'Whole foods', 'Hydration', 'Regular meals'],
                'foods': ['Lean proteins', 'Whole grains', 'Fruits', 'Vegetables', 'Healthy fats'],
                'avoid': ['Processed foods', 'Excess sugar', 'Excess caffeine']
            }
        }
        return recommendations.get(cycle_phase, recommendations['Unknown'])
    
    @classmethod
    def search_food(cls, query):
        """Search for a food in the database"""
        results = []
        query = query.lower()
        
        for category, foods in cls.PERIOD_FRIENDLY_FOODS.items():
            for food in foods:
                if query in food['name'].lower():
                    results.append({
                        'name': food['name'],
                        'category': category,
                        'nutrition': food
                    })
        
        return results