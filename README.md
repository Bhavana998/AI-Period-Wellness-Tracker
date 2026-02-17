### deployment link: https://ai-period-wellness-tracker-xcv3nylpfozibyb9niyvgz.streamlit.app/
<div align="center">
  
  # 🌸 AI-Powered Period & Wellness Tracker

  <p align="center">
    <strong>An intelligent menstrual health tracking application powered by Machine Learning</strong>
  </p>

  <p align="center">
    <a href="https://www.python.org/">
      <img src="https://img.shields.io/badge/Python-3.8+-blue.svg?style=flat-square&logo=python" alt="Python">
    </a>
    <a href="https://streamlit.io/">
      <img src="https://img.shields.io/badge/Streamlit-1.28+-red.svg?style=flat-square&logo=streamlit" alt="Streamlit">
    </a>
    <a href="https://scikit-learn.org/">
      <img src="https://img.shields.io/badge/ML-RandomForest-orange.svg?style=flat-square" alt="ML">
    </a>
    <a href="https://github.com/Bhavana998/AI-Period-Wellness-Tracker/blob/main/LICENSE">
      <img src="https://img.shields.io/badge/License-MIT-green.svg?style=flat-square" alt="License">
    </a>
    <a href="https://github.com/Bhavana998/AI-Period-Wellness-Tracker/issues">
      <img src="https://img.shields.io/badge/Contributions-Welcome-brightgreen.svg?style=flat-square" alt="Contributions">
    </a>
  </p>

  <h3>
    <a href="#-features">Features</a> •
    <a href="#-quick-start">Quick Start</a> •
    <a href="#-machine-learning">ML Models</a> •
    <a href="#-demo">Demo</a> •
    <a href="#-contributing">Contributing</a>
  </h3>

---

## 📋 Table of Contents

