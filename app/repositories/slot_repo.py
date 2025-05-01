from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import AvailableSlot
from app.repositories.base_repo import AbstractRepository


class SlotRepository(AbstractRepository[AvailableSlot]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, AvailableSlot)

    async def list(self, provider_id: int) -> List[AvailableSlot]:
        result = await self.db.execute(
            select(AvailableSlot).where(
                AvailableSlot.provider_id == provider_id
            )
        )

        return list(result.scalars().all())
