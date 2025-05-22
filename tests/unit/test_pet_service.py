import pytest
from contextlib import nullcontext as does_not_raise
from pydantic import ValidationError
from unittest.mock import AsyncMock

from app.services import PetService
from app.schemas import PetCreate, PetUpdate
from app.database.models import Pet

@pytest.fixture
def repo():
    return AsyncMock()

@pytest.fixture
def service(repo):
    return PetService(pet_repository=repo)

@pytest.mark.asyncio
@pytest.mark.parametrize(
    "name, animal_type, breed, expectation",
    [
        # ✅ Корректные данные — без ошибок
        ("A", "cat", "B", does_not_raise()),
        ("A" * 50, "dog", "B" * 50, does_not_raise()),

        # ✅ Пустые строки
        ("", "cat", "Mixed", does_not_raise()),
        ("Buddy", "dog", "", does_not_raise()),

        # ✅ Спецсимволы
        ("Барсик-2", "cat", "Сиамская (длинношерстная)", does_not_raise()),
        ("Кот$", "dog", "#Порода_123", does_not_raise()),

        # ❌ Некорректный тип animal_type
        ("Тузик", "invalid_type", "Дворняга", pytest.raises(ValidationError)),
        ("Бобик", 123, 456.7, pytest.raises(ValidationError)),
        (None, "cat", "Перс", pytest.raises(ValidationError)),
    ]
)
async def test_registry_pet(service, repo, name, animal_type, breed, expectation):
    with expectation:

        pet_data = PetCreate(name=name, animal_type=animal_type, breed=breed)

    if expectation is does_not_raise():

        created_pet = Pet(owner_id=42, **pet_data.model_dump())
        repo.create.return_value = created_pet

        result = await service.registry_pet(pet_data, owner_id=42)

        repo.create.assert_awaited_once_with(
            owner_id=42,
            name=name,
            animal_type=animal_type,
            breed=breed
        )
        assert result == created_pet
    else:
        repo.create.assert_not_awaited()


@pytest.mark.asyncio
async def test_get_pet_by_id_found(service, repo):
    pet = Pet(id=1, owner_id=42, name="Барсик", animal_type="cat", breed="Мейн-кун")
    repo.get.return_value = pet

    result = await service.get_pet_by_id(1)

    repo.get.assert_called_once_with(1)
    assert result == pet

@pytest.mark.asyncio
async def test_get_pet_by_id_not_found(service, repo):
    repo.get.return_value = None

    result = await service.get_pet_by_id(999)

    repo.get.assert_called_once_with(999)
    assert result is None

@pytest.mark.asyncio
async def test_list_pets_for_owner(service, repo):
    pets = [
        Pet(id=1, owner_id=42, name="A", animal_type="dog", breed="B"),
        Pet(id=2, owner_id=42, name="C", animal_type="cat", breed="D"),
    ]
    repo.list_by_owner.return_value = pets

    result = await service.list_pets_by_owner(owner_id=42)

    repo.list_by_owner.assert_called_once_with(42)
    assert result == pets

@pytest.mark.asyncio
async def test_update_pet_success(service, repo):
    # Используем PetUpdate и передаём animal_type
    update_data = PetUpdate(name="Новый", animal_type="dog", breed="Сибирский")
    existing = Pet(id=1, owner_id=1, name="Old", animal_type="dog", breed="OldBreed")
    updated = Pet(id=1, owner_id=1, name="Новый", animal_type="dog", breed="Сибирский")

    repo.get.return_value = existing
    repo.update.return_value = updated

    result = await service.update_pet(1, update_data)

    repo.get.assert_called_once_with(1)
    repo.update.assert_awaited_once_with(1, update_data)
    assert result == updated

@pytest.mark.asyncio
async def test_update_pet_not_found(service, repo):
    repo.get.return_value = None
    update_data = PetUpdate(name="X", animal_type="cat", breed="Y")

    result = await service.update_pet(1, update_data)

    repo.get.assert_called_once_with(1)
    repo.update.assert_not_awaited()
    assert result is None

@pytest.mark.asyncio
async def test_delete_pet_found(service, repo):
    repo.delete.return_value = True

    result = await service.delete_pet(1)

    repo.delete.assert_awaited_once_with(1)
    assert result is True

@pytest.mark.asyncio
async def test_delete_pet_not_found(service, repo):
    repo.delete.return_value = False

    result = await service.delete_pet(999)

    repo.delete.assert_awaited_once_with(999)
    assert result is False


@pytest.mark.asyncio
async def test_delete_pet_found(service, repo):
    repo.delete.return_value = True

    result = await service.delete_pet(1)

    repo.delete.assert_awaited_once_with(1)
    assert result is True
