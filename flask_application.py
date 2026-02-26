import os
from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, Namespace, emit

from random import choices

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)
socketio = SocketIO(app, async_mode="eventlet")

class Wheel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    entries = db.Column(db.PickleType)
    weights = db.Column(db.PickleType)
    colors = db.Column(db.PickleType)  # Add this line

class MyNamespace(Namespace):
    def on_connect(self):
        pass

    def on_disconnect(self):
        pass

    def on_spin(self, data):
        self.emit('spin', {'angle': data['angle']}, broadcast=True)

        

        
        
socketio.on_namespace(MyNamespace('/'))

# After initializing socketio with app
@socketio.on('spinResult', namespace='/')
def handle_spin_result(data):
    print("Received spin result:", data)
    entry = data['entry']
    subEntry = data['subEntry']
    print("Broadcasting result:", {'entry': entry, 'subEntry': subEntry})
    emit('result', {'entry': entry, 'subEntry': subEntry}, broadcast=True)

@app.route('/wheel', methods=['GET', 'POST'])
def wheel():
    if request.method == 'POST':
        data = request.get_json()
        entries = data.get('entries')
        weights = data.get('weights')

        if len(entries) != len(weights):
            return jsonify({'error': 'Entries and weights must be the same length'}), 400

        try:
            weights = [float(weight) for weight in weights]
        except ValueError:
            return jsonify({'error': 'Weights must be numeric'}), 400

        
        
        wheel = Wheel.query.get(1)
        if wheel is None:
          wheel = Wheel(id=1, entries=['entry1', 'entry2', 'entry3', 'entry4'], weights=[1, 2, 3, 4], colors=['red', 'green', 'blue', 'yellow'])
          db.session.add(wheel)

        else:
            wheel.entries = entries
            wheel.weights = weights
        db.session.commit()

        print(f"Updated entries: {wheel.entries}")  # Add this line
        print(f"Updated weights: {wheel.weights}")  # Add this line

        # Return the updated entries and weights in the response
        return jsonify({'status': 'success', 'entries': wheel.entries, 'weights': wheel.weights}), 200
    else:
        wheel = Wheel.query.get(1)
        if wheel is None:
            return jsonify({'error': 'No entries added yet'}), 400
        return jsonify({'entries': wheel.entries, 'weights': wheel.weights}), 200

@app.route('/spin', methods=['POST'])
def spin():
    data = request.get_json()
    angle = data.get('angle')
    print(f"Received angle: {angle}")  # Add this line
    broadcast_status = socketio.emit('spin', {'angle': angle}, namespace='/')
    print(f"Broadcast status: {broadcast_status}")  # Add this line
    return jsonify({'status': 'success'}), 200


@app.route('/', methods=['GET'])
def home():
    return render_template('wheel.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # create tables if missing
        wheel = Wheel.query.get(1)
        if wheel is None:
            wheel = Wheel(
                id=1,
                entries=['entry1', 'entry2', 'entry3', 'entry4'],
                weights=[1, 2, 3, 4],
                colors=['red', 'green', 'blue', 'yellow']
            )
            db.session.add(wheel)
            db.session.commit()

    PORT = int(os.environ.get('PORT', 5000))  # <- Render gives this
    socketio.run(app, host='0.0.0.0', port=PORT)


