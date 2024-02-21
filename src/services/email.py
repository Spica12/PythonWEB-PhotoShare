from fastapi_mail import ConnectionConfig, FastMail
from pydantic import EmailStr

from src.conf.config import config
from src.services.auth import auth_service


class EmailService:
    conf = ConnectionConfig(
        MAIL_USERNAME=config.MAIL_USERNAME,
        MAIL_PASSWORD=config.MAIL_PASSWORD,
        MAIL_FROM=config.MAIL_FROM,
        MAIL_PORT=config.MAIL_PORT,
        MAIL_SERVER=config.MAIL_SERVER,
        MAIL_FROM_NAME="FastContacts",
        MAIL_STARTTLS=False,
        MAIL_SSL_TLS=True,
        USE_CREDENTIALS=True,
        VALIDATE_CERTS=True,
        TEMPLATE_FOLDER=config.BASE_DIR / "templates",
    )


    async def email_service(email: EmailStr, username: str, host: str):
        try:
            token_verification = auth_service.create_email_token({"sub": email})
            message = MessageSchema(
                subject="Confirm your email",
                recipients=[email],
                template_body={"host": host, "username": username, "token": token_verification},
                subtype=MessageType.html
            )
            fm = FastMail(conf)
            await fm.send_message(message, template_name="verify_email.html")
        except ConnectionErrors as err:
            print(err)