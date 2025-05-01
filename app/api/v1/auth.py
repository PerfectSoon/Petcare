from fastapi.security import OAuth2PasswordRequestForm
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token
from app.database.models import User
from app.services import UserService
from app.repositories import UserRepository
from app.repositories import ServiceRepository
from app.database.connection import get_db
from app.schemas import (
    UserOut,
    UserAuth,
    Token,
    OwnerCreate,
    ProviderCreate,
    OwnerOut,
    ProviderOut,
)
from app.api.depends import get_current_user

router = APIRouter()


@router.post("/register/owner", response_model=OwnerOut)
async def register_owner(
    owner_in: OwnerCreate, db: AsyncSession = Depends(get_db)
):
    service = UserService(repository=UserRepository(db))
    return await service.register_owner(owner_in)


@router.post("/register/provider", response_model=ProviderOut)
async def register_provider(
    provider_in: ProviderCreate, db: AsyncSession = Depends(get_db)
):
    service = UserService(
        repository=UserRepository(db), service_repository=ServiceRepository(db)
    )

    return await service.register_provider(provider_in)


@router.post("/login", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    user_auth = UserAuth(email=form_data.username, password=form_data.password)

    service = UserService(repository=UserRepository(db))

    auth_user = await service.authenticate_user(user_auth)
    if not auth_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный логин или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(
        subject=str(auth_user.id),
        role=auth_user.role.value,
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": auth_user.role.value,
    }


@router.get("/profile", response_model=UserOut)
async def get_profile(current_user: User = Depends(get_current_user)):
    return UserOut.from_orm(current_user)


@router.get("/profile/{user_id}", response_model=UserOut)
async def get_profile_by_id(user_id: int, db: AsyncSession = Depends(get_db)):
    service = UserService(repository=UserRepository(db))
    user = await service.user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return user
