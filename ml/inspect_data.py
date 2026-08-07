import pandas as pd
import os

data_dir = r"C:\Users\Kondreddy Mahendra\.gemini\antigravity-ide\scratch\intelligent_crop_system\data"
crop_file = os.path.join(data_dir, "Crop_recommendation.csv")
fert_file = os.path.join(data_dir, "Fertilizer_Recommendation.csv")

def inspect_dataset(filepath):
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return
    print(f"--- Inspecting: {os.path.basename(filepath)} ---")
    df = pd.read_csv(filepath)
    print(f"Shape: {df.shape}")
    print(f"Columns: {df.columns.tolist()}")
    print("\nData Types:")
    print(df.dtypes)
    print("\nMissing Values:")
    print(df.isnull().sum())
    print("\nDuplicate Count:", df.duplicated().sum())
    print("\nSample (First 3 rows):")
    print(df.head(3))
    print("\n")

inspect_dataset(crop_file)
inspect_dataset(fert_file)
