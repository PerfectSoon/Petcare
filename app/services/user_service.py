from dataclasses import dataclass
from typing import Type, TypeVar, Optional
from fastapi import HTTPException
from pydantic import BaseModel

from app.core.security import get_password_hash, verify_password
from app.database.models import User, Provider, Owner
from app.repositories import ServiceRepository
from app.repositories import UserRepository
from app.schemas import UserAuth, ProviderCreate, OwnerCreate


@dataclass(kw_only=True, frozen=True, slots=True)
class UserService:
    repository: UserRepository
    service_repository: Optional[ServiceRepository] = None

    T = TypeVar("T")

    async def _register_user(
        self, user_data: BaseModel, model_class: Type[T]
    ) -> T:

        existing_user = await self.repository.get_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=400, detail="Такой пользователь уже существует"
            )

        hashed_password = get_password_hash(user_data.password_hash)
        updated = user_data.model_copy(
            update={"password_hash": hashed_password}
        )
        user = model_class(**updated.model_dump())

        return await self.repository.create(user)

    async def register_owner(self, user_data: OwnerCreate) -> Owner:
        return await self._register_user(user_data, Owner)

    async def register_provider(self, user_data: ProviderCreate) -> Provider:
        created_provider = await self._register_user(user_data, Provider)

        await self.service_repository.create_ps_for_owner(
            created_provider, created_provider.provider_type
        )

        return created_provider

    async def authenticate_user(self, user_data: UserAuth) -> User | None:
        user = await self.repository.get_by_email(user_data.email)
        if not user:
            raise HTTPException(
                status_code=400, detail="Пользователь не найден"
            )
        if not verify_password(user_data.password, user.password_hash):
            return None
        return user

    async def user_by_id(self, user_id: id) -> User | None:
        user = await self.repository.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=400, detail="Пользователь не найден"
            )
        return user
