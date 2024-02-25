from pathlib import Path

from pydantic import ConfigDict, EmailStr, field_validator
from pydantic_settings import BaseSettings

# TODO Testing
import logging
# logging global rules
LOG_DIR = "src/logs"
logging.basicConfig(
    format="%(asctime)s %(message)s",
    level=logging.INFO,
    handlers=[
        logging.FileHandler(f"{LOG_DIR}/test.log"),
        # logging.StreamHandler()
    ],
)
# logging.getLogger("bcrypt").setLevel(logging.ERROR)

class Settings(BaseSettings):
    DB_URL: str = "postgresql+asyncpg://postgres:567234@0.0.0.0:5432/abc"
    SECRET_KEY_JWT: str = "1234567890"

    ALGORITHM: str = "HS256"
    MAIL_USERNAME: str = "example@gmail.com"
    MAIL_PASSWORD: str = "passwoord"
    MAIL_FROM: str = "user@gmail.com"
    MAIL_PORT: int = 6379
    MAIL_SERVER: str = "smtp.mail.com"

    CLOUDINARY_NAME: str = "abc"
    CLOUDINARY_API_KEY: int = 000000000000000
    CLOUDINARY_API_SECRET: str = "secret"

    BASE_DIR: Path = Path(__file__).parent.parent.parent

    model_config = ConfigDict(
        extra="ignore", env_file=".env", env_file_encoding="utf-8"
    )

    @field_validator("ALGORITHM")
    @classmethod
    def validade_algorithm(cls, value):
        """
        The validade_algorithm function is a helper function that validates the algorithm used to sign the JWT.
            It raises an error if it's not HS256 or HS512.

        :param cls: Pass the class that is being validated
        :param value: Pass the value of the algorithm parameter in the jwt
        :return: The value of the algorithm
        """
        if value not in ["HS256", "HS512"]:
            raise ValueError("Algorithm must be HS256 or HS512")

        return value


config = Settings()
