import unittest
from flask import jsonify
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import create_app
from database import db
from models import Bank

class FlaskTestCase(unittest.TestCase):
    def setUp(self):
        global app
        app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "postgresql://postgres:root@localhost:5432/test_db",
        "WTF_CSRF_ENABLED": False
        #"JSONIFY_PRETTYPRINT_REGULAR": True
        })
        self.app = app.test_client()
        
        with app.app_context():
            db.create_all()
            test_wallets = [
            Bank(wallet_uuid='2f13b6e0-ba48-4a14-a0e4-538fbd5a4bec', wallet_amount=5000),
            Bank(wallet_uuid='c1d488f4-b53f-4ca2-b420-2418169642d5', wallet_amount=2000),
            Bank(wallet_uuid='78cefbe7-35a9-4a60-8c22-c5360d1bf7e6', wallet_amount=0)
            ]
            db.session.add_all(test_wallets)
            db.session.commit()
    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()
    
    def test_index(self):
        response = self.app.get('/')
        self.assertEqual(response.text, "Hello")
    
    def test_get_wallets(self):
        response = self.app.get('/api/v1/wallets').json

        with app.app_context():
            wallets = db.session.query(Bank).all()
            data_list = []
            for wallet in wallets:
                wallet_data = {'wallet_uuid':wallet.wallet_uuid,
                            'amount':wallet.wallet_amount}
                data_list.append(wallet_data)
            wallets = jsonify({'wallets':data_list}).json
            self.assertEqual(wallets, response)

    def test_get_wallet_balance(self):
        wallet_uuid = '2f13b6e0-ba48-4a14-a0e4-538fbd5a4bec'
        response = self.app.get(f'/api/v1/wallets/{wallet_uuid}').json
        with app.app_context():  
            wallet = db.session.query(Bank).filter(Bank.wallet_uuid==wallet_uuid).first()
            result = jsonify({'amount':wallet.wallet_amount}).json
            self.assertEqual(response,result)
        
    def test_deposit(self):
        data = {
            "operationType": "DEPOSIT",
            "amount": 1000
        }
        wallet_uuid = '2f13b6e0-ba48-4a14-a0e4-538fbd5a4bec'
        response = self.app.post(f'/api/v1/wallets/{wallet_uuid}/operation', json=data)
        with app.app_context():
            operation_type = data['operationType'].lower()
            if operation_type == "deposit":
                result = {'amount':"6000.0000"}
                self.assertEqual(response.json, result)
            else:
                raise AssertionError
            
    def test_withdraw(self):
        data = {
            "operationType": "WITHDRAW",
            "amount": 1000
        }
        wallet_uuid = 'c1d488f4-b53f-4ca2-b420-2418169642d5'
        response = self.app.post(f'/api/v1/wallets/{wallet_uuid}/operation', json=data)
        with app.app_context():
            operation_type = data['operationType'].lower()
            if operation_type == "withdraw":
                result = {'amount':"1000.0000"}
                self.assertEqual(response.json, result)
            else:
                raise AssertionError
            
    def test_withdraw_low(self):
        data = {
            "operationType": "withdraw",
            "amount": 1000
        }
        wallet_uuid = '78cefbe7-35a9-4a60-8c22-c5360d1bf7e6'
        response = self.app.post(f'/api/v1/wallets/{wallet_uuid}/operation', json=data)
        with app.app_context():
            operation_type = data['operationType'].lower()
            if operation_type == "withdraw":
                self.assertEqual(response.text, "Недостаточно средств")
            else:
                raise AssertionError
        
    def test_no_wallet(self):
        data = {
            "operationType": "withdraw",
            "amount": 1000
        }
        wallet_uuid = '16016ce8-3b6b-4986-ab5a-6771c5ed971b'
        response = self.app.post(f'/api/v1/wallets/{wallet_uuid}/operation', json=data)
        with app.app_context():
            self.assertEqual(response.text, "Кошелек не найден")

    def test_invalid_json(self):
        data = {
            "operationType": "wrong_op",
            "amount": 10000
        }
        wallet_uuid = '78cefbe7-35a9-4a60-8c22-c5360d1bf7e6'
        response = self.app.post(f'/api/v1/wallets/{wallet_uuid}/operation', json=data)
        with app.app_context():
            self.assertEqual(response.text, "Невалидный JSON")

    def test_total_failure(self):
        data = {
            "Total":"failure"
        }
        wallet_uuid = '78cefbe7-35a9-4a60-8c22-c5360d1bf7e6'
        response = self.app.post(f'/api/v1/wallets/{wallet_uuid}/operation', json=data)
        with app.app_context():
            self.assertEqual(response.text, "Ошибка при обработке данных")

if __name__ == '__main__':
    unittest.main()