from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from time import time
from datetime import datetime, timedelta
from config import Config

db = SQLAlchemy()

class Property(db.Model):
    __tablename__ = 'property'
    
    id = db.Column(db.Integer, primary_key=True)
    deal_number = db.Column(db.String(100))
    property_type = db.Column(db.String(100))
    location = db.Column(db.String(200))
    price = db.Column(db.Float)
    area = db.Column(db.Float)
    category = db.Column(db.String(100))
    is_anomaly = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'deal_number': self.deal_number,
            'property_type': self.property_type,
            'location': self.location,
            'price': self.price,
            'area': self.area,
            'category': self.category,
            'is_anomaly': self.is_anomaly,
            'created_at': self.created_at.isoformat()
        }

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    is_verified = db.Column(db.Boolean, default=False)
    verification_code = db.Column(db.String(6))
    reset_code = db.Column(db.String(6))
    verification_code_expires = db.Column(db.DateTime)
    reset_code_expires = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_verification_code(self):
        import random
        import string
        code = ''.join(random.choices(string.digits, k=6))
        self.verification_code = code
        self.verification_code_expires = datetime.utcnow() + timedelta(minutes=30)
        return code

    def verify_code(self, code):
        if not self.verification_code or not self.verification_code_expires:
            return False
        if datetime.utcnow() > self.verification_code_expires:
            return False
        is_valid = self.verification_code == code
        if is_valid:
            # Clear the verification code after successful verification
            self.verification_code = None
            self.verification_code_expires = None
            db.session.commit()
        return is_valid

    def generate_reset_code(self):
        import random
        import string
        code = ''.join(random.choices(string.digits, k=6))
        self.reset_code = code
        self.reset_code_expires = datetime.utcnow() + timedelta(minutes=30)
        db.session.commit()
        return code

    def verify_reset_code(self, code):
        if not self.reset_code or not self.reset_code_expires:
            return False
        if datetime.utcnow() > self.reset_code_expires:
            return False
        is_valid = self.reset_code == code
        if is_valid:
            # Clear the reset code after successful verification
            self.reset_code = None
            self.reset_code_expires = None
            db.session.commit()
        return is_valid
