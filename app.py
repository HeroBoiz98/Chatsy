from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_socketio import SocketIO, join_room, leave_room, send
import os
import uuid

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
socketio = SocketIO(app)

# Directory to store HTML files for rooms
ROOMS_DIR = 'rooms'

# Create the rooms directory if it doesn't exist
if not os.path.exists(ROOMS_DIR):
    os.makedirs(ROOMS_DIR)

# Dictionary to store messages for each room
room_messages = {}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/create_room')
def create_room():
    room_code = generate_room_code()
    room_file = os.path.join(ROOMS_DIR, f'{room_code}.html')
    with open(room_file, 'w') as f:
        f.write('')
    room_messages[room_code] = []
    return f'Room created! Unique code: {room_code}'

@app.route('/join_room/<room_code>', methods=['GET', 'POST'])
def join_room_route(room_code):
    if request.method == 'GET':
        room_file = os.path.join(ROOMS_DIR, f'{room_code}.html')
        if os.path.exists(room_file):
            session['name'] = request.args.get('name', 'Anonymous')
            session['room'] = room_code
            messages = room_messages.get(room_code, [])
            return render_template('room.html', room_code=room_code, messages=messages, user_name=session['name'])
        else:
            return 'Room not found!'
    else:
        pass

@socketio.on('join')
def on_join(data):
    room = data['room']
    join_room(room)
    send({'msg': session.get('name') + ' has entered the room.'}, room=room)

@socketio.on('send_message')
def send_message(data):
    room_code = data['room_code']
    message_text = data['message']
    user_name = session.get('name', 'Anonymous')
    message = {'user': user_name, 'text': message_text}
    room_messages[room_code].append(message)
    send(message, room=room_code)

def generate_room_code():
    return str(uuid.uuid4())[:10]

if __name__ == '__main__':
    socketio.run(app, debug=True)
