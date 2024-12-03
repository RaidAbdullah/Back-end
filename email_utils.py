from flask_mail import Mail, Message

mail = Mail()

def send_email(subject, sender, recipients, text_body, html_body):
    """Utility function to send emails"""
    try:
        msg = Message(subject, sender=sender, recipients=recipients)
        msg.body = text_body
        msg.html = html_body
        mail.send(msg)
    except Exception as e:
        print(f"Error sending email: {str(e)}")

def send_verification_code(user, code):
    msg = Message('Verify Your Email',
                  recipients=[user.email])
                  
    msg.html = f'''
    <h1>Welcome!</h1>
    <p>Thank you for signing up. Your verification code is:</p>
    <h2 style="color: #4a90e2; font-size: 24px; text-align: center; padding: 10px; background: #f5f5f5; border-radius: 5px;">{code}</h2>
    <p>Enter this code in the application to verify your account.</p>
    <p>If you did not sign up for this account, please ignore this email.</p>
    <p>This code will expire in 30 minutes.</p>
    '''
    
    mail.send(msg)

def send_reset_code(user, code):
    msg = Message('Password Reset Code',
                  recipients=[user.email])
                  
    msg.html = f'''
    <h1>Password Reset Code</h1>
    <p>Your password reset code is:</p>
    <h2 style="color: #4a90e2; font-size: 24px; text-align: center; padding: 10px; background: #f5f5f5; border-radius: 5px;">{code}</h2>
    <p>Enter this code in the application to reset your password.</p>
    <p>If you did not request a password reset, please ignore this email.</p>
    <p>This code will expire in 30 minutes.</p>
    '''
    
    mail.send(msg)
