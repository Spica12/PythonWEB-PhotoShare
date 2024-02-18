from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.dependencies.database import get_db

router_images = APIRouter(prefix="/images", tags=["Images"])


@router_images.get("/", response_model=None, dependencies=None, status_code=None)
async def show_images(
        limit: int = Query(10, ge=10, le=100),
        skip: int = Query(0, ge=0),
        db: AsyncSession = Depends(get_db),
):
    """
    Show all images with query parameters.


    All depends will be later
    """
    pass


@router_images.get("/{image}", response_model=None, dependencies=None, status_code=None)
async def show_image(
        db: AsyncSession = Depends(get_db)
):
    """
    Show image by name in db or unique url ????

    All depends will be later

    """
    pass


@router_images.post("/images", response_model=None, dependencies=None, status_code=None)
async def add_image(
        operation: str = Query(None),
        db: AsyncSession = Depends(get_db)
):
    """
    Upload image, send to cloudinary, create url and other

    All depends will be later
    """
    pass


@router_images.delete("/{image}", response_model=None, dependencies=None, status_code=None)
async def delete_image(db: AsyncSession = Depends(get_db)):
    """
    Delete image from db and cloudinary.
    Must to check if admin or owner of the image

    All depends will be later
    """
    pass


@router_images.delete("/{image}", response_model=None, dependencies=None, status_code=None)
async def update_image(db: AsyncSession = Depends(get_db)):
    """
    Change image description.
    Must to check if admin, moderator or owner of the image

    All depends will be later
    """
    pass

# comments section


@router_images.post("/{image}/comment", response_model=None, dependencies=None, status_code=None)
async def add_comment(db: AsyncSession = Depends(get_db)):
    """
    Add comment to current image

    All depends will be later
    """
    pass


@router_images.put("/{image}/comment/{comment_id}", response_model=None, dependencies=None, status_code=None)
async def edit_comment(db: AsyncSession = Depends(get_db)):
    """
    Edit comment by id or another reference ???

    All depends will be later

    Check - owner|moderator|admin.
    """
    pass


@router_images.delete("/{image}/comment/{comment_id}", response_model=None, dependencies=None, status_code=None)
async def delete_comment(db: AsyncSession = Depends(get_db)):
    """
    Delete comment by id or another reference ???

    All depends will be later

    Check - owner|moderator|admin.
    """
    pass
