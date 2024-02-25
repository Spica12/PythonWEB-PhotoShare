from copy import copy, deepcopy
from fastapi import (
    APIRouter, Depends, HTTPException, Path, Query, Request, status,
    File, Form, UploadFile
)
from fastapi.responses import RedirectResponse, StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from typing import List, Union
from src.services.tags import TagService


# config
from src.conf import messages
from src.dependencies.database import get_db

# models
from src.models.users import UserModel
from src.models.users import Roles

# schemas
from src.schemas import comment
from src.schemas import rating
from src.schemas.photos import ImageResponseAfterCreateSchema, ImageSchema
from src.schemas.transform import TransformRequestSchema
from src.schemas.unified import ImagePageResponseShortSchema, ImagePageResponseFullSchema

# services
from src.services.auth import auth_service
from src.services.cloudinary import CloudinaryService
from src.services.photos import PhotoService
from src.services.comments import CommentService
from src.services.rating import RatingService
from src.services.roles import RoleChecker
from src.services.qr import QRCodeService

# routers
router_photos = APIRouter(prefix="/photos", tags=["Photos"])

# TODO remove in release
from typing import Union
# deprecated routers.
router_deprecated = APIRouter(prefix="/photos", tags=["DEPRECATED"])

# ================================================================================================================
# photos section
# ================================================================================================================


@router_photos.get(
    "/",
    response_model=list[ImagePageResponseShortSchema],
    dependencies=None,
    status_code=status.HTTP_200_OK
)
async def show_photos(
    limit: int = Query(10, ge=10, le=100),
    skip: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """
    Show all photos. Pagination in query parameters:
        limit = limit photos per page
        skip = skip images from previous pages.
            Example: when limit = 10 photos per page,
            for the 3d page skip = 20.

    Show for all users, unregistered too
    """
    # todo rebase rate with AVG !
    #  add tags
    photos = await PhotoService(db).get_all_photo_per_page(skip=skip, limit=limit)
    return photos


@router_photos.get(
    "/{photo_id}",
    response_model=ImagePageResponseFullSchema,
    dependencies=None,
    status_code=status.HTTP_200_OK,
)
async def show_photo(
        photo_id: int,
        limit: int = Query(20, ge=10, le=100),
        skip: int = Query(0, ge=0),
        db: AsyncSession = Depends(get_db)
):
    """
    Show photo by id
    Pagination in query parameters for comments.

    Show for all users, unregistered too
    """
    # todo rebase rate with AVG !
    #  add tags
    #   add to comments: update_user
    #   rebese comments created with updated
    photo = await PhotoService(db).get_one_photo_page(photo_id, skip, limit)
    if not photo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.PHOTO_NOT_FOUND
        )
    return photo


@router_photos.post(
    "/",
    response_model=ImageResponseAfterCreateSchema,
    dependencies=None,
    status_code=status.HTTP_201_CREATED,
)
async def upload_photo(
    # file: UploadFile = File(),                                                                  # todo add to body schema
    # description: str | None = Form("", description="Add description to your photo"),     # todo add to body schema
    body: ImageSchema = Depends(),
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(auth_service.get_current_user),
):
    if body.tags:
        list_tags = body.tags.split(",")
        body.tags = [tag.strip() for tag in list_tags]
        if len(body.tags) > 5:
            raise HTTPException(
               status_code=status.HTTP_400_BAD_REQUEST, detail=messages.TOO_MANY_TAGS
            )
    else:
        body.tags = []

    # Upload photo and get url
    photo_cloud_url, public_id = CloudinaryService().upload_photo(body.file, current_user)
    # Add new_photo to db
    # Without this, new_photo isn't returned. I don't know why.
    new_photo = deepcopy(await PhotoService(db).add_photo(
       current_user,
       public_id,
       photo_cloud_url,
       body.description
    ))
    if body.tags:
        await TagService(db).add_tags_to_photo(new_photo.id, body.tags)
    return new_photo
#    new_photo_copy = copy(new_photo)
#    # If we have tags then we need to add them
#    if body.tags:
#        await TagService(db).add_tags_to_photo(new_photo_copy.id, body.tags)
#
#    return new_photo_copy


