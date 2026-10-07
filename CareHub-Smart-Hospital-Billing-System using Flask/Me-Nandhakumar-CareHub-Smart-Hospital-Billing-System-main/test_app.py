import unittest
from app import app
from database import init_db, execute_query

class CareHubAppTests(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()
        init_db()

    def test_01_login_logout(self):
        # GET Login Page
        res = self.client.get('/login')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Staff Portal Login', res.data)

        # POST Invalid Login
        res = self.client.post('/login', data={'username': 'wrong', 'password': 'bad'}, follow_redirects=True)
        self.assertIn(b'Invalid username or password', res.data)

        # POST Valid Login
        res = self.client.post('/login', data={'username': 'admin', 'password': '1234'}, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Hospital Operations Dashboard', res.data)

        # GET Logout
        res = self.client.get('/logout', follow_redirects=True)
        self.assertIn(b'You have been logged out', res.data)

    def test_02_add_patient_and_bill(self):
        # Log in first
        self.client.post('/login', data={'username': 'admin', 'password': '1234'})

        # POST Add Patient with Fever + Cold
        # Fever: Paracetamol 20 + Ibuprofen 30 = 50
        # Cold: Cetirizine 15 + Cough Syrup 50 = 65
        # Total expected = 115
        patient_data = {
            'name': 'Test Patient',
            'age': '28',
            'gender': 'male',
            'weight': '70',
            'contact': '9876543210',
            'symptoms': ['fever', 'cold'],
            'payment_mode': 'GPay',
            'consultation_fee': '50'
        }
        res = self.client.post('/patient/add', data=patient_data, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Official Tax Invoice', res.data)
        self.assertIn(b'Test Patient', res.data)
        self.assertIn(b'Paracetamol', res.data)
        self.assertIn(b'Cetirizine', res.data)
        self.assertIn(b'Scan & Pay via UPI', res.data)

    def test_03_appointments_flow(self):
        self.client.post('/login', data={'username': 'admin', 'password': '1234'})

        # Book appointment
        appt_data = {
            'patient_name': 'Alice Smith',
            'doctor': 'Dr. Rajesh Sharma (General Physician)',
            'appoint_date': '2026-08-15',
            'appoint_time': '10:00 AM',
            'contact': '9988776655',
            'notes': 'Routine Checkup'
        }
        res = self.client.post('/appointments', data=appt_data, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Alice Smith', res.data)
        self.assertIn(b'Dr. Rajesh Sharma', res.data)

    def test_04_patient_search(self):
        self.client.post('/login', data={'username': 'admin', 'password': '1234'})

        # Search by query
        res = self.client.get('/search?q=Test+Patient')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Test Patient', res.data)

    def test_05_medicines_api(self):
        res = self.client.get('/api/medicines')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn('fever', data)
        self.assertIn('cold', data)

if __name__ == '__main__':
    unittest.main()
