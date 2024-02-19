from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.photos import PhotoRepo


class PhotoService:

    def __init__(self, db: AsyncSession):
        """
        The __init__ function is called when the class is instantiated.
        It's used to initialize variables and do other setup tasks that need to be done every time an object of this class is created.

        :param self: Represent the instance of the class
        :param db: AsyncSession: Create a connection to the database
        :return: Nothing
        """
        self.repo = PhotoRepo(db=db)
