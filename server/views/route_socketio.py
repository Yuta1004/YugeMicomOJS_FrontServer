from flask_socketio import emit
from server import socketio


@socketio.on("message_from_client")
def handle_connect_event(message):
    print(message)
    emit("message_from_server", "Hello Client!", broadcast=True)

