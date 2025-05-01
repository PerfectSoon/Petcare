from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database.models import Pet
from app.repositories.base_repo import AbstractRepository


class PetRepository(AbstractRepository[Pet]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, Pet)

    async def get_by_id(self, pet_id: int) -> Pet | None:
        result = await self.db.execute(
            select(Pet)
            .options(selectinload(Pet.medical_records))
            .where(Pet.id == pet_id)
        )

        return result.scalar_one_or_none()

    async def list(self, owner_id: int) -> List[Pet] | None:
        result = await self.db.execute(
            select(Pet)
            .where(Pet.owner_id == owner_id)
        )

        return list(result.scalars().all())
