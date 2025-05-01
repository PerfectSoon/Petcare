from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database.models import Booking, AvailableSlot
from app.repositories.base_repo import AbstractRepository


class BookingRepository(AbstractRepository[Booking]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, Booking)

    async def list(self, provider_id: int) -> List[Booking] | None:
        result = await self.db.execute(
            select(Booking)
            .options(
                selectinload(Booking.slot).selectinload(AvailableSlot.provider)
            )
            .where(Booking.slot.has(provider_id=provider_id))
        )

        return list(result.scalars().all())
