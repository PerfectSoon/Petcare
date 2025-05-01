from dataclasses import dataclass
from typing import List, Optional

from fastapi import HTTPException

from app.database.models import AvailableSlot
from app.repositories import SlotRepository
from app.repositories import UserRepository
from app.schemas import SlotCreate, SlotOut


@dataclass(kw_only=True, frozen=True, slots=True)
class SlotService:
    slot_repository: SlotRepository
    user_repository: Optional[UserRepository] = None

    async def create_slot(
        self, slot_data: SlotCreate, provider_id: int
    ) -> SlotOut:

        user = await self.user_repository.get_by_id(provider_id)

        if not user:
            raise HTTPException(status_code=404, detail="Провайдер не найден")

        slot = AvailableSlot(**slot_data.model_dump(), provider_id=provider_id)

        return await self.slot_repository.create(slot)

    async def get_list_slots(self, provider_id) -> List[SlotOut]:
        return await self.slot_repository.list(provider_id)
