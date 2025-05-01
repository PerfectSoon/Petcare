from dataclasses import dataclass
from typing import Optional

from fastapi import HTTPException

from app.database.models import MedicalRecord
from app.repositories import MedicalRecordRepo, PetRepository

from app.schemas import MedicalRecordBase


@dataclass(kw_only=True, frozen=True, slots=True)
class MedRecordService:
    repository: MedicalRecordRepo
    pet_repo: Optional[PetRepository] = None

    async def create_med_record(
        self, owner_id: int, pet_id: int, record_data: MedicalRecordBase
    ) -> MedicalRecord:
        pet = await self.pet_repo.get_by_id(pet_id)

        if not pet:
            raise HTTPException(status_code=400, detail="Питомец не найден")
        if pet.owner_id != owner_id:
            raise HTTPException(
                status_code=403,
                detail="Вы не являетесь владельцем данного питомца",
            )
        med_record = MedicalRecord(
            pet_id=pet_id, **record_data.model_dump(exclude_unset=True)
        )

        return await self.repository.create(med_record)

    async def delete_med_record(self, owner_id: int, med_rec_id: int) -> None:
        med_rec = await self.repository.get_by_id(med_rec_id)
        if not med_rec:
            raise HTTPException(
                status_code=400, detail="Медицинская запись не найдена"
            )
        pet = await self.repository.get_pet_by_id(med_rec_id)
        if not pet or pet.owner_id != owner_id:
            raise HTTPException(status_code=403, detail="Доступ запрещен")
        await self.repository.delete(med_rec_id)

    async def update_med_record(
        self, owner_id: int, med_rec_id: int, data: MedicalRecordBase
    ) -> MedicalRecord:

        med_rec = await self.repository.get_by_id(med_rec_id)
        if not med_rec:
            raise HTTPException(
                status_code=400, detail="Медицинская запись не найдена"
            )
        pet = await self.repository.get_pet_by_id(med_rec_id)
        print(pet)
        print(f"pet.owner_id - {pet.owner_id} | owner_id - {owner_id}")
        if not pet:
            raise HTTPException(status_code=403, detail="Питомец не найден")
        if pet.owner_id != owner_id:
            raise HTTPException(status_code=403, detail="Доступ запрещен Ы")

        return await self.repository.update(med_rec, data)
