from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.dependencies.database import get_db

router_photos = APIRouter(prefix="/photos", tags=["Photos"])


@router_photos.get("/", response_model=None, dependencies=None, status_code=None)
async def show_photos(
        limit: int = Query(10, ge=10, le=100),
        skip: int = Query(0, ge=0),
        db: AsyncSession = Depends(get_db),
):
    """
    Show all images with query parameters.


    All depends will be later
    """
    pass


@router_photos.get("/{photo_id}", response_model=None, dependencies=None, status_code=None)
async def show_photo(
        photo_id: int,
        db: AsyncSession = Depends(get_db)
):
    """
    Show image by id

    All depends will be later

    """
    pass


@router_photos.post("/", response_model=None, dependencies=None, status_code=None)
async def add_photo(
        operation: str = Query(None),
        db: AsyncSession = Depends(get_db)
):
    """
    Upload image, send to cloudinary, create url and other

    All depends will be later
    """
    pass


@router_photos.delete("/{photo_id}", response_model=None, dependencies=None, status_code=None)
async def delete_photo(
        photo_id: int,
        db: AsyncSession = Depends(get_db)
):
    """
    Delete image from db and cloudinary.
    Must to check if admin or owner of the image

    All depends will be later
    """
    pass


@router_photos.put("/{photo_id}", response_model=None, dependencies=None, status_code=None)
async def update_photo(
        photo_id: int,
        db: AsyncSession = Depends(get_db)
):
    """
    Change image description.
    Must to check if admin, moderator or owner of the image

    All depends will be later
    """
    pass

# comments section


@router_photos.post("/{photo_id}/comment", response_model=None, dependencies=None, status_code=None)
async def add_comment(
        photo_id: int,
        db: AsyncSession = Depends(get_db)
):
    """
    Add comment to current image

    All depends will be later
    """
    pass


@router_photos.put("/{photo_id}/comment/{comment_id}", response_model=None, dependencies=None, status_code=None)
async def edit_comment(
        photo_id: int,
        comment_id: int,
        db: AsyncSession = Depends(get_db)
):
    """
    Edit comment by id or another reference ???

    All depends will be later

    Check - owner|moderator|admin.
    """
    pass


@router_photos.delete("/{photo_id}/comment/{comment_id}", response_model=None, dependencies=None, status_code=None)
async def delete_comment(
        photo_id: int,
        comment_id: int,
        db: AsyncSession = Depends(get_db)
):
    """
    Delete comment by id or another reference ???

    All depends will be later

    Check - owner|moderator|admin.
    """
    pass
