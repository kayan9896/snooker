import socketio
from threading import Event

class OnlineGameConnection:
    def __init__(self):
        self.sio = socketio.Client()
        self.match_found = Event()
        self.game_data = None
        self.setup_events()

    def setup_events(self):
        @self.sio.on('connect')
        def on_connect():
            print("Connected to server")

        @self.sio.on('match_found')
        def on_match_found(data):
            self.game_data = data
            self.match_found.set()

        @self.sio.on('connect_error')
        def on_connect_error():
            print("Connection failed!")

    def connect(self):
        try:
            self.sio.connect('https://z3qgq6jj.cdpad.io/')
        except Exception as e:
            print(f"Connection error: {e}")
            raise

    def disconnect(self):
        try:
            self.sio.disconnect()
        except:
            pass
        self.match_found.clear()

    def find_match(self):
        self.match_found.clear()
        self.sio.emit('find_game')

    def is_match_found(self):
        return self.match_found.is_set()

    def get_game_data(self):
        return self.game_data
