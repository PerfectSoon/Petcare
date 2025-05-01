from dataclasses import dataclass
from typing import List, TypeVar, Type

from fastapi import HTTPException
from pydantic import BaseModel

from app.database.models import (
    Service,
    VeterinaryService,
    SittingService,
    GroomingService,
    ProviderType,
)
from app.repositories import ServiceRepository
from app.schemas import (
    VeterinaryServiceCreate,
    SittingServiceCreate,
    GroomingServiceCreate,
    ProviderServiceOut,
)


@dataclass(kw_only=True, frozen=True, slots=True)
class ServiceService:
    repository: ServiceRepository
    T = TypeVar("T")

    async def _create_service(
        self,
        service_data: BaseModel,
        model_class: Type[T],
        provider_type: ProviderType,
    ) -> T:

        service = model_class(
            **service_data.model_dump(), service_type=provider_type
        )
        created_service = await self.repository.create(service)

        await self.repository.create_ps_for_service(
            provider_type, created_service
        )

        return created_service

    async def create_vet_service(
        self, data: VeterinaryServiceCreate
    ) -> VeterinaryService:
        return await self._create_service(
            data, VeterinaryService, ProviderType.vet
        )

    async def create_sitter_service(
        self, data: SittingServiceCreate
    ) -> SittingService:
        return await self._create_service(
            data, SittingService, ProviderType.sitter
        )

    async def create_grooming_service(
        self, data: GroomingServiceCreate
    ) -> GroomingService:
        return await self._create_service(
            data, GroomingService, ProviderType.groomer
        )

    async def list_services(self, provider_id: int) -> List[ProviderServiceOut]:
        items = await self.repository.list_by_provider(provider_id)
        return [ProviderServiceOut.model_validate(item) for item in items]

    async def get_by_id(self, service_id: int) -> Service | None:
        service = await self.repository.get_by_id(service_id)
        if not service:
            raise HTTPException(status_code=404, detail="Услуга не найдена")
        return service

    async def update_service(
        self, provider_id: int, ps_id: int, data: BaseModel
    ) -> ProviderServiceOut:
        ps = await self.repository.get_by_provider_and_id(provider_id, ps_id)
        if not ps:
            raise HTTPException(
                status_code=404, detail="Назначенная услуга не найдена"
            )

        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            raise HTTPException(
                status_code=400, detail="Нет данных для обновления"
            )

        return await self.repository.update(ps, update_data)

    async def delete_service(self, provider_id: int, ps_id: int) -> None:
        ps = await self.repository.get_by_provider_and_id(provider_id, ps_id)
        if not ps:
            raise HTTPException(status_code=404, detail="Услуга не найдена")
        await self.repository.delete(ps.id)
