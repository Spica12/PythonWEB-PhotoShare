from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from src.routers import auth, users, photos

from src.dependencies.database import get_db
from src.conf.config import config

app = FastAPI()

app.include_router(auth.router_auth, prefix="/api")
app.include_router(users.router_users, prefix="/api")
app.include_router(photos.router_photos, prefix="/api")


origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory=config.BASE_DIR / "src" / "templates")

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse(
        "index.html",
        context={"request": request}
    )
    # return {"message": "Main page: Python WEB group #1 project"}


@app.get("/api/healthchecker")
async def healthchecker(db: AsyncSession = Depends(get_db)):
    """
    The healthchecker function is a simple function that checks if the database is up and running.
    It does this by making a request to the database, and checking if it returns any results.
    If it doesn't return any results, then we know something's wrong with our connection.

    :param db: AsyncSession: Pass the database connection to the function
    :return: A dictionary with the key &quot;message&quot; and value &quot;welcome to fastapi!&quot;
    """
    try:
        # Make request
        result = await db.execute(text("SELECT 1"))
        result = result.fetchone()
        if result is None:
            raise HTTPException(
                status_code=500, detail="Database is not configured correctly"
            )
        return {"message": "Welcome to FastAPI!"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error connecting to the database")
