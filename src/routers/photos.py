from copy import deepcopy
from typing import Annotated, List

from fastapi import (APIRouter, Depends, HTTPException, Path, Query, Request,
                     status)
from fastapi.responses import RedirectResponse, StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

# config
from src.conf import messages
from src.dependencies.database import get_db
# models
from src.models.users import Roles, UserModel
# schemas
from src.schemas import comment, rating
from src.schemas.comment import CommentResponseShort
from src.schemas.photos import (ImageResponseAfterCreateSchema,
                                ImageResponseAfterUpdateSchema, ImageSchema)
from src.schemas.transform import TransformRequestSchema
from src.schemas.unified import (ImagePageResponseFullSchema,
                                 ImagePageResponseShortSchema,
                                 ShowAllRateSchema)
# services
from src.services.auth import auth_service
from src.services.cloudinary import CloudinaryService
from src.services.comments import CommentService
from src.services.photos import PhotoService
from src.services.qr import QRCodeService
from src.services.rating import RatingService
from src.services.roles import RoleChecker
from src.services.tags import TagService

# routers
router_photos = APIRouter(prefix="/photos", tags=["Photos"])


@router_photos.get(
    "/",
    response_model=list[ImagePageResponseShortSchema],
    dependencies=None,
    status_code=status.HTTP_200_OK,
)
async def show_photos(
    limit: Annotated[int, Query(description="Limit photos per page", ge=4, le=20)] = 4,
    skip: Annotated[int, Query(description="Skip number of photos", ge=0)] = 0,
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
    photos = await PhotoService(db).get_all_photo_per_page(skip=skip, limit=limit)
    return photos


@router_photos.get(
    "/{photo_id}",
    response_model=ImagePageResponseFullSchema,
    dependencies=None,
    status_code=status.HTTP_200_OK,
)
async def show_photo(
    photo_id: Annotated[int, Path(title="Photo ID", ge=1)],
    limit: Annotated[
        int, Query(description="Limit comments per page", ge=1, le=50)
    ] = 20,
    skip: Annotated[int, Query(description="Skip comments for next page", ge=0)] = 0,
    db: AsyncSession = Depends(get_db),
):
    """
    Show photo by id with comments if it is.
    Limit and skip in query parameters is for comments pagination.

    Additional undocumented functionality: if limit = 1,
    skip shows specific comment. (do not use as hardcoded url for comment)

    Show for all users, unregistered too
    """
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
    body: ImageSchema = Depends(),
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(auth_service.get_current_user),
):
    """
    Upload photos. Description and tags are optional.
    Only 5 tags accepted with ,(coma) separator.

    Only for registered users.
    """

    # Validate photo
    await PhotoService(db).validate_photo(body.file)

    # Normalize tags
    if body.tags:
        body.tags = await TagService(db).normalize_list_of_tag(body.tags)
        if len(body.tags) > 5:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=messages.TOO_MANY_TAGS
            )
        for tag in body.tags:
            if len(tag) > 20:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail=messages.MAX_LEN_TAG
                    )
    else:
        body.tags = []

    # Upload photo and get url
    photo_cloud_url, public_id = CloudinaryService().upload_photo(
        body.file, current_user
    )
    # Add new_photo to db
    # Without deepcopy(or copy), new_photo isn't returned. I don't know why.
    new_photo = deepcopy(
        await PhotoService(db).add_photo(
            current_user, public_id, photo_cloud_url, body.description
        )
    )
    if body.tags:
        await TagService(db).add_tags_to_photo(new_photo.id, body.tags)
    return new_photo


