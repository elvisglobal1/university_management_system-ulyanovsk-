import random
import string
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_password(length=10):
    """Generate a random password"""
    characters = string.ascii_letters + string.digits + "!@#$%^&*"
    password = ''.join(random.choice(characters) for _ in range(length))
    return password

def send_email(email: str, password: str):
    """
    Simulate sending email with password
    In production, use SMTP like:
    - smtplib for Gmail/Yandex
    - SendGrid API
    - AWS SES
    """
    logger.info(f"=== EMAIL SIMULATION ===")
    logger.info(f"To: {email}")
    logger.info(f"Subject: Your University System Password")
    logger.info(f"Body: Your password is: {password}")
    logger.info(f"Please change it after first login.")
    logger.info(f"========================")
    
    # In production, uncomment this:
    """
    import smtplib
    from email.mime.text import MIMEText
    
    msg = MIMEText(f"Your password is: {password}\nPlease change it after first login.")
    msg['Subject'] = 'Your University System Password'
    msg['From'] = 'noreply@university.com'
    msg['To'] = email
    
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login('your-email@gmail.com', 'app-password')
        server.send_message(msg)
    """
