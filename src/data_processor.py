import pandas as pd
import os
import joblib
from sklearn.linear_model import Ridge

def get_data():
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    csv_path = os.path.join(project_root, 'data', 'web_logs_cleaned.csv')
    print(f"Attempting to load data from CSV at: {csv_path}")
    
    if not os.path.exists(csv_path):
        print(f"[!] Error: CSV file not found at {csv_path}")
        return {'raw': pd.DataFrame(), 'encoded': pd.DataFrame(), 'model': None}
    
    try:
        df = pd.read_csv(csv_path)
        print("Columns in web_logs_cleaned.csv:", df.columns.tolist())
        
        # Validate required columns
        required_columns = ['timestamp', 'country', 'action_type', 'product', 'team_member_id', 'revenue', 
                           'referrer', 'user_agent', 'hour', 'is_conversion', 'day_of_week', 'month', 
                           'referrer_type', 'device_type', 'country_gdp']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            print(f"[!] Warning: Missing columns in CSV: {missing_columns}")
        
        # Ensure timestamp is datetime
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # One-hot encode categorical columns to match model expectations
        categorical_columns = ['hour', 'referrer_type', 'device_type', 'team_member_id', 'product', 'day_of_week', 'month']
        df_encoded = pd.get_dummies(df, columns=categorical_columns, drop_first=True)
        print("Columns after one-hot encoding:", df_encoded.columns.tolist())
        
        # Add target data
        df['target_revenue'] = df['revenue'] * 1.1
        df['target_inquiries'] = df['is_conversion'].rolling(window=24, min_periods=1).sum() * 1.05
        
        # Test model loading
        model = joblib.load(os.path.join(project_root, 'models', 'ridge_revenue_model.pkl'))
        columns = joblib.load(os.path.join(project_root, 'models', 'ridge_revenue_model_columns.pkl'))
        print("[✓] Model loaded successfully with scikit-learn 1.6.1 and joblib 1.5.0")
        
        # Validate model columns
        missing_model_cols = [col for col in columns if col not in df_encoded.columns]
        if missing_model_cols:
            print(f"[!] Warning: Columns required by model but missing in DataFrame: {missing_model_cols}")
        else:
            print("[✓] All model columns present in DataFrame")
        
        return {'raw': df, 'encoded': df_encoded, 'model': model}
    
    except Exception as e:
        print(f"[!] Error loading data or model: {str(e)}")
        return {'raw': pd.DataFrame(), 'encoded': pd.DataFrame(), 'model': None}