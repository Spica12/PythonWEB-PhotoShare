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
    fm = FastMail(conf)
