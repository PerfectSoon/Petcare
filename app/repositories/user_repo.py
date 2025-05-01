from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database.models import User, Provider
from app.repositories.base_repo import AbstractRepository


class UserRepository(AbstractRepository[User]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, User)

    async def get_by_email(self, email: str) -> User | None:
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_by_id(self, id: int) -> User | None:
        result = await self.db.execute(
            select(User)
            .where(User.id == id)
            .options(selectinload(User.provider).selectinload(Provider.documents), selectinload(User.owner))
        )
        return result.unique().scalar_one_or_none()
