from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.depends import get_current_active_owner
from app.database.models import Owner
from app.repositories import MedicalRecordRepo
from app.services import PetService, MedRecordService
from app.repositories import PetRepository
from app.schemas import (
    PetCreate,
    PetOut,
    PetBase,
    MedicalRecordBase,
    MedicalRecordOut,
)
from app.database.connection import get_db


router = APIRouter()


@router.post("/register", response_model=PetOut)
async def register_pet(
    pet_in: PetCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Owner = Depends(get_current_active_owner),
):
    pet_service = PetService(pet_repository=PetRepository(db=db))

    created_pet = await pet_service.registry_pet(
        pet_in, owner_id=current_user.id
    )
    if created_pet is None:
        raise HTTPException(status_code=400, detail="Питомец не создан")
    return created_pet


@router.delete("/delete/{pet_id}", status_code=204)
async def delete_pet(pet_id: int, db: AsyncSession = Depends(get_db)):
    pet_repo = PetRepository(db=db)
    pet_service = PetService(pet_repository=pet_repo)

    await pet_service.delete_pet(pet_id)

    return {"detail": "Питомец удален"}


@router.put("/update/{pet_id}", response_model=PetOut)
async def update_pet(
    pet_id: int,
    pet_data: PetBase,
    db: AsyncSession = Depends(get_db),
):
    pet_service = PetService(pet_repository=PetRepository(db=db))

    updated = await pet_service.update_pet(pet_id, pet_data)
    if not updated:
        raise HTTPException(status_code=404, detail="Питомец не обновлен")
    return updated


@router.post("/{pet_id}/medical/create", response_model=MedicalRecordOut)
async def create_med_rec(
    med_rec_data: MedicalRecordBase,
    pet_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Owner = Depends(get_current_active_owner),
):
    service = MedRecordService(repository=MedicalRecordRepo(db=db),pet_repo=PetRepository(db=db))

    created_med_rec = await service.create_med_record(
        current_user.id, pet_id, med_rec_data
    )
    if created_med_rec is None:
        raise HTTPException(status_code=400, detail="Данные не созданы")

    return created_med_rec

@router.delete("medical/delete/{med_rec_id}", status_code=204)
async def delete_med_rec(
    med_rec_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Owner = Depends(get_current_active_owner),
):
    service = MedRecordService(repository=MedicalRecordRepo(db=db))

    await service.delete_med_record(
        current_user.id, med_rec_id
    )

    return {"detail": "Медицинская запись удалена"}


@router.put("medical/update/{med_rec_id}", response_model=MedicalRecordOut)
async def update_med_rec_for_pet(
    med_rec_id: int,
    med_rec_data: MedicalRecordBase,
    db: AsyncSession = Depends(get_db),
    current_user: Owner = Depends(get_current_active_owner),
):
    service = MedRecordService(repository=MedicalRecordRepo(db=db))

    updated = await service.update_med_record(
        current_user.id, med_rec_id, med_rec_data
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Данные не обновлены")
    return updated
