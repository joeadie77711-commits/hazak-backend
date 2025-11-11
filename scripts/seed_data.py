from pymongo import MongoClient
from dotenv import load_dotenv, find_dotenv
import os

# Cari dan baca fail .env
dotenv_path = find_dotenv()
print("ENV path found:", dotenv_path)  # Debug

# Debug: baca isi fail .env
with open(dotenv_path, "r") as f:
    print("Isi fail .env:")
    print(f.read())

# Muatkan environment
load_dotenv(dotenv_path)

# Debug: semak nilai terus
print("Semakan terus:", os.environ.get("MONGO_URI"))

# Ambil URI dari environment
mongo_uri = os.getenv("MONGO_URI")
print("Connecting to:", mongo_uri)  # Debug

# Sambung ke MongoDB Atlas
client = MongoClient(mongo_uri)
db = client["hazak_db"]
collection = db["users"]

# Contoh data
sample_data = [
    {"name": "Ali", "email": "ali@example.com"},
    {"name": "Siti", "email": "siti@example.com"}
]

# Masukkan data
collection.delete_many({})


result = collection.insert_many(sample_data)
print("Data seeded successfully!")