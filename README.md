# AI-Driven Business Intelligence Platform

A smart analytics platform that combines automated data analysis, natural language querying, and machine learning models to simplify business insights.

Developed by **Amrita Kumari**

---

## Overview

This project allows users to upload datasets and instantly perform:

- Automated Exploratory Data Analysis (EDA)
- Natural Language to SQL querying
- Sales/metric forecasting
- Customer churn prediction
- AI-generated reports

The goal is to reduce manual effort in data analysis and make insights accessible even to non-technical users.

---

## Key Features

### 1. Automated EDA
- Detects missing values, data types, and distributions
- Generates correlation insights
- Works with CSV and Excel files

### 2. Natural Language to SQL
- Ask questions in plain English
- Converts queries into SQL automatically
- Executes on uploaded dataset

### 3. Forecasting Module
- Predicts future values for numeric columns
- Uses machine learning for better accuracy
- Provides performance metrics

### 4. Churn Prediction
- Identifies customers likely to leave
- Outputs probability-based risk levels
- Useful for retention strategies

### 5. Interactive Dashboard
- Built using Streamlit
- Clean UI for data upload and visualization
- Real-time insights display

---

## System Flow
Data Upload (CSV / Excel)
↓
Automated EDA Processing
↓
┌───────────────┐
│ │
NL Query Engine ML Models
│ │
SQL Results Predictions
↓
Interactive Dashboard
↓
Report Generation


---

## Tech Stack

- **Python**
- **Pandas, NumPy**
- **Streamlit**
- **XGBoost**
- **SQLite + SQLAlchemy**
- **Plotly**
- **Generative AI API (for NL queries & reports)**

---

## Project Structure


ai-bi-platform/
├── app.py
├── requirements.txt
├── data/
├── eda/
├── models/
├── nlsql/
├── dashboard/
├── reports/
└── database/


---

## How to Run

### 1. Clone the repository
```bash
git clone https://github.com/Amrita839/ai-bi-platform-clean.git
cd ai-bi-platform-clean
2. Install dependencies
pip install -r requirements.txt
3. Setup environment variables

Create a .env file and add your API keys.

4. Run the application
streamlit run dashboard/streamlit_app.py
Sample Use Cases
Business performance analysis
Customer behavior insights
Revenue forecasting
Data-driven decision making
Notes
Works best with structured datasets
Large files may take longer to process
API keys required for AI-based features