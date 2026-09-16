import os
import unittest
from datetime import date
os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
from app import create_app
from app.extensions import db
from app.models import User, Student, Room, RoomSlot, Allocation, OutingRequest, Payment
from flask_jwt_extended import create_access_token

class FeatureTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.ctx = self.app.app_context(); self.ctx.push()
        self.client = self.app.test_client()
        owner = User.query.filter_by(role='owner').first()
        self.admin = self.headers(owner)
        student = Student(student_code='TEST101', full_name='Test Student', phone='1234567890', email='student101@hostel.com')
        other = Student(student_code='TEST102', full_name='Other Student', phone='1234567891')
        db.session.add_all([student, other]); db.session.flush()
        user = User(name='Test Student', email='test@local', role='student', student_id=student.id)
        user.set_password('test'); db.session.add(user); db.session.commit()
        self.student_id = student.id; self.other_id = other.id; self.student = self.headers(user)
    def headers(self, user):
        return {'Authorization': 'Bearer ' + create_access_token(identity=str(user.id), additional_claims={'role': user.role})}
    def tearDown(self):
        db.session.remove(); self.ctx.pop()
    def test_capacity(self):
        room = Room.query.first()
        slot = RoomSlot.query.filter_by(room_id=room.id, code='B4').first()
        db.session.add(Allocation(student_id=self.student_id, slot_id=slot.id)); db.session.commit()
        path = f'/api/rooms/{room.id}'
        self.assertEqual(self.client.put(path, headers=self.admin, json={'bedroom_capacity':0}).status_code,400)
        response = self.client.put(path, headers=self.admin, json={'bedroom_capacity':1,'hall_capacity':0})
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.json['capacity'],1)
        self.assertEqual(response.json['occupied'],1)
        for count in [2,1,2]:
            self.assertEqual(self.client.put(path,headers=self.admin,json={'bedroom_capacity':count}).json['capacity'],count)
        self.assertEqual(self.client.put(path,headers=self.admin,json={'hall_capacity':-1}).status_code,400)
    def test_admin_registration(self):
        response = self.client.post('/api/auth/register', json={
            'name': 'New Admin', 'email': 'new.admin@example.com', 'password': 'secure-pass-123'
        })
        self.assertEqual(response.status_code, 201)
        self.assertTrue(response.json['access_token'])
        user = User.query.filter_by(email='new.admin@example.com').first()
        self.assertEqual(user.role, 'staff')
        self.assertNotEqual(user.password_hash, 'secure-pass-123')
        self.assertTrue(user.check_password('secure-pass-123'))
        duplicate = self.client.post('/api/auth/register', json={
            'name': 'New Admin', 'email': 'new.admin@example.com', 'password': 'secure-pass-123'
        })
        self.assertEqual(duplicate.status_code, 409)
    def test_movement(self):
        outing = OutingRequest(student_id=self.student_id, outing_date=date.today(), leaving_time='10:00', expected_return_time='18:00',destination='College',reason='Class')
        db.session.add(outing); db.session.commit(); path=f'/api/outings/{outing.id}'
        self.assertEqual(self.client.post(path+'/returned',headers=self.admin).status_code,409)
        for action in ['approve','out','returned']:
            response=self.client.post(path+'/'+action,headers=self.admin)
            self.assertEqual(response.status_code,200)
        self.assertTrue(response.json['actual_leaving_time']); self.assertTrue(response.json['actual_return_time'])
        self.assertEqual(self.client.get('/api/outings',headers=self.admin).json['summary']['returned'],1)
        self.assertEqual(self.client.post(path+'/out',headers=self.admin).status_code,409)
    def test_complaints_and_stream(self):
        self.assertEqual(self.client.post('/api/complaints',headers=self.student,json={}).status_code,400)
        response=self.client.post('/api/complaints',headers=self.student,json={'student_id':self.other_id,'title':'Leaking Pipe','description':'Washbasin leak'})
        self.assertEqual(response.status_code,201)
        self.assertEqual(response.json['student'],'Test Student')
        self.assertEqual(len(self.client.get('/api/complaints',headers=self.student).json['complaints']),1)
        self.assertEqual(self.client.get('/api/admin/complaints',headers=self.admin).json['complaints'][0]['title'], 'Leaking Pipe')
        self.assertEqual(self.client.patch(f"/api/admin/complaints/{response.json['id']}",headers=self.admin,json={'status':'RESOLVED'}).json['status'],'RESOLVED')
    def test_receipt_privacy(self):
        payment=Payment(student_id=self.other_id,amount=100,method='Cash',receipt_no='TEST-REC')
        db.session.add(payment); db.session.commit()
        self.assertEqual(self.client.get(f'/api/payments/{payment.id}/receipt.pdf',headers=self.student).status_code,403)
        payment.student_id=self.student_id; db.session.commit()
        response=self.client.get(f'/api/payments/{payment.id}/receipt.pdf',headers=self.student)
        self.assertEqual(response.status_code,200); self.assertTrue(response.data.startswith(b'%PDF'))

if __name__ == '__main__': unittest.main()
