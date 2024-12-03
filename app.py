from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_migrate import Migrate
from Scraper import PropertyDealsScraper
from models import db, User, Property
from email_utils import mail, send_verification_code, send_reset_code
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
migrate = Migrate(app, db)
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

@app.route('/scrape', methods=['GET'])
def scrape_data():
    try:
        # Static URL for the scraping target
        url = "https://srem.moj.gov.sa/transactions-info"
        
        # Initialize and run the scraper
        scraper = PropertyDealsScraper(url)
        data_without_category, data_with_category = scraper.scrape()
        
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
            'https://faisalalmane.pythonanywhere.com/classify',
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
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        
        if not username or not email or not password:
            return jsonify({"error": "Username, email and password are required"}), 400
            
        if User.query.filter_by(username=username).first():
            return jsonify({"error": "Username already exists"}), 400
            
        if User.query.filter_by(email=email).first():
            return jsonify({"error": "Email already registered"}), 400
            
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.flush()  # This assigns an id to the user
        
        # Generate verification code and send email
        verification_code = user.generate_verification_code()
        send_verification_code(user, verification_code)
        db.session.commit()
        
        return jsonify({
            "message": "Registration successful. Please check your email for the verification code.",
            "username": user.username
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({"error": "Username and password are required"}), 400
            
        user = User.query.filter_by(username=username).first()
        
        if not user or not user.check_password(password):
            return jsonify({"error": "Invalid username or password"}), 401
            
        if not user.is_verified:
            return jsonify({"error": "Please verify your account before logging in"}), 401
            
        login_user(user)
        return jsonify({"message": "Login successful", "username": user.username})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/verify_account', methods=['POST'])
def verify_account():
    try:
        data = request.get_json()
        username = data.get('username')
        verification_code = data.get('verification_code')
        
        if not username or not verification_code:
            return jsonify({"error": "Username and verification code are required"}), 400
            
        user = User.query.filter_by(username=username).first()
        if not user:
            return jsonify({"error": "User not found"}), 404
            
        if user.verify_code(verification_code):
            user.is_verified = True
            db.session.commit()
            return jsonify({"message": "Account verified successfully. You can now log in."})
        else:
            return jsonify({"error": "Invalid verification code"}), 400
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/forgot_password', methods=['POST'])
def forgot_password():
    try:
        data = request.get_json()
        username = data.get('username')
        
        if not username:
            return jsonify({"error": "Username is required"}), 400
            
        user = User.query.filter_by(username=username).first()
        
        if not user:
            return jsonify({"error": "User not found"}), 404
            
        reset_code = user.generate_reset_code()
        send_reset_code(user, reset_code)
        
        return jsonify({
            "message": "Password reset code has been sent to your email."
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/reset_password', methods=['POST'])
def reset_password():
    try:
        data = request.get_json()
        username = data.get('username')
        reset_code = data.get('reset_code')
        new_password = data.get('new_password')
        
        if not username or not reset_code or not new_password:
            return jsonify({"error": "Username, reset code and new password are required"}), 400
            
        user = User.query.filter_by(username=username).first()
        if not user:
            return jsonify({"error": "User not found"}), 404
            
        if user.verify_reset_code(reset_code):
            user.set_password(new_password)
            db.session.commit()
            return jsonify({"message": "Password has been reset successfully. You can now log in with your new password."})
        else:
            return jsonify({"error": "Invalid reset code"}), 400
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
