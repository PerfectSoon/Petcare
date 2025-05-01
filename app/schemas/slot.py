from pydantic import BaseModel
from datetime import date, time

from app.schemas.user import ProviderOut


class SlotBase(BaseModel):
    date: date
    start_time: time
    end_time: time
    is_available: bool


class SlotCreate(SlotBase):
    pass


class SlotOut(SlotBase):
    id: int

    provider: ProviderOut

    class Config:
        from_attributes = True
