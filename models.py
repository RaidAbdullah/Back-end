from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from time import time
from datetime import datetime
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
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
        
    def get_reset_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            Config.SECRET_KEY,
            algorithm='HS256'
        )
        
    def get_verification_token(self, expires_in=86400):
        return jwt.encode(
            {'verify_email': self.id, 'exp': time() + expires_in},
            Config.SECRET_KEY,
            algorithm='HS256'
        )
    
    @staticmethod
    def verify_reset_token(token):
        try:
            id = jwt.decode(token, Config.SECRET_KEY, algorithms=['HS256'])['reset_password']
            return User.query.get(id)
        except:
            return None
            
    @staticmethod
    def verify_email_token(token):
        try:
            id = jwt.decode(token, Config.SECRET_KEY, algorithms=['HS256'])['verify_email']
            return User.query.get(id)
        except:
            return None
