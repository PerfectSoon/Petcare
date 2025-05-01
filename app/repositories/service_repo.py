from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload

from app.database.models import ProviderService, Service, Provider
from app.database.types import ProviderType
from app.repositories.base_repo import AbstractRepository


class ServiceRepository(AbstractRepository[ProviderService]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, ProviderService)

    async def list_by_provider(self, provider_id: int) -> List[ProviderService]:
        result = await self.db.execute(
            select(ProviderService)
            .options(selectinload(ProviderService.service))
            .where(ProviderService.provider_id == provider_id)
        )

        return list(result.scalars().all())

    async def get_by_provider_and_id(
        self, provider_id: int, ps_id: int
    ) -> ProviderService | None:
        result = await self.db.execute(
            select(ProviderService)
            .where(ProviderService.id == ps_id)
            .where(ProviderService.provider_id == provider_id)
            .options(joinedload(ProviderService.service))
        )

        return result.scalar_one_or_none()

    async def create_ps_for_owner(
        self, created_provider: Provider, provider_type: ProviderType
    ) -> None:
        services = await self.db.execute(
            select(Service).where(Service.service_type == provider_type)
        )
        services = services.scalars().all()

        for service in services:
            ps = ProviderService(
                provider_id=created_provider.id,
                service_id=service.id,
                custom_price=service.base_price,
                custom_duration=service.duration_min,
            )
            await self.create(ps)

    async def create_ps_for_service(
        self, provider_type: ProviderType, created_service
    ) -> None:
        result = await self.db.execute(
            select(Provider.id).where(Provider.provider_type == provider_type)
        )
        provider_ids = result.scalars().all()

        for provider_id in provider_ids:
            ps = ProviderService(
                provider_id=provider_id,
                service_id=created_service.id,
                custom_price=created_service.base_price,
                custom_duration=created_service.duration_min,
            )
            await self.create(ps)
