from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from fastapi_mail.errors import ConnectionErrors
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
        TEMPLATE_FOLDER=config.BASE_DIR / "src" / "services" / "templates",
    )
    fm = FastMail(conf)


    async def send_varification_mail(self, email: EmailStr, username: str, host: str):
        try:
            token_verification = auth_service.create_email_token({"sub": email})
            message = MessageSchema(
                subject="Confirm your email",
                recipients=[email],
                template_body={"host": host, "username": username, "token": token_verification},
                subtype=MessageType.html
            )
            await self.fm.send_message(message, template_name="verify_email.html")

        except ConnectionErrors as err:
            print(err)

    async def send_password_reset_notification(self, email, new_password):
        try:
            # Generate a new password reset token
            token_reset = auth_service.create_email_token({"sub": email})

            # Prepare the email message
            message = MessageSchema(
                subject="Password Reset",
                recipients=[email],
                template_body={"new_password": new_password, "token_reset": token_reset},
                subtype=MessageType.html
            )

            # Send the email using EmailService
            await self.fm.send_message(message, template_name="password_reset_email.html")

        except ConnectionErrors as err:
            print(err)