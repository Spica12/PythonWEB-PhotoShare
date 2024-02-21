from fastapi import (APIRouter, Depends, File, Form, HTTPException, Path,
                     Query, UploadFile, status)
from sqlalchemy.ext.asyncio import AsyncSession

# config
from src.conf import messages
from src.dependencies.database import get_db

# models
from src.models.users import UserModel

# schemas
from src.schemas import comment
from src.schemas.photos import ImageResponseAfterCreateSchema

# services
from src.services.auth import auth_service
from src.services.cloudinary import CloudinaryService
from src.services.photos import PhotoService
from src.services.comments import CommentService
from src.services.qr import QRCodeService

router_photos = APIRouter(prefix="/photos", tags=["Photos"])

# ================================================================================================================
# photos section
# ================================================================================================================


@router_photos.get(
    "/",
    response_model=list[ImageResponseAfterCreateSchema],
    dependencies=None,
    status_code=status.HTTP_200_OK,
)
async def show_photos(
        limit: int = Query(10, ge=10, le=100),
        skip: int = Query(0, ge=0),
        db: AsyncSession = Depends(get_db)
):
    """
    Show all images with query parameters.
    Show for all users, unregistered too
    All depends will be later
    """
    photos = await PhotoService(db).get_all_photos(user, skip, limit)

    return photos


@router_photos.get("/{photo_id}", response_model=None, dependencies=None, status_code=None)
async def show_photo(
        photo_id: int,
        db: AsyncSession = Depends(get_db)
):
    """
    Show image by id
    Show for all users, unregistered too

    All depends will be later

    """
    pass


@router_photos.post(
    "/",
    response_model=ImageResponseAfterCreateSchema,
    dependencies=None,
    status_code=status.HTTP_201_CREATED,
)
async def upload_photo(
    file: UploadFile = File(),
    description: str | None = Form('', description="Add description to your photo"),
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(auth_service.get_current_user),
):
    # Upload photo and get url
    photo_cloud_url = CloudinaryService().upload_photo(file, user)
    photo = await PhotoService(db).add_photo(current_user, photo_cloud_url, description)

    return photo


@router_photos.delete("/{photo_id}", response_model=None, dependencies=None, status_code=None)
async def delete_photo(
        photo_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: UserModel = Depends(auth_service.get_current_user)
):
    """
    Delete image from db and cloudinary.
    Only for registered users

    We must to check if admin or owner of the image

    All depends will be later
    """
    pass


@router_photos.put("/{photo_id}", response_model=None, dependencies=None, status_code=None)
async def update_photo(
        photo_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: UserModel = Depends(auth_service.get_current_user)
):
    """
    Change image description.
    Only for registered users

    We must to check if admin, moderator or owner of the image

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
    Show for all users, unregistered too
    """
    # check if we have photo object in database to perform operations with comments
    exists_photo = await PhotoService(db).get_photo_exists(photo_id=photo_id)
    if not exists_photo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.PHOTO_NOT_FOUND
        )
    result = await CommentService(db).get_all_comments(photo_id=photo_id, skip=skip, limit=limit)
    return result


@router_photos.post("/{photo_id}/comments",
                    response_model=comment.CommentResponseShort,
                    dependencies=None,
                    status_code=status.HTTP_201_CREATED
                    )
async def add_comment(
        body: comment.CommentSchema,
        photo_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: UserModel = Depends(auth_service.get_current_user)
):
    """
    Add comment to current image
    Only for registered users
    """
    # check if we have photo object in database to perform operations with comments
    exists_photo = await PhotoService(db).get_photo_exists(photo_id=photo_id)
    if not exists_photo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.PHOTO_NOT_FOUND
        )
    # if photo object in database - we can add comment
    result = await CommentService(db).add_comment(photo_id=photo_id, comment=body.content, user_id=current_user.id)
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
        db: AsyncSession = Depends(get_db),
        current_user: UserModel = Depends(auth_service.get_current_user)
):
    """
    Edit comment by id
    Only for registered users.

    Check - owner|moderator|admin.
    """
    # check if we have photo object in database to perform operations with comments
    exists_photo = await PhotoService(db).get_photo_exists(photo_id=photo_id)
    if not exists_photo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.PHOTO_NOT_FOUND
        )

    # check if comment exists to perform operations on it
    exists_comment = await CommentService(db).check_exist_comment(photo_id=photo_id, comment_id=comment_id)
    if not exists_comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.COMMENT_NOT_FOUND
        )

    # Todo check admin/moderator role
    # check if comment owner or admin/moderator role
    edit_permissions = await CommentService(db).check_permissions(photo_id=photo_id, comment_id=comment_id, user_id=current_user.id)
    if not edit_permissions:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=messages.NO_EDIT_RIGHTS
        )

    result = await CommentService(db).edit_comment(photo_id=photo_id, comment_id=comment_id, comment=body.content)
    return result


@router_photos.delete("/{photo_id}/comment/{comment_id}",
                      response_model=None,
                      dependencies=None,
                      status_code=status.HTTP_204_NO_CONTENT
                      )
async def delete_comment(
        photo_id: int = Path(ge=1),
        comment_id: int = Path(ge=1),
        db: AsyncSession = Depends(get_db),
        current_user: UserModel = Depends(auth_service.get_current_user)
):
    """
    Delete comment by id

    All depends will be later
    Check - owner|moderator|admin.
    """

    # check if we have photo object in database to perform operations with comments
    exists_photo = await PhotoService(db).get_photo_exists(photo_id=photo_id)
    if not exists_photo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.PHOTO_NOT_FOUND
        )

    # check if comment exists to perform operations on it
    exists_comment = await CommentService(db).check_exist_comment(photo_id=photo_id, comment_id=comment_id)
    if not exists_comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.COMMENT_NOT_FOUND
        )

    # Todo check admin/moderator role
    # check if comment owner or admin/moderator role
    edit_permissions = await CommentService(db).check_permissions(photo_id=photo_id, comment_id=comment_id, user_id=current_user.id)
    if not edit_permissions:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=messages.NO_EDIT_RIGHTS
        )
    result = await CommentService(db).delete_comment(photo_id=photo_id, comment_id=comment_id)

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
