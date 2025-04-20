import pandas as pd
import gc
import json
from flask import Flask, request, jsonify
from flask_socketio import SocketIO
from flask_cors import CORS
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
from vocab_predict import VocabPredictor
from config import HOST, PORT, VOCAB_FORMAT_PATH, VOCAB_MAP_FILE_PATH, FS_YT_FILE_PATH, DB_CONFIG

print("server.py: Libraries imported.")

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
socketio = SocketIO(app, cors_allowed_origins="*")
connected_clients = {}

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

format = pd.read_parquet(VOCAB_FORMAT_PATH)
vocab_predictor = VocabPredictor()

# Authentication APIs
@app.route('/api/signup', methods=['POST'])
def signup():
    try:
        data = request.get_json()
        print("data",data)
        username = data.get('username')
        password = data.get('password')
        email = data.get('email')

        if not username or not password or not email:
            return jsonify({"error": "Missing required fields"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if username or email already exists
        cursor.execute("SELECT id FROM users WHERE username = %s OR email = %s", (username, email))
        if cursor.fetchone():
            return jsonify({"error": "Username or email already exists"}), 400

        # Insert new user
        hashed_password = generate_password_hash(password)
        cursor.execute(
            "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
            (username, email, hashed_password)
        )
        conn.commit()

        # Get the last inserted user ID
        cursor.execute("SELECT LAST_INSERT_ID()")
        user_id = cursor.fetchone()[0]  # Fetch the ID of the newly inserted user

        return jsonify({
            "message": "User created successfully",
            "user_id":user_id
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        print("login data",data)
        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT id, password FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()

        if not user:
            return jsonify({"error": "User not found"}), 404

        if not check_password_hash(user[1], password):
            return jsonify({"error": "Incorrect password"}), 401

        return jsonify({"message": "Login successful", "user_id": user[0]}), 200

    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

    finally:
        cursor.close()
        conn.close()


# Score APIs
# @app.route('/api/score', methods=['POST'])
# def save_score():
#     try:
#         data = request.get_json()
#         user_id = data.get('user_id')
#         score = data.get('score')
        
#         if not all([user_id, score]):
#             return jsonify({"error": "Missing required fields"}), 400

#         conn = get_db_connection()
#         cursor = conn.cursor()
        
#         cursor.execute(
#             "INSERT INTO scores (user_id, score) VALUES (%s, %s)",
#             (user_id, score)
#         )
#         conn.commit()
        
#         cursor.close()
#         conn.close()
#         return jsonify({"message": "Score saved successfully"}), 201

#     except Exception as e:
#         return jsonify({"error": str(e)}), 500


@app.route('/api/score', methods=['POST'])
def save_score():
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        score = data.get('score')
        quiz_data = data.get('quiz_data')
        
        if not user_id or not quiz_data:
            return jsonify({"error": "Missing required fields (user_id and quiz_data are required)"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
            INSERT INTO scores (user_id, score, quiz_data)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE
            score = %s,
            quiz_data = %s,
            created_at = CURRENT_TIMESTAMP
        """
        score = score if score is not None else sum(1 for item in quiz_data if item.get('isCorrect', False))
        cursor.execute(
            query,
            (user_id, score, json.dumps(quiz_data), score, json.dumps(quiz_data))
        )

        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({"message": "Score and quiz data saved successfully"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/score/<int:user_id>', methods=['GET'])
def get_scores(user_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT user_id, score, created_at, quiz_data FROM scores WHERE user_id = %s ORDER BY created_at DESC",
            (user_id,)
        )
        # Fetch all rows and map them to a list of dictionaries with all fields
        scores = [
            {
                "user_id": row[0],
                "score": row[1],
                "created_at": str(row[2]),  # Convert timestamp to string
                "quiz_data": row[3]  # quiz_data is already JSON in the database
            }
            for row in cursor.fetchall()
        ]
        
        cursor.close()
        conn.close()
        return jsonify(scores), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Existing Routes
@app.route('/')
def index():
    return "Flask Socket.IO Server Running"

@app.route('/api/vocab-contents', methods=['GET'])
def get_vocab_data():
    try:
        with open(VOCAB_MAP_FILE_PATH, 'r') as f:
            data = json.load(f)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/fs-contents', methods=['GET'])
def get_fs_data():
    try:
        with open(FS_YT_FILE_PATH, 'r') as f:
            data = json.load(f)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@socketio.on("connect")
def handle_connect():
    client_id = request.sid
    connected_clients[client_id] = {"all_landmarks": [], "frame": 0}
    print(f"Client connected: {request.sid}")

@socketio.on("disconnect")
def handle_disconnect():
    client_id = request.sid
    connected_clients.pop(client_id, None)
    print(f"Client disconnected: {request.sid}")

@socketio.on("vocab-landmarkers")
def handle_vocab_landmarkers(results):
    try:
        if not results:
            return
        client_id = request.sid
        client_data = connected_clients.get(client_id)
        if not client_data:
            return
        client_data["frame"] += 1
        landmarks = create_vocab_framedata_df(results, client_data["frame"], format)
        client_data["all_landmarks"].append(landmarks)
        print("Received landmarks.")
    except Exception as e:
        print(f"Error at handle_vocab_landmarkers(): {str(e)}")

@socketio.on("vocab-predict")
def handle_vocab_predict():
    try:
        client_id = request.sid
        client_data = connected_clients.get(client_id)
        if not client_data or not client_data["all_landmarks"]:
            return []
        
        all_landmarks_df = pd.concat(client_data["all_landmarks"]).reset_index(drop=True)
        print("Predicting sign...")
        results = vocab_predictor.predict_sign(all_landmarks_df)
        
        if results:
            for result in results:
                print(f"Prediction result: {result['sign']}, {result['confidence'] * 100:.2f}%")
        
        client_data["all_landmarks"] = []
        gc.collect()
        return results
    except Exception as e:
        print(f"Error at handle_vocab_predict(): {str(e)}")
        return None

def create_vocab_framedata_df(results, frame, format):
    try:
        face = pd.DataFrame()
        pose = pd.DataFrame()
        left_hand = pd.DataFrame()
        right_hand = pd.DataFrame()

        if "faceLandmarks" in results and results["faceLandmarks"]:
            for i, point in enumerate(results["faceLandmarks"]):
                face.loc[i, ["x", "y", "z"]] = [point["x"], point["y"], point["z"]]
        if "poseLandmarks" in results and results["poseLandmarks"]:
            for i, point in enumerate(results['poseLandmarks']):
                pose.loc[i, ["x", "y", "z"]] = [point["x"], point["y"], point["z"]]
        if "leftHandLandmarks" in results and results["leftHandLandmarks"]:
            for i, point in enumerate(results['leftHandLandmarks']):
                left_hand.loc[i, ["x", "y", "z"]] = [point["x"], point["y"], point["z"]]
        if "rightHandLandmarks" in results and results["rightHandLandmarks"]:
            for i, point in enumerate(results["rightHandLandmarks"]):
                right_hand.loc[i, ["x", "y", "z"]] = [point["x"], point["y"], point["z"]]

        face = face.reset_index().rename(columns={"index": "landmark_index"}).assign(type="face")
        pose = pose.reset_index().rename(columns={"index": "landmark_index"}).assign(type="pose")
        left_hand = left_hand.reset_index().rename(columns={"index": "landmark_index"}).assign(type="left_hand")
        right_hand = right_hand.reset_index().rename(columns={"index": "landmark_index"}).assign(type="right_hand")

        landmarks = pd.concat([face, left_hand, pose, right_hand]).reset_index(drop=True)
        landmarks = format.merge(landmarks, on=["type", "landmark_index"], how="left")
        landmarks = landmarks.assign(frame=frame)
        return landmarks
    except Exception as e:
        print(f"Error at create_vocab_framedata_df(): {str(e)}")
        return pd.DataFrame()

if __name__ == "__main__":
    print(f"Server running on http://{HOST}:{PORT}")
    socketio.run(app, host=HOST, port=PORT, debug=False)