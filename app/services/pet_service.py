from dataclasses import dataclass
from typing import List

from fastapi import HTTPException

from app.database.models import Pet
from app.repositories import PetRepository
from app.schemas import PetCreate, PetBase


@dataclass(kw_only=True, frozen=True, slots=True)
class PetService:
    pet_repository: PetRepository

    async def registry_pet(self, pet_data: PetCreate, owner_id: int) -> Pet:

        pet = Pet(**pet_data.model_dump(), owner_id=owner_id)
        if not pet:
            raise HTTPException(status_code=400, detail="Питомец не найден")

        return await self.pet_repository.create(pet)

    async def get_pet_by_id(self, pet_id: int) -> Pet | None:
        pet = await self.pet_repository.get_by_id(pet_id)
        if not pet:
            raise HTTPException(status_code=400, detail="Питомец не найден")
        return pet

    async def list_pets_by_owner(self, owner_id: int) -> List[Pet] | None:
        return await self.pet_repository.list(owner_id)

    async def update_pet(self, pet_id: int, pet_data: PetBase) -> Pet:
        pet = await self.get_pet_by_id(pet_id)
        if not pet:
            raise HTTPException(status_code=400, detail="Питомец не найден")
        return await self.pet_repository.update(pet, pet_data)

    async def delete_pet(self, pet_id: int) -> None:
        pet = await self.get_pet_by_id(pet_id)
        if not pet:
            raise HTTPException(status_code=400, detail="Питомец не найден")
        await self.pet_repository.delete(pet_id)
