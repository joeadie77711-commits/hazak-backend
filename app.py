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

# ✅ Konfigurasi CORS yang lebih longgar
CORS(app, origins="*", allow_headers="*", methods=["GET", "POST"], supports_credentials=True)

# ✅ Log environment variable
uri = os.environ.get("MONGO_URI")
print("🔧 MONGO_URI:", uri, flush=True)

# ✅ Sambung ke MongoDB Atlas
print("🔌 Cuba sambung ke MongoDB Atlas...", flush=True)
client = MongoClient(uri, server_api=ServerApi('1'))

try:
    client.admin.command('ping')
    print("✅ Berjaya sambung ke MongoDB Atlas!", flush=True)
except Exception as e:
    print("❌ Ralat sambungan MongoDB:", e, flush=True)

# ✅ Setup JWT
app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_K")
app.secret_key = os.environ.get("SECRET_KEY")
jwt = JWTManager(app)

# ✅ Pilih database dan koleksi
db = client["hazak_db"]
users_collection = db["users"]

@app.route('/')
def home():
    return jsonify({"message": "Hazak API aktif!"})

@app.route('/register', methods=['POST'])
def register():
    print("🚀 Endpoint /register dipanggil", flush=True)
    try:
        data = request.get_json(force=True)
        print("📥 Data diterima dari frontend:", data, flush=True)

        name = data.get("name")
        email = data.get("email")
        password = data.get("password")

        if not name or not email or not password:
            print("⚠️ Medan kosong dikesan", flush=True)
            return jsonify({"message": "Semua medan wajib diisi"}), 400

        if users_collection.find_one({"email": email}):
            print("⚠️ Email sudah wujud:", email, flush=True)
            return jsonify({"message": "Email sudah didaftarkan"}), 400

        hashed_pw = generate_password_hash(password)
        result = users_collection.insert_one({
            "name": name,
            "email": email,
            "password": hashed_pw
        })
        print("✅ Disimpan dengan _id:", result.inserted_id, flush=True)

        return jsonify({"message": "Pendaftaran berjaya!"}), 201

    except Exception as e:
        print("❌ Error dalam /register:", e, flush=True)
        return jsonify({"message": "Server error"}), 500

@app.route('/login', methods=['POST'])
def login():
    print("🚀 Endpoint /login dipanggil", flush=True)
    try:
        data = request.get_json(force=True)
        email = data.get("email")
        password = data.get("password")

        user = users_collection.find_one({"email": email})
        if not user or not check_password_hash(user["password"], password):
            print("⚠️ Login gagal untuk:", email, flush=True)
            return jsonify({"message": "Email atau kata laluan salah"}), 401

        access_token = create_access_token(identity=email)
        print("✅ Token dijana untuk:", email, flush=True)
        return jsonify({"token": access_token}), 200

    except Exception as e:
        print("❌ Error dalam /login:", e, flush=True)
        return jsonify({"message": "Server error"}), 500

@app.route('/users', methods=['GET'])
@jwt_required()
def get_users():
    print("🚀 Endpoint /users dipanggil", flush=True)
    try:
        current_user = get_jwt_identity()
        users = list(users_collection.find({}, {"_id": 0, "password": 0}))
        print("📦 Jumlah pengguna:", len(users), flush=True)
        return jsonify({"current_user": current_user, "users": users})
    except Exception as e:
        print("❌ Error dalam /users:", e, flush=True)
        return jsonify({"message": "Server error"}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    print(f"🚀 Flask berjalan di port {port}", flush=True)
    app.run(host='0.0.0.0', port=port)