@router_photos.delete(
    "/{photo_id}",
    response_model=None,
    dependencies=None,
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_photo(
    photo_id: int,
    transform_id: int = Query( default=None, qe=1),
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(auth_service.get_current_user),
):
    """
    Delete image from db and cloudinary.
    Only for registered users

    We must to check if admin or owner of the image

    All depends will be later
    """
    photo = await PhotoService(db).get_photo_exists(photo_id)
    if not photo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.PHOTO_NOT_FOUND
        )

    # Get user role
    admin_moderator_check = await RoleChecker(
        [Roles.admin, Roles.moderator]
    ).check_admin_or_moderator(user_id=current_user.id, db=db)
    # check owner and moderator|admin
    if (photo.user_id != current_user.id) and admin_moderator_check is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=messages.NO_EDIT_RIGHTS
        )

    if not transform_id:
        result = CloudinaryService().destroy_photo(public_id=photo.public_id)
        if result["result"] == "ok":
            await PhotoService(db).delete_photo(photo)
        elif result["result"] == "not found":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=messages.PHOTO_NOT_FOUND
            )
    else:
        result = await PhotoService(db).delete_transformed_photo(photo_id, transform_id)
        return result


@router_photos.get(
    "/{photo_id}/transform",
    response_model=None,
    dependencies=None,
    status_code=status.HTTP_200_OK,
)
async def get_transformed_photos(
    photo_id: int,
    transform_id: int | None = Query(default=None, ge=1),     # if None - show all transformations
    qr_code: bool = Query(default=False),                       # Show qr code for current transformation
    db: AsyncSession = Depends(get_db),
):
    # check if photo object exists to work with it
    photo = await PhotoService(db).get_photo_exists(photo_id)
    if not photo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.PHOTO_NOT_FOUND
        )
    # if we want to show all variants of transformations for current photo
    if transform_id is None:
        # show list of transformed variants for current photo.
        # TODO
        transformed_photos = await PhotoService(db).get_transformed_photos_by_photo_id(photo_id)
        if not transformed_photos:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=messages.TRANSFORMED_PHOTOS_NOT_FOUND,
            )
        return transformed_photos

    else:
        transformed_photo = await PhotoService(db).get_transformed_photo_by_transformed_id(photo_id, transform_id)
        if not transformed_photo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=messages.TRANSFORMED_PHOTOS_NOT_FOUND,
            )

        if not qr_code:
            return {"transformed_photo_url": transformed_photo.image_url}
        else:
            response = RedirectResponse(url=transform_photo.image_url)
            return response



@router_photos.post(
    "/{photo_id}/transform",
    response_model=None,
    dependencies=None,
    status_code=status.HTTP_201_CREATED,
)
async def transform_photo(
    photo_id: int,
    transformation: TransformRequestSchema,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(auth_service.get_current_user),
):
    # Need to choose delete this route or not
    photo = await PhotoService(db).get_photo_exists(photo_id)
    if not photo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.PHOTO_NOT_FOUND
        )

    transform_photo_url = CloudinaryService().get_transformed_photo_url(
        public_id=photo.public_id,
        request_for_transformation=transformation.model_dump(),
    )

    new_transformered_photo = await PhotoService(db).add_transformed_photo_to_db(
        photo.id, transform_photo_url
    )

    return {"transformed_photo_url": new_transformered_photo.image_url}


"""
            # Need to choose delete this route or not
            transform_photo_url = CloudinaryService().get_transformed_photo_url(
                public_id=photo.public_id, transformation=transformation.model_dump()
            )
            new_transformed_photo = await PhotoService(db).add_transformed_photo_to_db(
                photo.id, transform_photo_url
            )
            return {"transformed_photo_url": new_transformed_photo.image_url}
"""


# ================================================================================================================
# end of photos section
# ================================================================================================================


@router_photos.put(
    "/{photo_id}",
    response_model=ImageResponseAfterCreateSchema,
    dependencies=None,
    status_code=status.HTTP_200_OK,
)
async def update_photo(
    photo_id: int,
    description: str,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(auth_service.get_current_user),
):
    """
    Change image description.
    Only for registered users

    We must to check if admin, moderator or owner of the image

    All depends will be later
    """
    photo = await PhotoService(db).get_photo_exists(photo_id)
    if not photo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.PHOTO_NOT_FOUND
        )

    # Get user role
    admin_moderator_check = await RoleChecker(
        [Roles.admin, Roles.moderator]
    ).check_admin_or_moderator(user_id=current_user.id, db=db)
    # check owner and moderator|admin
    if (photo.user_id != current_user.id) and admin_moderator_check is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=messages.NO_EDIT_RIGHTS
        )

    photo.description = description
    edited_photo = await PhotoService(db).update_photo(photo)

    return edited_photo


