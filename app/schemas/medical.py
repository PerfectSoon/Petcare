from typing import Optional
from pydantic import BaseModel, Field
from app.database.types import RecordType


class MedicalRecordBase(BaseModel):
    record_type: RecordType
    description: Optional[str] = Field(default=None, max_length=400)
    document_url: Optional[str] = Field(default=None, max_length=200)

    class Config:
        from_attributes = True


class MedicalRecordOut(MedicalRecordBase):
    id: int
    pet_id: int

    class Config:
        from_attributes = True
