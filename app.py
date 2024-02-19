from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO
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
def join_room(room_code):
    if request.method == 'GET':
        room_file = os.path.join(ROOMS_DIR, f'{room_code}.html')
        if os.path.exists(room_file):
            user_name = request.args.get('name', 'Anonymous')
            messages = room_messages.get(room_code, [])
            return render_template('room.html', room_code=room_code, messages=messages, user_name=user_name)
        else:
            return 'Room not found!'
    else:
        pass

@app.route('/room/<room_code>/send_message', methods=['POST'])
def send_message(room_code):
    message_text = request.form['message']
    user_name = request.form['user_name']
    message = {'user': user_name, 'text': message_text}
    room_messages[room_code].append(message)
    socketio.emit('receive_message', message, room=room_code)
    return jsonify({'message': 'Message sent successfully!'})

def generate_room_code():
    return str(uuid.uuid4())[:10]

if __name__ == '__main__':
    socketio.run(app, debug=True)
