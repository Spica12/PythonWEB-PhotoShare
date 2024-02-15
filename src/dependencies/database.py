import contextlib

from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine

from src.conf.config import config


class DataBaseSessionManager:
    def __init__(self, url: str):
        """
        The __init__ function is the constructor for the class. It initializes
        the engine and session_maker attributes of the class.

        :param self: Represent the instance of the class
        :param url: str: Create the engine
        :return: Nothing
        """
        self.engine: AsyncEngine | None = create_async_engine(url)
        self._session_maker = async_sessionmaker(
            autoflush=False, autocommit=False, bind=self.engine
        )

    @contextlib.asynccontextmanager
    async def session(self):
        """
        The session function is a context manager that provides a transactional scope around a series of operations.
        It will automatically rollback the session if an exception occurs, or commit the session otherwise.

        :param self: Represent the instance of the class
        :return: A context manager that can be used in a with statement
        """
        if self._session_maker is None:
            raise Exception("Session is not initialized")
        session = self._session_maker()
        try:
            yield session
        except Exception as e:
            print(e)
            await session.rollback()
        finally:
            await session.close()


sessionmanager = DataBaseSessionManager(config.DB_URL)


async def get_db():
    """
    The get_db function is a coroutine that returns an async context manager.
    The context manager yields a database session, which can be used to query the database.
    When the block of code exits, the session is automatically closed.

    :return: A context manager
    """
    async with sessionmanager.session() as session:
        yield session
