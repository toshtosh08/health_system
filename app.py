from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'  # Replace with a secure key later
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///health_system.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    contact_info = db.Column(db.String(100), nullable=False)
    enrollments = db.relationship('Enrollment', backref='client', lazy=True)

class Program(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)

class Enrollment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    program_id = db.Column(db.Integer, db.ForeignKey('program.id'), nullable=False)
    program = db.relationship('Program', backref='enrollments')

# API Authentication Middleware
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        try:
            token = token.split(" ")[1]  # Expecting 'Bearer <token>'
            jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
        except:
            return jsonify({'error': 'Invalid token'}), 401
        return f(*args, **kwargs)
    return decorated

# Routes
@app.route('/')
def index():
    programs = Program.query.all()
    return render_template('index.html', programs=programs)

@app.route('/create_program', methods=['POST'])
def create_program():
    name = request.form.get('name').strip()
    description = request.form.get('description').strip()
    if not name:
        return jsonify({'error': 'Program name is required'}), 400
    if Program.query.filter_by(name=name).first():
        return jsonify({'error': 'Program already exists'}), 400
    program = Program(name=name, description=description)
    db.session.add(program)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/register_client', methods=['POST'])
def register_client():
    name = request.form.get('name').strip()
    dob = request.form.get('date_of_birth')
    gender = request.form.get('gender').strip()
    contact = request.form.get('contact_info').strip()
    if not all([name, dob, gender, contact]):
        return jsonify({'error': 'All fields are required'}), 400
    try:
        dob = datetime.strptime(dob, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Invalid date format'}), 400
    client = Client(name=name, date_of_birth=dob, gender=gender, contact_info=contact)
    db.session.add(client)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/enroll_client', methods=['POST'])
def enroll_client():
    client_id = request.form.get('client_id')
    program_id = request.form.get('program_id')
    if not all([client_id, program_id]):
        return jsonify({'error': 'Client ID and Program ID are required'}), 400
    if Enrollment.query.filter_by(client_id=client_id, program_id=program_id).first():
        return jsonify({'error': 'Client already enrolled'}), 400
    enrollment = Enrollment(client_id=client_id, program_id=program_id)
    db.session.add(enrollment)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/search_client', methods=['GET'])
def search_client():
    query = request.args.get('query', '').strip()
    clients = Client.query.filter(Client.name.ilike(f'%{query}%')).all() if query else []
    return render_template('search_results.html', clients=clients)

@app.route('/client/<int:client_id>')
def client_profile(client_id):
    client = Client.query.get_or_404(client_id)
    return render_template('client_profile.html', client=client)

@app.route('/api/client/<int:client_id>', methods=['GET'])
@token_required
def api_client_profile(client_id):
    client = Client.query.get_or_404(client_id)
    enrollments = [{'program': e.program.name} for e in client.enrollments]
    return jsonify({
        'id': client.id,
        'name': client.name,
        'date_of_birth': client.date_of_birth.isoformat(),
        'gender': client.gender,
        'contact_info': client.contact_info,
        'enrollments': enrollments
    })

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        token = jwt.encode({'username': username}, app.config['SECRET_KEY'], algorithm='HS256')
        return jsonify({'token': token})
    return jsonify({'error': 'Invalid credentials'}), 401

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Creates database tables
    app.run(debug=True)