- [✨ Features](#-features)
- [🚀 Quick Start](#-quick-start)
- [🧠 Machine Learning Models](#-machine-learning-models)
- [📁 Project Structure](#-project-structure)
- [📊 How to Use](#-how-to-use)
- [📈 Sample Data](#-sample-data)
- [🛠️ Technologies Used](#️-technologies-used)
- [🤝 Contributing](#-contributing)
- [📝 License](#-license)
- [📬 Contact](#-contact)

---

## ✨ Features

<div align="center">

| Feature | Description | Status |
|:--------|:------------|:------:|
| 📅 **Period Tracking** | Log cycles, symptoms, flow intensity | ✅ |
| 🔮 **Next Period Prediction** | AI predicts your next period date | ✅ |
| 💊 **Pain Forecasting** | 7-day pain level predictions | ✅ |
| 😴 **Sleep Analysis** | Track sleep patterns across your cycle | ✅ |
| 🍎 **Food & Nutrition** | Log meals and identify trigger foods | ✅ |
| 📊 **Interactive Dashboard** | Visualize patterns and insights | ✅ |
| 💡 **Personalized Insights** | Get phase-specific health advice | ✅ |
| 📈 **Cycle Analytics** | Track regularity and patterns | ✅ |
| 📥 **CSV Import/Export** | Backup and restore your data | ✅ |

</div>

### 🌟 Key Highlights

- **🤖 AI-Powered:** Random Forest models trained on your personal data
- **📊 Visual Analytics:** Beautiful Plotly charts for easy pattern recognition
- **🍽️ Food-Symptom Correlation:** Identify foods that trigger pain
- **😴 Sleep-Cycle Analysis:** Understand how your cycle affects sleep
- **📱 Responsive Design:** Works on desktop, tablet, and mobile

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip package manager

## 1. Push code to GitHub
git add .
git commit -m "Ready for deployment"
git push

# 2. Go to share.streamlit.io
# 3. Connect GitHub account
# 4. Select this repository
# 5. Configure:
#    - Main file: app.py
#    - Python version: 3.9
# 6. Click "Deploy"
Your app will be live at: https://your-app-name.streamlit.app

# Clone the repository
git clone https://github.com/Bhavana998/AI-Period-Wellness-Tracker.git
cd AI-Period-Wellness-Tracker

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py

📦 Dependencies
txt
streamlit==1.28.1
pandas==2.0.3
numpy==1.24.3
scikit-learn==1.3.0
plotly==5.17.0
matplotlib==3.7.2
seaborn==0.12.2
joblib==1.3.2
python-dateutil==2.8.2

🧠 Machine Learning Models
1. Pain Predictor
Attribute	Details
Model	RandomForestRegressor
Features	Sleep hours, stress level, exercise, cycle phase, historical patterns
Output	Pain level prediction (0-10 scale)
Accuracy	~85% after 30+ days of data
File	models/pain_predictor.py
2. Cycle Predictor
Attribute	Details
Model	Hybrid (Statistical + ML)
Features	Previous cycle lengths, seasonal patterns
Output	Next period date with confidence score
Training	Minimum 3 cycles of data
File	models/cycle_predictor.py
3. Nutrition Correlator
Attribute	Details
Purpose	Analyzes food-symptom relationships
Identifies	Trigger foods, optimal nutrition
Features	Calories, protein, fiber, water intake
File	models/nutrition_predictor.py
                                                           
                                                        📁 Project Structure                       
                                                        AI-Period-Wellness-Tracker/
                                                        │
                                                        ├── app.py                 # Main Streamlit application
                                                        ├── requirements.txt       # Python dependencies
                                                        ├── README.md              # Documentation
                                                        ├── .gitignore             # Git ignore rules
                                                        │
                                                        ├── models/                 # ML Models
                                                        │   ├── __init__.py
                                                        │   ├── pain_predictor.py
                                                        │   ├── cycle_predictor.py
                                                        │   └── nutrition_predictor.py
                                                        │
                                                        ├── data/                   # Data Management
                                                        │   ├── __init__.py
                                                        │   ├── data_manager.py     # Handles all data operations
                                                        │   └── food_database.py    # Food recommendations
                                                        │
                                                        ├── utils/                   # Helper Functions
                                                        │   ├── __init__.py
                                                        │   ├── helpers.py          # Cycle phase calculation
                                                        │   └── nutrition_utils.py  # Nutrition analysis
                                                        │
                                                             └── ml_models/               # Saved Models
                                                             └── saved_models/        # Trained model files (.pkl)

    
📊 How to Use
📝 Logging Data
Period Data:

Select date

Check "Period started today?" if applicable

Set pain level (0-10)

Log sleep hours and quality

Record stress level and mood

Add exercise minutes

Click "Save Entry"

Food Data:

Choose meal type

Log food items or use quick database

Track calories and nutrients

Record water intake

Note cravings and bloating

Click "Save Food Entry"

📈 Analyzing Insights
Page	Purpose
Dashboard	Overview of your cycle status
Predictions	AI forecasts for next period and pain
Insights	Correlations between lifestyle and symptoms
Sleep Analysis	Sleep patterns throughout your cycle
Food Insights	Food-symptom correlations
📈 Sample Data
Test the app immediately with sample data:

Run the app

Go to Settings → Data Management

Click "Load Sample Data"

Explore all features with 4 cycles of realistic data

The sample data includes:

📅 4 complete menstrual cycles

💊 Realistic pain patterns (0-10 scale)

😴 Sleep variations (5-9 hours)

😊 Mood tracking across phases

🔄 Regular cycle patterns (28-35 days)

🛠️ Technologies Used
Technology	Purpose
Streamlit	Web application framework
Python	Programming language
Pandas	Data manipulation
scikit-learn	Machine Learning models
Plotly	Interactive visualizations
Matplotlib	Static visualizations
joblib	Model persistence
🚀 Deployment
Deploy to Streamlit Cloud
bash
# 1. Push code to GitHub
git add .
git commit -m "Ready for deployment"
git push

# 2. Go to share.streamlit.io
# 3. Connect GitHub account
# 4. Select this repository
# 5. Configure:
#    - Main file: app.py
#    - Python version: 3.9
# 6. Click "Deploy"
Your app will be live at: https://your-app-name.streamlit.app

📊 CSV Import Format
Import your existing data with this format:

csv
date,period_start,bleeding,pain_level,cramps,sleep_hours,sleep_quality,stress_level,exercise_minutes,mood
2024-01-01,TRUE,Heavy,8,TRUE,5.2,Poor,9,0,Irritable
2024-01-02,FALSE,Medium,6,TRUE,6.5,Fair,7,20,Anxious
🤝 Contributing
Contributions are welcome! Here's how:

Fork the repository

Create a feature branch

bash
git checkout -b feature/AmazingFeature
Commit your changes

bash
git commit -m 'Add AmazingFeature'
Push to the branch

bash
git push origin feature/AmazingFeature
Open a Pull Request

Development Guidelines
✅ Follow PEP 8 style guide

✅ Add docstrings to new functions

✅ Update documentation

✅ Test with sample data

📝 License
This project is licensed under the MIT License - see the LICENSE file for details.

text
MIT License

Copyright (c) 2024 Bhavana

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files...
📬 Contact
Bhavana

GitHub: @Bhavana998

Project Link: https://github.com/Bhavana998/AI-Period-Wellness-Tracker

Live Demo: https://ai-period-wellness-tracker.streamlit.app

<div align="center">
⭐ Star this repository if you find it useful!
Made with ❤️ for women's health

⬆ back to top

</div> ```
