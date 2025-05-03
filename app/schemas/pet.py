from datetime import date
from typing import Optional, List
from pydantic import BaseModel, Field

from app.database.types import AnimalType, RecordType


class MedicalRecordBase(BaseModel):
    record_type: RecordType
    description: Optional[str] = Field(default=None, max_length=400)
    document_url: Optional[str] = Field(default=None, max_length=200)

    class Config:
        from_attributes = True


class MedicalRecordOut(MedicalRecordBase):
    id: int
    pet_id: int


class PetBase(BaseModel):
    name: str = Field(max_length=50)
    animal_type: AnimalType
    breed: Optional[str] = Field(default="Без породы", max_length=50)
    birth_date: Optional[date] = None
    medical_notes: Optional[str] = None

class PetUpdate(BaseModel):
    name: str = Field(max_length=50)
    breed: Optional[str] = Field(default="Без породы", max_length=50)
    birth_date: Optional[date] = None
    medical_notes: Optional[str] = None


class PetCreate(PetBase):
    pass


class PetOut(PetBase):
    id: int
    owner_id: int
    medical_records: List[MedicalRecordOut] = []

    class Config:
        from_attributes = True


PetOut.model_rebuild()
