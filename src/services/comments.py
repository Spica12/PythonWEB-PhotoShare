from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from src.repositories.comments import CommentRepo


class CommentService:
    def __init__(self, db: AsyncSession):
        self.repo = CommentRepo(db=db)

    async def check_exist_comment(self, photo_id: int, comment_id: int):
        result = await self.repo.get_comment(photo_id, comment_id)
        return result

    # async def check_comment_owner(self, photo_id: int, comment_id: int, user_id: UUID):
    #     result = await self.repo.get_comment(photo_id, comment_id)
    #     if result.user_id != user_id:
    #         return None
    #     else:
    #         return result

    async def add_comment(self, photo_id: int, comment: str, user_id: UUID):
        result = await self.repo.add_comment(photo_id=photo_id, comment=comment, user_id=user_id)
        return result

    # async def get_all_comments(self, photo_id: int, skip: int, limit: int):
    #     result = await self.repo.get_all_comments(photo_id=photo_id, skip=skip, limit=limit)
    #     return result

    async def edit_comment(self, photo_id: int, comment_id: int, comment: str):
        result = await self.repo.edit_comment(photo_id=photo_id, comment_id=comment_id, comment=comment)
        return result

    async def delete_comment(self, photo_id: int, comment_id: int):
        await self.repo.del_comment(photo_id=photo_id, comment_id=comment_id)
