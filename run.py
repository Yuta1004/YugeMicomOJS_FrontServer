from server import app, socketio

socketio.run(app, port=12000)
