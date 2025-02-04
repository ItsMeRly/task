from sqlalchemy.dialects.postgresql import UUID
from flask_sqlalchemy import SQLAlchemy
import uuid
from database import db

class Bank(db.Model):
    __tablename__ = 'wallets'
    wallet_uuid = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    wallet_amount = db.Column(db.Numeric(18,4))
