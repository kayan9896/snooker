from flask import Flask, request
from flask_socketio import SocketIO, emit
from collections import deque
import time
import uuid

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

class MatchMaker:
    def __init__(self):
        self.waiting_players = deque()

    def add_player(self, player_id):
        self.waiting_players.append({
            'id': player_id,
            'join_time': time.time()
        })

    def find_match(self, player_id):
        # Remove current player if they're already in queue
        self.waiting_players = deque(
            player for player in self.waiting_players 
            if player['id'] != player_id
        )
        
        # Add current player to queue
        self.add_player(player_id)

        # If we have at least 2 players, make a match
        if len(self.waiting_players) >= 2:
            player1 = self.waiting_players.popleft()
            player2 = self.waiting_players.popleft()
            return player1, player2
        return None

matchmaker = MatchMaker()

@socketio.on('connect')
def handle_connect():
    print(f"Client connected: {request.sid}")

@socketio.on('disconnect')
def handle_disconnect():
    print(f"Client disconnected: {request.sid}")

@socketio.on('find_game')
def handle_find_game():
    match = matchmaker.find_match(request.sid)
    
    if match:
        player1, player2 = match
        game_id = str(uuid.uuid4())
        
        # Send match found event to both players
        game_data = {
            'game_id': game_id,
            'player1_id': player1['id'],
            'player2_id': player2['id']
        }
        
        socketio.emit('match_found', game_data, room=player1['id'])
        socketio.emit('match_found', game_data, room=player2['id'])

if __name__ == '__main__':
    socketio.run(app, debug=True,host='0.0.0.0',port=3000)
