from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.dependencies.database import get_db
from src.services.cloudinary import CloudinaryService
from src.services.qr import QRCodeService

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
    return {"message": "Hello, this is your FastAPI Cloudinary integration!"}


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
        image_url: str,
        public_id: str,
        unique_filename: bool = Query(False),
        overwrite: bool = Query(True),
        db: AsyncSession = Depends(get_db)
):
    try:
        # Upload an image to Cloudinary
        cloudinary_service.upload_photo(image_url, public_id, unique_filename, overwrite)

        return {"message": "Image uploaded successfully!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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

@router.post("/create_image_link/")
def create_image_link(url: str, db: Session = Depends(get_db)):
    qr_code_service = QRCodeService()

    # Create a new image link in the database
    # new_image_link = ImageLink(url=url)
    # db.add(new_image_link)
    # db.commit()
    # db.refresh(new_image_link)

    # Generate QR code
    qr_image = qr_code_service.generate_qr_code(str(new_image_link.id))

    # Save QR code to the database
    new_image_link.qr_code = qr_image.get_image().tobytes()
    db.commit()

    return {"image_link_id": new_image_link.id}


@router.get("/get_qr_code/{image_link_id}")
def get_qr_code(image_link_id: int, db: Session = Depends(get_db)):
    # Get QR code from the database
    image_link = db.query(ImageLink).filter(ImageLink.id == image_link_id).first()
    if image_link is None:
        raise HTTPException(status_code=404, detail="Image link not found")

    # Return QR code as a StreamingResponse
    return StreamingResponse(io.BytesIO(image_link.qr_code), media_type="image/png")

