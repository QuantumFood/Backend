from passlib.context import CryptContext
import smtplib 
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os 
from dotenv import load_dotenv


load_dotenv()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str):
    return pwd_context.hash(password)

SMTP_EMAIL = os.getenv("SMTP_EMAIL")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

def send_mail(to_addr):
    from_address = SMTP_EMAIL
    from_password = SMTP_PASSWORD
    
    msg = MIMEMultipart()
    msg['From'] = from_address
    msg['To'] = to_addr
    msg['Subject'] = "QUANTUMFOOD - YOUR ORDER HAS BEEN RECIEVED"

    body = """
    Hello,

    Your food order has been recieved.
    Please don't forget to collect your food.

    Thank you. 
    """
    msg.attach(MIMEText(body, 'plain'))
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(from_address, from_password)
        text = msg.as_string()
        server.sendmail(from_address, to_addr, text)
        server.quit()
        return True
    except Exception as e:
        print(e)
        return False