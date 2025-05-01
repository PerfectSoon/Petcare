from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database.models import MedicalRecord, Pet
from app.repositories.base_repo import AbstractRepository


class MedicalRecordRepo(AbstractRepository[MedicalRecord]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, MedicalRecord)

    async def get_pet_by_id(self, id: int) -> Pet | None:
        result = await self.db.execute(
            select(Pet)
            .join(MedicalRecord, MedicalRecord.pet_id == Pet.id)
            .where(MedicalRecord.id == id)
            .options(selectinload(Pet.medical_records))
        )
        return result.scalar_one_or_none()
