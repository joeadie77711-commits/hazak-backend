import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    jwt_required,
    get_jwt_identity
)

app = Flask(__name__)
# Aktifkan CORS sepenuhnya tanpa sekatan
CORS(app)

# JWT setup
app.config["JWT_SECRET_KEY"] = "hazakRahsiaToken123"
jwt = JWTManager(app)

# MongoDB Atlas URI dengan TLS bypass
uri = "mongodb+srv://joeadie77711:220481joe@cluster0.lqzyzwf.mongodb.net/?retryWrites=true&w=majority&tls=true&tlsAllowInvalidCertificates=true"
client = MongoClient(uri, server_api=ServerApi('1'))

# Uji sambungan MongoDB
try:
    client.admin.command('ping')
    print("✅ Berjaya sambung ke MongoDB Atlas!")
except Exception as e:
    print("❌ Ralat sambungan MongoDB:", e)

# Pilih database dan koleksi
db = client["hazak_db"]
users_collection = db["users"]

@app.route('/')
def home():
    return jsonify({"message": "Hazak API aktif!"})

@app.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json(force=True)
        print("📥 Data diterima dari frontend:", data)

        name = data.get("name")
        email = data.get("email")
        password = data.get("password")

        if not name or not email or not password:
            return jsonify({"message": "Semua medan wajib diisi"}), 400

        if users_collection.find_one({"email": email}):
            return jsonify({"message": "Email sudah didaftarkan"}), 400

        hashed_pw = generate_password_hash(password)
        result = users_collection.insert_one({
            "name": name,
            "email": email,
            "password": hashed_pw
        })
        print("✅ Disimpan dengan _id:", result.inserted_id)

        return jsonify({"message": "Pendaftaran berjaya!"}), 201

    except Exception as e:
        print("❌ Error dalam /register:", e)
        return jsonify({"message": "Server error"}), 500

@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json(force=True)
        email = data.get("email")
        password = data.get("password")

        user = users_collection.find_one({"email": email})
        if not user or not check_password_hash(user["password"], password):
            return jsonify({"message": "Email atau kata laluan salah"}), 401

        access_token = create_access_token(identity=email)
        return jsonify({"token": access_token}), 200

    except Exception as e:
        print("❌ Error dalam /login:", e)
        return jsonify({"message": "Server error"}), 500

@app.route('/users', methods=['GET'])
@jwt_required()
def get_users():
    try:
        current_user = get_jwt_identity()
        users = list(users_collection.find({}, {"_id": 0, "password": 0}))
        return jsonify({"current_user": current_user, "users": users})
    except Exception as e:
        print("❌ Error dalam /users:", e)
        return jsonify({"message": "Server error"}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)