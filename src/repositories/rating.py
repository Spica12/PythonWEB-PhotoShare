from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class RatingRepo:

    def __init__(self, db):
        """
        The __init__ function is called when the class is instantiated.
        It sets up the database connection and creates a new session for each request.

        :param self: Represent the instance of the class
        :param db: Pass in a database connection to the class
        :return: Nothing
        """
        self.db: AsyncSession = db
