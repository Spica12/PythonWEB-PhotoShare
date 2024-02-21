from sqlalchemy import Column, String, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class BlacklistTokenModel(Base):
    __tablename__ = 'blacklist_tokens'

    id = Column(int, primary_key=True, index=True)
    token = Column(String, index=True)
    created_at = Column(DateTime)

    def __init__(self, token: str):
        self.token = token
