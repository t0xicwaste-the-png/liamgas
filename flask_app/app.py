from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-please-change-in-prod')

# Database Config (Supports Render Postgres or External Neon via MY_DB_URL)
database_url = os.environ.get('MY_DB_URL') or os.environ.get('DATABASE_URL') or 'sqlite:///site.db'
if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)
app.config['SQLALCHEMY_DATABASE_URI'] = database_url

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    # Profile picture removed for simplicity (Render ephemeral FS)
    messages = db.relationship('Message', backref='author', lazy=True)
    rooms = db.relationship('ChatRoom', backref='creator', lazy=True)

class ChatRoom(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    messages = db.relationship('Message', backref='room', lazy=True)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('chat_room.id'), nullable=False)

# Auto-create tables on startup (Essential for Render)
# Must be AFTER models are defined!
with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists.')
            return redirect(url_for('register'))
            
        hashed_password = generate_password_hash(password, method='sha256')
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        
        login_user(new_user)
        return redirect(url_for('chat_rooms'))
        
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('chat_rooms'))
        else:
            flash('Login Unsuccessful. Please check username and password')
            
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/profile')
@login_required
def profile():
    # Profile pic removed
    return render_template('profile.html', user=current_user)

@app.route('/chat/')
@login_required
def chat_rooms():
    rooms = ChatRoom.query.order_by(ChatRoom.created_at.desc()).all()
    return render_template('chat_rooms.html', rooms=rooms)

@app.route('/chat/create/', methods=['GET', 'POST'])
@login_required
def create_room():
    if not current_user.is_admin:
        flash('Only admins can create rooms.')
        return redirect(url_for('chat_rooms'))
        
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        new_room = ChatRoom(name=name, description=description, created_by=current_user.id)
        db.session.add(new_room)
        db.session.commit()
        return redirect(url_for('chat_rooms'))
    return render_template('create_room.html')

@app.route('/chat/<int:room_id>/')
@login_required
def chat_room(room_id):
    room = ChatRoom.query.get_or_404(room_id)
    messages = Message.query.filter_by(room_id=room_id).order_by(Message.timestamp.desc()).limit(50).all()
    messages = messages[::-1] # Reverse to show oldest first
    return render_template('chat_room.html', room=room, messages=messages)

@app.route('/chat/<int:room_id>/send/', methods=['POST'])
@login_required
def send_message(room_id):
    content = request.form.get('content')
    if content:
        msg = Message(content=content, user_id=current_user.id, room_id=room_id)
        db.session.add(msg)
        db.session.commit()
        return jsonify({'success': True})
    return jsonify({'success': False, 'error': 'No content'})

@app.route('/chat/<int:room_id>/messages/')
@login_required
def get_messages(room_id):
    after_id = request.args.get('after', 0, type=int)
    new_messages = Message.query.filter(Message.room_id == room_id, Message.id > after_id).order_by(Message.timestamp).all()
    
    messages_data = [{
        'id': msg.id,
        'user': msg.author.username,
        'content': msg.content,
        'timestamp': msg.timestamp.isoformat(),
        # No profile picture URL
        'profile_picture': None
    } for msg in new_messages]
    
    return jsonify({'messages': messages_data})

if __name__ == '__main__':
    # (Optional) We can leave this here too for local dev convenience, 
    # but the one above handles production.
    with app.app_context():
        db.create_all()
    app.run(debug=True)
