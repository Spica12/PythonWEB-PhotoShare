import logging

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from src.models.photos import CommentModel
from src.models.users import UserModel


class CommentRepo:
    def __init__(self, db):
        self.db: AsyncSession = db

    async def add_comment(self, photo_id: int, comment: str, user_id: UUID):
        new_comment = CommentModel(content=comment, photo_id=photo_id, user_id=user_id)
        self.db.add(new_comment)
        await self.db.commit()
        await self.db.refresh(new_comment)
        return new_comment

    async def get_all_comments(self, photo_id: int, skip: int, limit: int):
        # add username
        stmt = (
            select(CommentModel.id,
                   CommentModel.content,
                   CommentModel.updated_at,
                   UserModel.username)
            # .select_from(UserModel)
            .join(CommentModel)#, isouter=True)
            .filter_by(photo_id=photo_id)
            .group_by(CommentModel.id,
                      UserModel.username,
                      CommentModel.content,
                      CommentModel.updated_at,
                      )
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return result.fetchall()

    async def get_comment(self,  photo_id: int, comment_id: int):
        # to check if object exists before edit or delete
        stmt = select(CommentModel).filter(
            and_(CommentModel.id == comment_id, CommentModel.photo_id == photo_id)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def del_comment(self, photo_id: int, comment_id: int):
        stmt = select(CommentModel).filter(
            and_(CommentModel.id == comment_id, CommentModel.photo_id == photo_id)
        )
        result = await self.db.execute(stmt)
        result = result.scalar_one_or_none()
        if result:
            await self.db.delete(result)
            await self.db.commit()

    async def edit_comment(self, photo_id: int, comment_id: int, comment: str):
        stmt = select(CommentModel).filter(
            and_(CommentModel.id == comment_id, CommentModel.photo_id == photo_id)
        )
        result = await self.db.execute(stmt)
        result = result.scalar_one_or_none()
        if result:
            result.content = comment
            await self.db.commit()
            await self.db.refresh(result)
        return result
