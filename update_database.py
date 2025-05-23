import pandas as pd
import sqlite3
import os

# Load CSV
project_root = os.path.abspath(os.path.dirname(__file__))
csv_path = os.path.join(project_root, 'data', 'web_logs_cleaned.csv')
print(f"Loading data from CSV at: {csv_path}")
df = pd.read_csv(csv_path)
df['timestamp'] = pd.to_datetime(df['timestamp'])

# One-hot encode categorical columns
categorical_columns = ['hour', 'referrer_type', 'device_type', 'team_member_id', 'product', 'day_of_week', 'month']
df_encoded = pd.get_dummies(df, columns=categorical_columns, drop_first=True)

# Add target columns
df_encoded['target_revenue'] = df_encoded['revenue'] * 1.1
df_encoded['target_inquiries'] = df_encoded['is_conversion'].rolling(window=24, min_periods=1).sum() * 1.05

# Save to SQLite
sqlite_db_path = os.path.join(project_root, 'data', 'analytics_data.db')
print(f"Saving data to SQLite database at: {sqlite_db_path}")
conn = sqlite3.connect(sqlite_db_path)
df_encoded.to_sql('web_logs', conn, if_exists='replace', index=False)
conn.close()
print(f"[✓] CSV data saved to SQLite database at '{sqlite_db_path}'")