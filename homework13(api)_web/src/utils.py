import os
from src.config import config
from dotenv import load_dotenv
from passlib.context import CryptContext
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig

load_dotenv()

conf = ConnectionConfig(
    MAIL_USERNAME=config.MAIL_USERNAME,
    MAIL_PASSWORD=config.MAIL_PASSWORD,
    MAIL_FROM=config.MAIL_USERNAME,
    MAIL_PORT=config.MAIL_PORT,
    MAIL_SERVER=config.MAIL_SERVER,
    MAIL_FROM_NAME="Test",
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

async def send_verification_email(email: str, token: str):
    message = MessageSchema(
        subject="Verify your email",
        recipients=[email],
        body=f"Please verify your email by clicking on the following link: http://localhost:8000/auth/verify?token={token}",
        subtype="html"
    )
    fm = FastMail(conf)
    await fm.send_message(message)