# ================================================================================================================
# TODO REMOVE EVERYTHING BELOW THIS TEXT
#  DEPRECATED
# somebody can try single methods
# ================================================================================================================


@router_deprecated.post(
    "/{photo_id}/transformed/{transform_id}/qrcode",
    response_model=None,
    dependencies=None,
    status_code=status.HTTP_200_OK,
)
async def create_qr_code_for_transformed_photo(
    photo_id: int,
    transform_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(auth_service.get_current_user),
):
    photo = await PhotoService(db).get_photo_exists(photo_id)
    if not photo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.PHOTO_NOT_FOUND
        )
    transform_photo = await PhotoService(db).get_transformed_photo_by_transformed_id(
        photo_id, transform_id
    )
    if not transform_photo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=messages.TRANSFORMED_PHOTOS_NOT_FOUND,
        )
    transform_photo_url = f"{str(request.base_url)}api/photos/{photo_id}/transformed/{transform_id}/qrcode"

    transformed_qr_code = QRCodeService().generate_qr_code(transform_photo_url)

    # For Swagger
    return StreamingResponse(transformed_qr_code, media_type="image/jpeg")

"""

transform_photo = await PhotoService(db).get_transformed_photo_by_transformed_id(photo_id, transform_id)
            if not transform_photo:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=messages.TRANSFORMED_PHOTOS_NOT_FOUND,
                )
            # TODO rewrite URL with valid query parameters
            transform_photo_url = f"{str(request.base_url)}api/photos/{photo_id}/transformed/{transform_id}/qrcode"

            transformed_qr_code = QRCodeService().generate_qr_code(transform_photo_url)

            # For Swagger
            return StreamingResponse(transformed_qr_code, media_type="image/jpeg")

"""


@router_deprecated.get(
    "/{photo_id}/transformed/{transform_id}/url",
    response_model=None,
    dependencies=None,
    status_code=status.HTTP_200_OK,
)
async def get_transformed_photo(
    photo_id: int,
    transform_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(auth_service.get_current_user),
):
    photo = await PhotoService(db).get_photo_exists(photo_id)
    if not photo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.PHOTO_NOT_FOUND
        )

    transform_photo = await PhotoService(db).get_transformed_photo_by_transformed_id(
        photo_id, transform_id
    )
    if not transform_photo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=messages.TRANSFORMED_PHOTOS_NOT_FOUND,
        )

    return {
        "transformed_photo_url": transform_photo.image_url,
    }


@router_deprecated.get(
    "/{photo_id}/transformed/{transform_id}/qrcode",
    response_model=None,
    dependencies=None,
    status_code=status.HTTP_200_OK,
)
async def get_transformed_photo(
    photo_id: int,
    transform_id: int,
    db: AsyncSession = Depends(get_db),
    # current_user: UserModel = Depends(auth_service.get_current_user),
):
    photo = await PhotoService(db).get_photo_exists(photo_id)
    if not photo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.PHOTO_NOT_FOUND
        )
    transform_photo = await PhotoService(db).get_transformed_photo_by_transformed_id(
        photo_id, transform_id
    )
    if not transform_photo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=messages.TRANSFORMED_PHOTOS_NOT_FOUND,
        )

    response = RedirectResponse(url=transform_photo.image_url)

    return response

