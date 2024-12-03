from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_socketio import SocketIO, emit, join_room, leave_room
from Scraper import PropertyDealsScraper
from models import db, User, Property
from email_utils import mail, send_verification_email, send_password_reset_email
from config import Config
import json
import requests
from datetime import datetime

app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
CORS(app)
db.init_app(app)
mail.init_app(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize login manager
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Socket.IO events
@socketio.on('connect')
def handle_connect():
    if current_user.is_authenticated:
        # Join a room specific to this user
        join_room(f'user_{current_user.id}')
        emit('connection_status', {'status': 'connected', 'user_id': current_user.id})

@socketio.on('disconnect')
def handle_disconnect():
    if current_user.is_authenticated:
        leave_room(f'user_{current_user.id}')

def notify_users_of_anomaly(anomaly_data):
    """Helper function to send real-time notifications to all users"""
    socketio.emit('anomaly_alert', anomaly_data, broadcast=True)

# Create database tables
with app.app_context():
    db.create_all()

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "message": "API is running"})

@app.route('/api/example', methods=['GET'])
def get_example():
    return jsonify({
        "message": "Example data",
        "data": [
            {"id": 1, "name": "Item 1"},
            {"id": 2, "name": "Item 2"}
        ]
    })

@app.route('/api/example', methods=['POST'])
def create_example():
    data = request.get_json()
    # Process the data here
    return jsonify({
        "message": "Data received successfully",
        "received_data": data
    }), 201

@app.route('/api/scrape', methods=['GET'])
def scrape_data():
    try:
        # Static URL for the scraping target
        url = "https://srem.moj.gov.sa/transactions-info"
        
        # Initialize and run the scraper
        scraper = PropertyDealsScraper(url)
        data_without_category, data_with_category = scraper.scrape_daily_deals()
        
        # First API call - send data without category for classification
        response1 = requests.post(
            'https://faisalalmane2.pythonanywhere.com/classify',
            json=data_without_category
        )
        
        if response1.status_code != 200:
            return jsonify({
                "error": "First API call failed",
                "status": response1.status_code,
                "message": response1.text
            }), 500

        # Get the classified data
        classified_data = response1.json()

        # Second API call - send classified data for anomaly detection
        response2 = requests.post(
            'https://faisalalmane2.pythonanywhere.com/detect_anomalies',
            json=classified_data
        )

        if response2.status_code != 200:
            return jsonify({
                "error": "Second API call failed",
                "status": response2.status_code,
                "message": response2.text
            }), 500

        # Get the anomaly results
        anomaly_results = response2.json()

        # Store results in database
        for property_data in anomaly_results:
            # Create new Property record
            property_entry = Property(
                district=property_data.get('district'),
                price=property_data.get('price'),
                area=property_data.get('area'),
                price_per_meter=property_data.get('price_per_meter'),
                is_anomaly=property_data.get('is_anomaly', False),
                anomaly_score=property_data.get('anomaly_score', 0.0),
                date_added=datetime.now()
            )
            
            db.session.add(property_entry)
            
            # If it's an anomaly, notify connected users
            if property_entry.is_anomaly:
                notify_users_of_anomaly({
                    'district': property_entry.district,
                    'price': property_entry.price,
                    'area': property_entry.area,
                    'price_per_meter': property_entry.price_per_meter,
                    'anomaly_score': property_entry.anomaly_score
                })
        
        db.session.commit()

        return jsonify({
            "message": "Scraping and processing completed successfully",
            "anomalies_found": len([p for p in anomaly_results if p.get('is_anomaly', False)])
        }), 200

    except Exception as e:
        return jsonify({
            "error": "An error occurred during scraping",
            "message": str(e)
        }), 500

@app.route('/api/signup', methods=['POST'])
def signup():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        username = data.get('username')
        
        if not email or not password or not username:
            return jsonify({"error": "Email, password, and username are required"}), 400
            
        if User.query.filter_by(email=email).first():
            return jsonify({"error": "Email already registered"}), 400
            
        if User.query.filter_by(username=username).first():
            return jsonify({"error": "Username already taken"}), 400
            
        user = User(email=email, username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        # Send verification email
        token = user.get_verification_token()
        send_verification_email(user, token)
        
        return jsonify({
            "message": "Registration successful. Please check your email to verify your account."
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400
            
        user = User.query.filter_by(email=email).first()
        
        if not user or not user.check_password(password):
            return jsonify({"error": "Invalid email or password"}), 401
            
        if not user.is_verified:
            return jsonify({"error": "Please verify your email before logging in"}), 401
            
        login_user(user)
        return jsonify({"message": "Login successful", "email": user.email})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/forgot-password', methods=['POST'])
def forgot_password():
    try:
        data = request.get_json()
        email = data.get('email')
        
        if not email:
            return jsonify({"error": "Email is required"}), 400
            
        user = User.query.filter_by(email=email).first()
        
        if not user:
            return jsonify({"error": "Email not found"}), 404
            
        token = user.get_reset_token()
        send_password_reset_email(user, token)
        
        return jsonify({
            "message": "Password reset instructions have been sent to your email."
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/verify_email/<token>')
def verify_email(token):
    try:
        user = User.verify_email_token(token)
        
        if not user:
            return jsonify({"error": "Invalid or expired verification link"}), 400
            
        user.is_verified = True
        db.session.commit()
        
        return jsonify({"message": "Email verified successfully. You can now log in."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/reset_password/<token>', methods=['POST'])
def reset_password(token):
    try:
        user = User.verify_reset_token(token)
        
        if not user:
            return jsonify({"error": "Invalid or expired reset link"}), 400
            
        data = request.get_json()
        new_password = data.get('new_password')
        
        if not new_password:
            return jsonify({"error": "New password is required"}), 400
            
        user.set_password(new_password)
        db.session.commit()
        
        return jsonify({"message": "Password has been reset successfully. You can now log in with your new password."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
