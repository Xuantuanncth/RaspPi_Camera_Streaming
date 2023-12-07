import socketio

# Initialize a new Socket.IO client
sio = socketio.Client()

# Define event handlers
@sio.on('connect')
def on_connect():
    print('Connected to server')

@sio.on('disconnect')
def on_disconnect():
    print('Disconnected from server')

@sio.on('chat')
def on_chat_message(data):
    print('Received message:', data)

@sio.on('setting')
def on_setting_message(data):
    print('Received setting:', data)

# Connect to the Socket.IO server
sio.connect('http://localhost:3000')

# Send a message to the server
sio.emit('chat', 'Hello from Python!')

# Wait for the connection to be established and messages to be received
sio.wait()
