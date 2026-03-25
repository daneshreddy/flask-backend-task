from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import bcrypt

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'super-secret-key'

db = SQLAlchemy(app)
jwt = JWTManager(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.LargeBinary)
    role = db.Column(db.String(10))

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200))
    user = db.Column(db.String(50))

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    user_id = db.Column(db.Integer)

@app.route('/')
def home():
    return "Backend Running"

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"message": "Missing data"}), 400

    existing = User.query.filter_by(username=username).first()
    if existing:
        return jsonify({"message": "User already exists"}), 400

    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    new_user = User(username=username, password=hashed, role='user')
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"})

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"message": "Missing data"}), 400

    user = User.query.filter_by(username=username).first()

    if not user:
        return jsonify({"message": "User not found"}), 404

    if bcrypt.checkpw(password.encode('utf-8'), user.password):
        token = create_access_token(identity=username)
        return jsonify({"token": token})

    return jsonify({"message": "Invalid credentials"}), 401

@app.route('/dashboard', methods=['GET'])
@jwt_required()
def dashboard():
    user = get_jwt_identity()
    return jsonify({"message": f"Welcome {user}"})

@app.route('/notes', methods=['POST'])
@jwt_required()
def create_note():
    data = request.get_json()
    user = get_jwt_identity()

    note = Note(content=data['content'], user=user)
    db.session.add(note)
    db.session.commit()

    return jsonify({"message": "Note created"})

@app.route('/notes', methods=['GET'])
@jwt_required()
def get_notes():
    user = get_jwt_identity()
    notes = Note.query.filter_by(user=user).all()

    return jsonify([{"id": n.id, "content": n.content} for n in notes])

@app.route('/notes/<int:id>', methods=['PUT'])
@jwt_required()
def update_note(id):
    data = request.get_json()
    note = Note.query.get(id)

    if not note:
        return jsonify({"message": "Note not found"})

    note.content = data['content']
    db.session.commit()

    return jsonify({"message": "Updated"})

@app.route('/notes/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_note(id):
    note = Note.query.get(id)

    if not note:
        return jsonify({"message": "Note not found"})

    db.session.delete(note)
    db.session.commit()

    return jsonify({"message": "Deleted"})

@app.route('/task', methods=['POST'])
@jwt_required()
def create_task():
    data = request.get_json()
    username = get_jwt_identity()
    user = User.query.filter_by(username=username).first()

    new_task = Task(title=data['title'], user_id=user.id)
    db.session.add(new_task)
    db.session.commit()

    return jsonify({"msg": "Task created"})

@app.route('/task', methods=['GET'])
@jwt_required()
def get_tasks():
    username = get_jwt_identity()
    user = User.query.filter_by(username=username).first()

    tasks = Task.query.filter_by(user_id=user.id).all()

    return jsonify([{"id": t.id, "title": t.title} for t in tasks])

@app.route('/task/<int:id>', methods=['PUT'])
@jwt_required()
def update_task(id):
    username = get_jwt_identity()
    user = User.query.filter_by(username=username).first()
    data = request.get_json()

    task = Task.query.get(id)

    if not task or task.user_id != user.id:
        return jsonify({"msg": "Task not found"}), 404

    task.title = data.get('title')
    db.session.commit()

    return jsonify({"msg": "Task updated"})

@app.route('/task/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_task(id):
    username = get_jwt_identity()
    user = User.query.filter_by(username=username).first()

    task = Task.query.get(id)

    if not task or task.user_id != user.id:
        return jsonify({"msg": "Task not found"}), 404

    db.session.delete(task)
    db.session.commit()

    return jsonify({"msg": "Task deleted"})

@app.route('/admin', methods=['GET'])
@jwt_required()
def admin_panel():
    username = get_jwt_identity()
    user = User.query.filter_by(username=username).first()

    if user.role != 'admin':
        return jsonify({"msg": "Access denied"}), 403

    return jsonify({"msg": "Welcome Admin"})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)