@router_photos.post(
    "/{photo_id}",
    response_model=comment.CommentResponseShort,
    dependencies=None,
    status_code=status.HTTP_201_CREATED,
)
async def add_comment(
    photo_id: Annotated[int, Path(description="Photo ID", ge=1)],
    body: comment.CommentSchema,
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


@router_photos.post(
    "/{photo_id}/set-rate",
    response_model=rating.RateResponseSchema,
    dependencies=None,
    status_code=status.HTTP_201_CREATED,
)
async def add_rate(
    photo_id: Annotated[int, Path(description="Photo ID", ge=1)],
    body: rating.SetRateSchema,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(auth_service.get_current_user),
):
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


@router_photos.delete(
    "/{photo_id}",
    response_model=None,
    dependencies=None,
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_photo_comment(
    photo_id: Annotated[int, Path(title="Photo ID", ge=1)],
    select: Annotated[
        str | None, Query(description="Choose object", enum=["transform", "comment"])
    ] = None,
    object_id: Annotated[int, Query(description="Choose object ID", ge=1)] = None,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(auth_service.get_current_user),
):
    """
    Delete
    image from db and cloudinary
    or
    Photo transformation with selected id for selected photo_id
    or
    Comment with selected id for selected photo_id

    Only for registered users.
    Operation for owners, moderators and admins.
    """
    photo = await PhotoService(db).get_photo_exists(photo_id)
    # if del photo
    if photo is None:
        # if no object to work with
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.PHOTO_NOT_FOUND
        )

    admin_moderator_check = await RoleChecker(
            [Roles.admin, Roles.moderator]
        ).check_admin_or_moderator(user_id=current_user.id, db=db)

    # choose what to delete: photo or photo transformation or comment
    if not select or select == "transform":
        # # check if we are owner or admin/moderator
        if (photo.user_id == current_user.id) or admin_moderator_check is not None:
            # if owner or admin - we can delete photo or one of transformation
            if not select:
                # delete photo
                try:
                    result = CloudinaryService().destroy_photo(public_id=photo.public_id)
                    if result["result"] == "ok":
                        await PhotoService(db).delete_photo(photo)
                    elif result["result"] == "not found":
                        raise HTTPException(
                            status_code=status.HTTP_404_NOT_FOUND,
                            detail=messages.PHOTO_NOT_FOUND,
                        )
                except AttributeError:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND, detail=messages.PHOTO_NOT_FOUND
                    )
            elif select == "transform":
                # delete transformation by id no checks because no errors if not exists
                await PhotoService(db).delete_transformed_photo(photo_id, object_id)
        else:
            # Goodbye if not
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail=messages.NO_EDIT_RIGHTS
            )

    elif select == "comment":
        # check if current user == owner of comment
        exists_comment = await CommentService(db).check_exist_comment(
            photo_id=photo_id, comment_id=object_id
        )
        if not exists_comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=messages.COMMENT_NOT_FOUND
            )
            # check if we are  admin/moderator
        if admin_moderator_check is not None:
            # perform operation on comment if all checks are pass successfully
            await CommentService(db).delete_comment(
                photo_id=photo_id, comment_id=object_id
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail=messages.NO_EDIT_RIGHTS
            )


