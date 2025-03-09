import pandas as pd
from pymongo import MongoClient

# Load the cleaned dataset
file_path = "cleaned_styles.csv"  # Update with the correct path
data = pd.read_csv(file_path)

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["fashionMate"]  # Your database name
collection = db["user_preferences"]

# Insert data into the wardrobe collection
records = data.to_dict(orient="records")
collection.insert_many(records)

print("Dataset inserted successfully!")
