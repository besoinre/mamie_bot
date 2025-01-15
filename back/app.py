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

database_url = os.getenv("DATABASE_URL")
client = MongoClient(database_url, ssl=True)
db = client['mamie_bot']
playersCollection = db['players']
eventsCollection = db['events']

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

@app.route('/keep-alive', methods=['GET'])
def keep_alive():
    return jsonify({"message": "Backend alive !"}), 200

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