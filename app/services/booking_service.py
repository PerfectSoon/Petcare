from dataclasses import dataclass
from typing import List

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

from app.database.models import Booking
from app.database.types import BookingStatus
from app.repositories import BookingRepository
from app.schemas import BookingBase


@dataclass(kw_only=True, frozen=True, slots=True)
class BookingService:
    repository: BookingRepository

    async def create_booking(
        self,
        booking_data: BookingBase,
    ) -> Booking:
        try:
            booking = Booking(**booking_data.model_dump(exclude_unset=True))

            return await self.repository.create(booking)
        except IntegrityError:
            raise HTTPException(
                status_code=400,
                detail="Слот занят или услуга уже забронирована. Возможно выбранного сервиса не существует",
            )

    async def get_booking_by_id(self, booking_id: int) -> Booking | None:
        booking = await self.repository.get_by_id(booking_id)
        if not booking:
            raise HTTPException(
                status_code=400, detail="Бронирование не найдено"
            )
        return booking

    async def delete_booking(self, booking_id: int) -> None:
        booking = await self.repository.get_by_id(booking_id)
        if not booking:
            raise HTTPException(
                status_code=400, detail="Бронирование не найдено"
            )
        if booking.status == BookingStatus.completed:
            raise HTTPException(
                status_code=400,
                detail="Бронирование уже выполнено, его нельзя удалить",
            )
        await self.repository.delete(booking_id)

    async def list_of_provider_booking(self, provider_id: int) -> List[Booking]:
        return await self.repository.list(provider_id)

    async def list_of_owner_booking(self, provider_id: int) -> List[Booking]:
        return await self.repository.list(provider_id)
