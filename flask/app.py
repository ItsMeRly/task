from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from models import Bank
from decimal import Decimal
from werkzeug.exceptions import BadRequest
from database import db


migrate = Migrate()

def create_app(config=None):
    app = Flask(__name__)
    CORS(app)

    app.config.from_mapping(
        CORS_HEADERS = 'Content-Type',
        #app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:root@localhost:5432/test_db"
        SQLALCHEMY_DATABASE_URI = "postgresql://user:pass@postgres:5432/bank_db",
        #SQLALCHEMY_DATABASE_URI = "postgresql://postgres:root@localhost:5432/purse",
        SQLALCHEMY_TRACK_MODIFICATIONS = False

    )
    if config:
        app.config.update(config)

    db.init_app(app)
    migrate.init_app(app,db)

    @app.route('/')
    def index():
        return "Hello"

    @app.route('/api/v1/wallets/<WALLET_UUID>/operation', methods=['POST'])
    def operation(WALLET_UUID):
        try:
            data = request.get_json()
            operation_type = data['operationType'].lower()
            amount = Decimal(data['amount'])
            wallet = db.session.query(Bank).filter(Bank.wallet_uuid==WALLET_UUID).first()

            if wallet is None:
                return "Кошелек не найден"
            
            if operation_type == "deposit":
                wallet.wallet_amount += amount
                db.session.commit()
            
            elif operation_type == "withdraw":
                if wallet.wallet_amount < amount:
                    return "Недостаточно средств"
                else:
                    wallet.wallet_amount -= amount
                    db.session.commit()
            else:
                raise BadRequest

            return {'amount':wallet.wallet_amount}
        
        except BadRequest:
            return "Невалидный JSON"

        except:
            return "Ошибка при обработке данных"

    @app.route('/api/v1/wallets/<WALLET_UUID>', methods=['GET'])
    def get_amount(WALLET_UUID):
        try:
            wallet = db.session.query(Bank).filter(Bank.wallet_uuid==WALLET_UUID).first()
            return {'amount':wallet.wallet_amount}
        except:
            return "Ошибка при обработке данных"

    @app.route('/api/v1/wallets', methods=['GET'])
    def get_wallets():
        #try:
            wallets = db.session.query(Bank).all()
            if wallets == None:
                return "Кошельки не найдены"
            data_list = []
            for wallet in wallets:
                wallet_data = {'wallet_uuid':wallet.wallet_uuid,
                            'amount':wallet.wallet_amount}
                data_list.append(wallet_data)
            return jsonify({'wallets':data_list})
        
        #except:
            #return "Ошибка при обработке данных"
        
    if __name__ == '__main__':
        app.run(host='0.0.0.0', debug=True)

    return app
    
create_app()