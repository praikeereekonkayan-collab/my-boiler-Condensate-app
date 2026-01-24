
import pandas as pd

file_path = r'C:\Users\nb.boiler\OneDrive\Desktop\%CONDENSATE BOILER.xlsx'

try:
    df = pd.read_excel(file_path)
    print("Columns:")
    print(df.columns.tolist())
    print("\nFirst 5 rows:")
    print(df.head())
    print("\nData Types:")
    print(df.dtypes)
except Exception as e:
    print(f"Error reading file: {e}")
