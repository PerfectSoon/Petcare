from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.depends import get_current_active_provider
from app.database.connection import get_db
from app.database.models import Provider
from app.repositories import ServiceRepository
from app.services import ServiceService
from app.schemas import (
    VeterinaryServiceCreate,
    GroomingServiceCreate,
    SittingServiceCreate,
    VeterinaryServiceOut,
    GroomingServiceOut,
    SittingServiceOut,
    ProviderServiceUpdate,
    ProviderServiceOut,
)

router = APIRouter()


@router.post("/create/vet", response_model=VeterinaryServiceOut)
async def create_vet_service(
    data: VeterinaryServiceCreate,
    db: AsyncSession = Depends(get_db),
):
    service = ServiceService(repository=ServiceRepository(db))
    return await service.create_vet_service(data)


@router.post("/create/grooming", response_model=GroomingServiceOut)
async def create_grooming_service(
    data: GroomingServiceCreate,
    db: AsyncSession = Depends(get_db),
):
    service = ServiceService(repository=ServiceRepository(db))
    return await service.create_grooming_service(data)


@router.post("/create/sitting", response_model=SittingServiceOut)
async def create_sitting_service(
    data: SittingServiceCreate,
    db: AsyncSession = Depends(get_db),
):
    service = ServiceService(repository=ServiceRepository(db))
    return await service.create_sitter_service(data)


@router.get("/get/{provider_id}", response_model=list[ProviderServiceOut])
async def get_provider_services(
    provider_id: int,
    db: AsyncSession = Depends(get_db),
):
    service = ServiceService(repository=ServiceRepository(db))
    return await service.list_services(provider_id)


@router.put("/update/{provider_service_id}", response_model=ProviderServiceOut)
async def update_provider_service(
    provider_service_id: int,
    update_data: ProviderServiceUpdate,
    current_provider: Provider = Depends(get_current_active_provider),
    db: AsyncSession = Depends(get_db),
):
    service = ServiceService(repository=ServiceRepository(db))
    return await service.update_service(
        current_provider.id, provider_service_id, update_data
    )


@router.delete("delete/{provider_service_id}")
async def delete_provider_service(
    provider_service_id: int,
    current_provider: Provider = Depends(get_current_active_provider),
    db: AsyncSession = Depends(get_db),
):
    service = ServiceService(repository=ServiceRepository(db))
    await service.delete_service(current_provider.id, provider_service_id)
    return {"detail": "Связь с услугой удалена"}
