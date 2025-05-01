from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.depends import get_current_active_provider
from app.database.models import Provider
from app.repositories import SlotRepository
from app.repositories import UserRepository
from app.schemas import SlotOut

from app.database.connection import get_db
from app.schemas import SlotCreate
from app.services import SlotService

router = APIRouter()


@router.post("/create", response_model=SlotOut)
async def create_slot(
    slot_in: SlotCreate,
    db: AsyncSession = Depends(get_db),
    current_provider: Provider = Depends(get_current_active_provider),
):
    service = SlotService(
        slot_repository=SlotRepository(db), user_repository=UserRepository(db)
    )

    return await service.create_slot(slot_in, current_provider.id)


@router.post("/list", response_model=List[SlotOut])
async def get_provider_slots(
    db: AsyncSession = Depends(get_db),
    current_provider: Provider = Depends(get_current_active_provider),
):
    service = SlotService(
        slot_repository=SlotRepository(db), user_repository=UserRepository(db)
    )

    return await service.get_list_slots(current_provider.id)
