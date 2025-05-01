from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.api.depends import get_current_active_owner
from app.database.models import User, Pet
from app.repositories import BookingRepository
from app.schemas import BookingCreate, BookingOut


from app.database.connection import get_db
from app.services import BookingService

router = APIRouter()


@router.post("/create", response_model=BookingOut)
async def create_booking(
    booking_in: BookingCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_owner),
):
    service = BookingService(repository=BookingRepository(db))

    pet = await db.get(Pet, booking_in.pet_id)
    if not pet or pet.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Питомец не принадлежит текущему пользователю",
        )

    return await service.create_booking(booking_in)


@router.delete("/cancel/{booking_id}")
async def cancel_booking(
    booking_id: int,
    db: AsyncSession = Depends(get_db),
):
    service = BookingService(repository=BookingRepository(db))
    await service.delete_booking(booking_id)
    return {"detail": "Бронирование отменено"}