@router_photos.get(
    "/{photo_id}/transform",
    response_model=None,
    dependencies=None,
    status_code=status.HTTP_200_OK,
)
async def get_transformed_photos(
    photo_id: Annotated[int, Path(title="Photo ID", ge=1)],
    select: Annotated[
        str | None, Query(description="Choose action", enum=["url", "qrcode"])
    ] = None,
    object_id: Annotated[int, Query(description="Choose object ID", ge=1)] = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Get List of photo transformations with default query

    For all users, unregistered too.

    Get url
    or show photo by url from qrcode (generated in post method)
    for transformation with object_id for photo with photo_id

    """
    # check if photo object exists to work with it
    photo = await PhotoService(db).get_photo_exists(photo_id)
    if not photo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.PHOTO_NOT_FOUND
        )

    # get all variants of transformations for current photo
    if select is None:
        # show list of transformed variants for current photo.
        # Empty list if we have no transformations
        transformed_photos = await PhotoService(db).get_transformed_photos_by_photo_id(
            photo_id
        )
        return transformed_photos

    elif select and object_id:
        transformed_photo = await PhotoService(
            db
        ).get_transformed_photo_by_transformed_id(photo_id, object_id)
        # get transformed photo by photo_id and transformed photo id
        # exception if there are no transformation
        if not transformed_photo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=messages.TRANSFORMED_PHOTOS_NOT_FOUND,
            )

        if select == "url":
            # show url for transformation of photo by photo_id and transformed photo id
            return {"transformed_photo_url": transformed_photo.image_url}

        elif select == "qrcode":
            # show qrcode for transformation of photo by photo_id and transformed photo id
            response = RedirectResponse(url=transformed_photo.image_url)
            return response

        else:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=messages.UNKNOWN_PARAMETER,
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=messages.UNKNOWN_PARAMETER,
        )


@router_photos.post(
    "/{photo_id}/transform",
    response_model=None,
    dependencies=None,
    status_code=status.HTTP_201_CREATED,
)
async def transform_photo(
    photo_id: Annotated[int, Path(title="Photo ID", ge=1)],
    transformation: TransformRequestSchema,
    request: Request,
    select: Annotated[
        str, Query(description="Choose action", enum=["create", "qrcode"])
    ] = "create",
    object_id: Annotated[int, Query(description="Choose object ID", ge=1)] = None,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(auth_service.get_current_user),
):
    """
    Crate photo transformation for current photo or
    Generate qr code for photo transformation

    """
    photo = await PhotoService(db).get_photo_exists(photo_id)
    if not photo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.PHOTO_NOT_FOUND
        )

    # create transformation only for photo owner
    if select == "create" and photo.user_id == current_user.id:
        # make transformation with current photo
        try:
            transform_photo_url = CloudinaryService().get_transformed_photo_url(
                public_id=photo.public_id,
                request_for_transformation=transformation.model_dump(),
            )
            # save transformation url
            new_transformed_photo = await PhotoService(db).add_transformed_photo_to_db(
                photo.id, transform_photo_url
            )
            return {"transformed_photo_url": new_transformed_photo.image_url}
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=messages.UNKNOWN_PARAMETER,
            )
    # but qr code can generate every one
    elif select == "qrcode" and object_id is not None:
        # create qr by transformation photo id
        transform_photo = await PhotoService(
            db
        ).get_transformed_photo_by_transformed_id(photo_id, object_id)
        if not transform_photo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=messages.TRANSFORMED_PHOTOS_NOT_FOUND,
            )
        transform_photo_url = \
            f"{str(request.base_url)}api/photos/{photo_id}/transform/?select=qrcode&object_id={object_id}"

        transformed_qr_code = QRCodeService().generate_qr_code(transform_photo_url)
        # Show qrcode in Swagger
        return StreamingResponse(transformed_qr_code, media_type="image/jpeg")
    else:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=messages.UNKNOWN_PARAMETER,
        )


@router_photos.put(
    "/{photo_id}",
    response_model=ImageResponseAfterUpdateSchema | CommentResponseShort,
    dependencies=None,
    status_code=status.HTTP_200_OK,
)
async def update_photo(
    photo_id: Annotated[int, Path(description="Photo ID", ge=1)],
    content: Annotated[str, Query(description="Content to change", min_length=3)],
    select: Annotated[
        str, Query(description="Choose action", enum=["photo", "comment"])
    ] = "photo",
    object_id: Annotated[int, Query(description="Choose object ID", ge=1)] = None,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(auth_service.get_current_user),
):
    """
    Change photo description.

    Only for registered users.
    Add - check if admin|moderator|owner
    """
    photo = await PhotoService(db).get_photo_exists(photo_id)
    # if no photo exists - nothing to edit
    if not photo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.PHOTO_NOT_FOUND
        )
    # Get user role
    admin_moderator_check = await RoleChecker(
        [Roles.admin, Roles.moderator]
    ).check_admin_or_moderator(user_id=current_user.id, db=db)

    if select == "photo":
        # photo owner or admin/moderator check
        if photo.user_id == current_user.id or admin_moderator_check is not None:
            photo.description = content
            edited_photo = await PhotoService(db).update_photo(photo)
            return edited_photo
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail=messages.NO_EDIT_RIGHTS
            )

    elif select == "comment":
        # check if comment exists to perform operations on it
        exists_comment = await CommentService(db).check_exist_comment(
            photo_id=photo_id, comment_id=object_id
        )

        if not exists_comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=messages.COMMENT_NOT_FOUND
            )

        # check if we are comment owner or admin/moderator
        if exists_comment.user_id == current_user.id or admin_moderator_check is not None:
            # perform operation on comment if all checks are pass successfully
            result = await CommentService(db).edit_comment(
                photo_id=photo_id, comment_id=object_id, comment=content
            )
            return result
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail=messages.NO_EDIT_RIGHTS
            )


@router_photos.get(
    "/{photo_id}/rating",
    response_model=List[ShowAllRateSchema],
    dependencies=[Depends(RoleChecker([Roles.admin, Roles.moderator]))],
    status_code=status.HTTP_200_OK,
)
async def show_rates(
    photo_id: int = Path(ge=1),
    db: AsyncSession = Depends(get_db),
):
    """
    Show all rates for current image

    Only for admin and moderators.
    To see what rate and who was set it.
    """
    # check if we have photo object in database to perform operations with comments
    exists_photo = await PhotoService(db).get_photo_exists(photo_id=photo_id)
    if not exists_photo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.PHOTO_NOT_FOUND
        )

    result = await RatingService(db).get_rates(photo_id=photo_id)
    return result


@router_photos.delete(
    "/{photo_id}/rating/{username}",
    response_model=None,
    dependencies=[Depends(RoleChecker([Roles.admin, Roles.moderator]))],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_rate(
    photo_id: Annotated[int, Path(description="Photo ID", ge=1)],
    username: Annotated[str, Path(description="Username", min_length=2, max_length=50)],
    db: AsyncSession = Depends(get_db),
):
    """
    Delete rate for photo with photo_id
    and user with username

    Only for admins and moderators
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
