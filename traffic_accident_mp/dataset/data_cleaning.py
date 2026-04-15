import pandas as pd

def clean_data():
    df = pd.read_csv("dataset/raw_data.csv")

    print("Columns:", df.columns)

    # Adjust column names based on your dataset
    df = df.rename(columns={
        "Start_Lat": "latitude",
        "Start_Lng": "longitude",
        "Severity": "severity"
    })

    # Keep required columns
    df = df[["latitude", "longitude", "severity"]]

    # Remove missing values
    df = df.dropna()

    # Reduce dataset size
    df = df.sample(1000, random_state=42)

    df.to_csv("dataset/cleaned_data.csv", index=False)

    print("✅ Cleaned data saved!")

if __name__ == "__main__":
    clean_data()