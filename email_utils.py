from flask_mail import Mail, Message
from flask import render_template_string

mail = Mail()

def send_verification_email(user, token):
    msg = Message('Verify Your Email',
                  recipients=[user.email])
                  
    verification_link = f'http://localhost:5000/verify_email/{token}'
    
    msg.html = f'''
    <h1>Welcome!</h1>
    <p>Thank you for signing up. Please click the link below to verify your email address:</p>
    <p><a href="{verification_link}">Click here to verify your email</a></p>
    <p>If you did not sign up for this account, please ignore this email.</p>
    '''
    
    mail.send(msg)

def send_password_reset_email(user, token):
    msg = Message('Password Reset Request',
                  recipients=[user.email])
                  
    reset_link = f'http://localhost:5000/reset_password/{token}'
    
    msg.html = f'''
    <h1>Password Reset Request</h1>
    <p>To reset your password, click the following link:</p>
    <p><a href="{reset_link}">Click here to reset your password</a></p>
    <p>If you did not request a password reset, please ignore this email.</p>
    <p>This link will expire in 10 minutes.</p>
    '''
    
    mail.send(msg)
