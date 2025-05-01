from typing import Optional
from pydantic import BaseModel

from app.schemas.pet import PetOut
from app.schemas.service import ServiceBase
from app.schemas.slot import SlotOut


class BookingBase(BaseModel):
    pet_id: int
    slot_id: int
    service_id: int
    notes: Optional[str] = None


class BookingCreate(BookingBase):
    pass


class BookingOut(BookingBase):
    id: int

    pet: PetOut
    slot: SlotOut
    service: ServiceBase

    class Config:
        from_attributes = True
