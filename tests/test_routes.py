import unittest
from app import app, db, Client, Program, Enrollment, User
import os
from datetime import datetime

class RoutesTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
        self.client = app.test_client()
        with app.app_context():
            # Drop and recreate tables to ensure a clean state
            db.drop_all()
            db.create_all()
            # Check if testdoctor user exists before creating
            if not User.query.filter_by(username='testdoctor').first():
                user = User(username='testdoctor')
                user.set_password('password')
                db.session.add(user)
                db.session.commit()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()
        # Optionally delete test.db to ensure no persistence
        if os.path.exists('test.db'):
            os.remove('test.db')

    def test_create_program(self):
        response = self.client.post('/create_program', data={'name': 'TB', 'description': 'Tuberculosis Program'})
        self.assertEqual(response.status_code, 302)
        with app.app_context():
            program = Program.query.filter_by(name='TB').first()
            self.assertIsNotNone(program)
            self.assertEqual(program.description, 'Tuberculosis Program')

    def test_register_client(self):
        response = self.client.post('/register_client', data={
            'name': 'John Doe',
            'date_of_birth': '1990-01-01',
            'gender': 'Male',
            'contact_info': 'john@example.com'
        })
        self.assertEqual(response.status_code, 302)
        with app.app_context():
            client = Client.query.filter_by(name='John Doe').first()
            self.assertIsNotNone(client)

    def test_enroll_client(self):
        with app.app_context():
            program = Program(name='TB')
            client = Client(
                name='John Doe',
                date_of_birth=datetime.strptime('1990-01-01', '%Y-%m-%d').date(),
                gender='Male',
                contact_info='john@example.com'
            )
            db.session.add_all([program, client])
            db.session.commit()
            program_id = program.id
            client_id = client.id
        response = self.client.post('/enroll_client', data={'client_id': client_id, 'program_id': program_id})
        self.assertEqual(response.status_code, 302)
        with app.app_context():
            enrollment = Enrollment.query.filter_by(client_id=client_id, program_id=program_id).first()
            self.assertIsNotNone(enrollment)

    def test_search_client(self):
        with app.app_context():
            client = Client(
                name='John Doe',
                date_of_birth=datetime.strptime('1990-01-01', '%Y-%m-%d').date(),
                gender='Male',
                contact_info='john@example.com'
            )
            db.session.add(client)
            db.session.commit()
        response = self.client.get('/search_client?query=John')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'John Doe', response.data)

    def test_client_profile(self):
        with app.app_context():
            client = Client(
                name='John Doe',
                date_of_birth=datetime.strptime('1990-01-01', '%Y-%m-%d').date(),
                gender='Male',
                contact_info='john@example.com'
            )
            db.session.add(client)
            db.session.commit()
            client_id = client.id
        response = self.client.get(f'/client/{client_id}')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'John Doe', response.data)

    def test_api_login(self):
        response = self.client.post('/api/login', json={'username': 'testdoctor', 'password': 'password'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('token', response.json)

    def test_api_client_profile(self):
        with app.app_context():
            client = Client(
                name='John Doe',
                date_of_birth=datetime.strptime('1990-01-01', '%Y-%m-%d').date(),
                gender='Male',
                contact_info='john@example.com'
            )
            db.session.add(client)
            db.session.commit()
            client_id = client.id
        # Get token
        login_response = self.client.post('/api/login', json={'username': 'testdoctor', 'password': 'password'})
        token = login_response.json['token']
        # Access API
        response = self.client.get(f'/api/client/{client_id}', headers={'Authorization': f'Bearer {token}'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['name'], 'John Doe')

if __name__ == '__main__':
    unittest.main()