@router_deprecated.get(
    "/{photo_id}/comments",
    response_model=list[comment.CommentResponseShort],
    dependencies=None,
    status_code=status.HTTP_200_OK,
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
    result = await CommentService(db).get_all_comments(
        photo_id=photo_id, skip=skip, limit=limit
    )
    return result


@router_deprecated.post(
    "/{photo_id}/comments",
    response_model=comment.CommentResponseShort,
    dependencies=None,
    status_code=status.HTTP_201_CREATED,
)
async def add_comment(
    body: comment.CommentSchema,
    photo_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(auth_service.get_current_user),
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
    result = await CommentService(db).add_comment(
        photo_id=photo_id, comment=body.content, user_id=current_user.id
    )
    return result


@router_deprecated.put(
    "/{photo_id}/comment/{comment_id}",
    response_model=None,
    dependencies=None,
    status_code=None,
)
async def edit_comment(
    body: comment.CommentSchema,
    photo_id: int = Path(ge=1),
    comment_id: int = Path(ge=1),
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(auth_service.get_current_user),
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
    exists_comment = await CommentService(db).check_exist_comment(
        photo_id=photo_id, comment_id=comment_id
    )
    if not exists_comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.COMMENT_NOT_FOUND
        )

    # check owner and moderator|admin
    comment_owner = await CommentService(db).check_comment_owner(
        photo_id=photo_id, comment_id=comment_id, user_id=current_user.id
    )
    admin_moderator_check = await RoleChecker(
        [Roles.admin, Roles.moderator]
    ).check_admin_or_moderator(user_id=current_user.id, db=db)
    if not comment_owner and admin_moderator_check is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=messages.NO_EDIT_RIGHTS
        )

    # perform operation on comment if all checks are passe successfully
    result = await CommentService(db).edit_comment(
        photo_id=photo_id, comment_id=comment_id, comment=body.content
    )
    return result


@router_deprecated.delete(
    "/{photo_id}/comment/{comment_id}",
    response_model=None,
    dependencies=[Depends(RoleChecker([Roles.admin, Roles.moderator]))],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_comment(
    photo_id: int = Path(ge=1),
    comment_id: int = Path(ge=1),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete comment by id
    Route can be access only for admin (or moderator ?)
    """

    # check if we have photo object in database to perform operations with comments
    exists_photo = await PhotoService(db).get_photo_exists(photo_id=photo_id)
    if not exists_photo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.PHOTO_NOT_FOUND
        )

    # check if comment exists to perform operations on it
    exists_comment = await CommentService(db).check_exist_comment(
        photo_id=photo_id, comment_id=comment_id
    )
    if not exists_comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.COMMENT_NOT_FOUND
        )

    result = await CommentService(db).delete_comment(
        photo_id=photo_id, comment_id=comment_id
    )
    return result


# ================================================================================================================
# comments section
# ================================================================================================================


@router_deprecated.post(
    "/{photo_id}/rating",
    response_model=rating.RateResponseSchema,
    dependencies=None,
    status_code=status.HTTP_201_CREATED,
)
async def add_rate(
    body: rating.SetRateSchema,
    photo_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(auth_service.get_current_user),
):
    """
    TESTING ROUTE

    Add rating to the image

    Temporary rote for testing functionality
    """
    # check if we have photo object in database to perform operations with comments
    exists_photo = await PhotoService(db).get_photo_exists(photo_id=photo_id)
    if not exists_photo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.PHOTO_NOT_FOUND
        )

    result = await RatingService(db).set_rate(
        photo_id=photo_id, rate=body.value, user_id=current_user.id
    )

    # if return None - rate was already set
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=messages.ALREADY_SET
        )

    return result


@router_deprecated.delete(
    "/{photo_id}/rating/{username}",
    response_model=None,
    dependencies=[Depends(RoleChecker([Roles.admin, Roles.moderator]))],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_rate(
    photo_id: int = Path(ge=1), username: str = "", db: AsyncSession = Depends(get_db)
):
    """
    TESTING ROUTE

    Delete rate

    Temporary rote for testing functionality
    """

    # check if we have photo object in database to perform operations with comments
    exists_photo = await PhotoService(db).get_photo_exists(photo_id=photo_id)
    if not exists_photo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.PHOTO_NOT_FOUND
        )

    result = await RatingService(db).delete_rate(photo_id=photo_id, username=username)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.RATING_NOT_SET
        )
    return result


@router_deprecated.get(
    "/{photo_id}/rating",
    response_model=None,
    dependencies=None,
    status_code=status.HTTP_200_OK,
)
async def show_rates(
    photo_id: int = Path(ge=1),
    db: AsyncSession = Depends(get_db),
):
    """
    TESTING ROUTE

    View avg rate for photo with photo_is

    Temporary rote for testing functionality
    """
    # check if we have photo object in database to perform operations with comments
    exists_photo = await PhotoService(db).get_photo_exists(photo_id=photo_id)
    if not exists_photo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.PHOTO_NOT_FOUND
        )

    result = await RatingService(db).get_avg_rate(photo_id=photo_id)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Test")

    return result


# @router_photos.post("/create_image_link/")
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


# @router_photos.get("/get_qr_code/{image_link_id}")
# def get_qr_code(image_link_id: int, db: Session = Depends(get_db)):
#     # Get QR code from the database
#     image_link = db.query(ImageLink).filter(ImageLink.id == image_link_id).first()
#     if image_link is None:
#         raise HTTPException(status_code=404, detail="Image link not found")

#     # Return QR code as a StreamingResponse
#     return StreamingResponse(io.BytesIO(image_link.qr_code), media_type="image/png")
