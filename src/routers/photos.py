from fastapi import (APIRouter, Depends, File, Form, HTTPException, Path,
                     Query, UploadFile, status)
from sqlalchemy.ext.asyncio import AsyncSession

from src.conf import messages
from src.dependencies.database import get_db
from src.models.users import UserModel
from src.schemas import comment
from src.schemas.photos import ImageResponseAfterCreateSchema
from src.services.auth import auth_service
from src.services.cloudinary import CloudinaryService
from src.services.comments import comment_service
from src.services.photos import PhotoService
from src.services.qr import QRCodeService

router_photos = APIRouter(prefix="/photos", tags=["Photos"])


@router_photos.get("/", response_model=None, dependencies=None, status_code=None)
async def show_photos(
        limit: int = Query(10, ge=10, le=100),
        skip: int = Query(0, ge=0),
        db: AsyncSession = Depends(get_db),
        user: UserModel = Depends(auth_service.get_current_user)
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

    # @router_photos.post("/", response_model=None, dependencies=None, status_code=None)
    # async def add_photo(
    #         image_url: str,
    #         public_id: str,
    #         unique_filename: bool = Query(False),
    #         overwrite: bool = Query(True),
    #         db: AsyncSession = Depends(get_db)
    # ):
    # try:
    # Upload an image to Cloudinary
    #     cloudinary_service.upload_photo(image_url, public_id, unique_filename, overwrite)

    #     return {"message": "Image uploaded successfully!"}
    # except Exception as e:
    #     raise HTTPException(status_code=500, detail=str(e))
    ...


@router_photos.post(
    "/",
    response_model=ImageResponseAfterCreateSchema,
    dependencies=None,
    status_code=status.HTTP_201_CREATED,
)
async def upload_photo(
    file: UploadFile = File(),
    description: str | None = Form('', description="Add description to your photo"),
    user: UserModel = Depends(auth_service.get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Upload photo and get url
    photo_cloud_url = CloudinaryService().upload_photo(file, user)
    photo = await PhotoService(db).add_photo(user, photo_cloud_url, description)

    return photo


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


# ================================================================================================================
# comments section
# ================================================================================================================


@router_photos.get("/{photo_id}/comments",
                   response_model=list[comment.CommentResponseShort],
                   dependencies=None,
                   status_code=status.HTTP_200_OK
                   )
async def show_comments(
        photo_id: int = Path(ge=1),
        limit: int = Query(10, ge=10, le=100),
        skip: int = Query(0, ge=0),
        db: AsyncSession = Depends(get_db),
):
    """
    Show all comments for specified image.
    """
    # check if we have photo object in database to perform operations with comments
    exists_photo = await comment_service.get_photo_exists(photo_id=photo_id, db=db)
    if not exists_photo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.PHOTO_NOT_FOUND
        )
    result = await comment_service.get_all_comments(photo_id=photo_id, skip=skip, limit=limit, db=db)
    return result


@router_photos.post("/{photo_id}/comments",
                    response_model=comment.CommentResponseShort,
                    dependencies=None,
                    status_code=status.HTTP_201_CREATED
                    )
async def add_comment(
        body: comment.CommentSchema,
        photo_id: int,
        db: AsyncSession = Depends(get_db)
):
    # TODO add depends for user
    """
    Add comment to current image
    All depends of user will be later
    """
    # check if we have photo object in database to perform operations with comments
    exists_photo = await comment_service.get_photo_exists(photo_id=photo_id, db=db)
    if not exists_photo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.PHOTO_NOT_FOUND
        )
    # if photo object in database - we can add comment
    # Todo replace user_id with current user
    result = await comment_service.add_comment(photo_id=photo_id, comment=body.content, user_id=1, db=db)
    return result


@router_photos.put("/{photo_id}/comment/{comment_id}",
                   response_model=None,
                   dependencies=None,
                   status_code=None
                   )
async def edit_comment(
        body: comment.CommentSchema,
        photo_id: int = Path(ge=1),
        comment_id: int = Path(ge=1),
        db: AsyncSession = Depends(get_db)
):
    """
    Edit comment by id or another reference ???

    All depends will be later

    Check - owner|moderator|admin.
    """
    # check if we have photo object in database to perform operations with comments
    exists_photo = await comment_service.get_photo_exists(photo_id=photo_id, db=db)
    if not exists_photo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.PHOTO_NOT_FOUND
        )

    # check if comment exists to perform operations on it
    exists_comment = await comment_service.check_exist_comment(photo_id=photo_id, comment_id=comment_id, db=db)
    if not exists_comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.COMMENT_NOT_FOUND
        )

    # Todo check admin/moderator role
    # check if comment owner or admin/moderator role
    edit_permissions = await comment_service.check_permissions(photo_id=photo_id, comment_id=comment_id, user_id="0a9c1d93-87dc-4511-8536-52d282218789", db=db)
    if not edit_permissions:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=messages.NO_EDIT_RIGHTS
        )

    result = await comment_service.edit_comment(photo_id=photo_id, comment_id=comment_id, comment=body.content, db=db)
    return result


@router_photos.delete("/{photo_id}/comment/{comment_id}",
                      response_model=None,
                      dependencies=None,
                      status_code=status.HTTP_204_NO_CONTENT
                      )
async def delete_comment(
        photo_id: int = Path(ge=1),
        comment_id: int = Path(ge=1),
        db: AsyncSession = Depends(get_db)
):
    """
    Delete comment by id

    All depends will be later
    Check - owner|moderator|admin.
    """

    # check if we have photo object in database to perform operations with comments
    exists_photo = await comment_service.get_photo_exists(photo_id=photo_id, db=db)
    if not exists_photo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.PHOTO_NOT_FOUND
        )

    # check if comment exists to perform operations on it
    exists_comment = await comment_service.check_exist_comment(photo_id=photo_id, comment_id=comment_id, db=db)
    if not exists_comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.COMMENT_NOT_FOUND
        )

    # Todo check admin/moderator role
    # check if comment owner or admin/moderator role
    user_id = "0a9c1d93-87dc-4511-8536-52d282218789" # test UUID, del after add users depends
    edit_permissions = await comment_service.check_permissions(photo_id=photo_id, comment_id=comment_id, user_id=user_id, db=db)
    if not edit_permissions:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=messages.NO_EDIT_RIGHTS
        )
    result = await comment_service.delete_comment(photo_id=photo_id, comment_id=comment_id, db=db)

    return result
    pass

# @router.post("/create_image_link/")
# def create_image_link(url: str, db: Session = Depends(get_db)):
#     qr_code_service = QRCodeService()

#     # Create a new image link in the database
#     new_image_link = ImageLink(url=url)
#     db.add(new_image_link)
#     db.commit()
#     db.refresh(new_image_link)

#     # Generate QR code
#     qr_image = qr_code_service.generate_qr_code(str(new_image_link.id))

#     # Save QR code to the database
#     new_image_link.qr_code = qr_image.get_image().tobytes()
#     db.commit()

#     return {"image_link_id": new_image_link.id}


# @router.get("/get_qr_code/{image_link_id}")
# def get_qr_code(image_link_id: int, db: Session = Depends(get_db)):
#     # Get QR code from the database
#     image_link = db.query(ImageLink).filter(ImageLink.id == image_link_id).first()
#     if image_link is None:
#         raise HTTPException(status_code=404, detail="Image link not found")

#     # Return QR code as a StreamingResponse
#     return StreamingResponse(io.BytesIO(image_link.qr_code), media_type="image/png")
