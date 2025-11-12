from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity

app = Flask(__name__)
CORS(app)

# Setup JWT
app.config["JWT_SECRET_KEY"] = "hazakRahsiaToken123"  # Tukar ke secret sebenar
jwt = JWTManager(app)

# Sambungan ke MongoDB Atlas dengan SSL bypass
uri = "mongodb+srv://joeadie77711:220481joe@cluster0.lqzyzwf.mongodb.net/?retryWrites=true&w=majority&tlsAllowInvalidCertificates=true"
client = MongoClient(uri, server_api=ServerApi('1'))

# Uji sambungan MongoDB
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print("MongoDB connection error:", e)

# Pilih database dan koleksi
db = client["hazak_db"]
users_collection = db["users"]

@app.route('/')
def home():
    return jsonify({"message": "Hazak API aktif!"})

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")

    if users_collection.find_one({"email": email}):
        return jsonify({"error": "Email sudah didaftarkan"}), 400

    hashed_pw = generate_password_hash(password)
    users_collection.insert_one({
        "name": name,
        "email": email,
        "password": hashed_pw
    })

    return jsonify({"message": "Pendaftaran berjaya!"}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    user = users_collection.find_one({"email": email})
    if not user or not check_password_hash(user["password"], password):
        return jsonify({"error": "Email atau password salah"}), 401

    access_token = create_access_token(identity=email)
    return jsonify({"token": access_token}), 200

@app.route('/users', methods=['GET'])
@jwt_required()
def get_users():
    current_user = get_jwt_identity()
    users = list(users_collection.find({}, {"_id": 0, "password": 0}))
    return jsonify({"current_user": current_user, "users": users})

if __name__ == '__main__':
   port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

