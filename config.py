import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    
    # PostgreSQL Database settings
    database_url = os.environ.get('DATABASE_URL', 'postgresql+pg8000://postgres:123456@localhost:5432/postgres')
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    SQLALCHEMY_DATABASE_URI = database_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Mail settings
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'raiiidAbdullah@gmail.com'  # Replace with your email
    MAIL_PASSWORD = 'bywb eaqt ujwf igkt'     # Replace with your app password
    MAIL_DEFAULT_SENDER = 'raiiidAbdullah@gmail.com'  # Replace with your email
