from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession


from app.database.connection import get_db
from app.database.models import (
    User,
    UserType,
    ProviderType,
    Service,
    Provider,
    Owner,
)
from app.core.security import decode_access_token
from app.repositories.user_repo import UserRepository
from app.services.user_service import UserService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
) -> User:
    token_data = decode_access_token(token)
    user_service = UserService(repository=UserRepository(db=db))

    user = await user_service.user_by_id(int(token_data.sub))

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не найден",
        )
    return user


async def get_current_active_owner(
    current_user: User = Depends(get_current_user),
) -> Owner:
    if current_user.role != UserType.owner:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Пользователь не является владельцем",
        )

    return current_user


async def get_current_active_provider(
    current_user: User = Depends(get_current_user),
) -> Provider:
    if current_user.role != UserType.provider:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Пользователь не является провайдером",
        )

    if (
        current_user.provider.provider_type == ProviderType.vet
        and not current_user.provider.is_verified
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Для доступа ветеринарам необходимо пройти верификацию документов.",
        )

    return current_user


async def validate_service_group(
    service_id: int,
    current_provider: Provider = Depends(get_current_active_provider),
    db: AsyncSession = Depends(get_db),
) -> Service:

    service = await db.get(Service, service_id)
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Сервис не найден"
        )
    if service.group != current_provider.service_type:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                f"Услуга '{service.name}' ({service.group}) не доступна "
                f"для данного поставщика услуг {current_provider.service_type}"
            ),
        )
    return service
