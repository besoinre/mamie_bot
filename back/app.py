from flask import Flask, jsonify, request
from flask_cors import CORS
from pymongo import MongoClient
from mamie_bot import mamieBot
from dataclasses import asdict
import threading
import time
import traceback
import re
from bson import ObjectId
import os
from waitress import serve
import firebase_admin
from firebase_admin import credentials, db

firebaseUrl = os.getenv("FIREBASE_URL")
cred = credentials.Certificate({
    "type": "service_account",
    "project_id": os.getenv("FIREBASE_PROJECT_ID"),
    "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
    "private_key": os.getenv("FIREBASE_PRIVATE_KEY"),
    "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
    "client_id": os.getenv("FIREBASE_CLIENT_ID"),
    "auth_uri": os.getenv("FIREBASE_AUTH_URI"),
    "token_uri": os.getenv("FIREBASE_TOKEN_URI"),
    "auth_provider_x509_cert_url": os.getenv("FIREBASE_AUTH_PROVIDER_X509_CERT_URL"),
    "client_x509_cert_url": os.getenv("FIREBASE_CLIENT_X509_CERT_URL"),
    "universe_domain": "gooleapis.com"    
})
firebase_admin.initialize_app(cred, {
    'databaseURL': firebaseUrl
})

environment = os.getenv("ENVIRONMENT")
database_url = os.getenv("DATABASE_URL")

client = MongoClient(database_url, ssl=environment != 'dev')
db_mongo = client['mamie_bot']
playersCollection = db_mongo['players']
eventsCollection = db_mongo['events']

app = Flask(__name__)
CORS(app)

port = int(os.getenv("PORT", 5000))

@app.route('/live-events', methods=['GET'])
def get_events():
    player_name = request.args.get('name')
    if(player_name):
        documents = eventsCollection.find({"player": {"$regex": f"^{player_name}$", "$options": "i"}})
    else:
        documents = eventsCollection.find()
    events = []
    for doc in documents:
        doc['_id'] = str(doc['_id'])  
        events.append(doc)

    if events:
        return jsonify(events), 200
    else:
        return jsonify({'message': 'Events not found'}), 404

@app.route('/players', methods=['POST'])
def add_player():
    data = request.get_json()
    if not data or 'playerName' not in data or 'puuid' not in data:
        return jsonify({"error": "Missing player_name or puuid"}), 400

    player_name = data['playerName']
    puuid = data['puuid']
    
    player_data = {
        "playerName": player_name,
        "puuid": puuid
    }
    existing_player = playersCollection.find_one({
        "$or": [
            {"playerName": {"$regex": f"^{re.escape(player_name)}$", "$options": "i"}},  
            {"puuid": {"$regex": f"^{re.escape(puuid)}$", "$options": "i"}}  
        ]
    })    
    if existing_player:
        return jsonify({"error": "Player already exists"}), 409

    inserted_id = playersCollection.insert_one(player_data).inserted_id
    return jsonify({"id": str(inserted_id), "message": "Player added successfully"}), 201

@app.route('/players', methods=['GET'])
def get_players():
    players = playersCollection.find()  
    player_list = [{"_id": str(player['_id']), "playerName": player["playerName"], "puuid": player["puuid"]} for player in players]
    return jsonify(player_list)

@app.route('/players/<player_id>', methods=['DELETE'])
def delete_player(player_id):
    try:
        player_object_id = ObjectId(player_id) 
    except Exception as e:
        return jsonify({"error": "Invalid player ID"}), 400  

    result = playersCollection.delete_one({"_id": player_object_id})
    
    if result.deleted_count == 1:
        return jsonify({"message": "Player deleted successfully"}), 200
    else:
        return jsonify({"error": "Player not found"}), 404

def update_firebase_games_history(new_games_data, max_history=500):
    # Add new entry as before
    history_ref = db.reference('tft-games-history')
    entry_key = str(int(time.time() * 1000))
    
    history_ref.child(entry_key).set({
        'games': new_games_data,
        'timestamp': entry_key
    })
    
    # Update latest reference
    latest_ref = db.reference('tft-games-latest')
    latest_ref.set({
        'games': new_games_data,
        'timestamp': entry_key
    })
    
    # Prune old entries if needed
    all_entries = history_ref.get() or {}
    if all_entries and len(all_entries) > max_history:
        # Sort entries by timestamp (oldest first)
        sorted_keys = sorted(all_entries.keys())
        # Calculate how many to remove
        to_remove = len(sorted_keys) - max_history
        # Remove oldest entries
        for i in range(to_remove):
            history_ref.child(sorted_keys[i]).delete()

# Define your background task
def lp_tracker():        
    print("Starting mamie bot")   
    mamie_bot = mamieBot()
    while True:
        try:
            mamie_bot.update()
        except:
            print("An error occurred:")
            traceback.print_exc()
        message_logs = mamie_bot.message_logs
        for message_log in message_logs:
                try:     
                    print(str(message_log))
                    eventsCollection.insert_one(asdict(message_log))
                    update_firebase_games_history(asdict(message_log))
                except Exception as e:
                    print("An error occurred:")
                    traceback.print_exc()
        time.sleep(10)


# Start the background task in a separate thread
thread = threading.Thread(target=lp_tracker)
thread.daemon = True  # Ensures the thread will close when the main program ends
thread.start()

# if __name__ == '__main__':
#     app.run(debug=True)

# if __name__ == '__main__':
#     app.run(host="0.0.0.0", port=port)

if __name__ == '__main__':
    serve(app, host='0.0.0.0', port=port)