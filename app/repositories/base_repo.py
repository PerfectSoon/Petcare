from typing import Type, TypeVar, Generic, List, Optional

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete

T = TypeVar("T")


class AbstractRepository(Generic[T]):
    def __init__(self, db: AsyncSession, model: Type[T]):
        self.model = model
        self.db = db

    async def get_by_id(self, id: int) -> Optional[T]:
        return await self.db.get(self.model, id)

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        result = await self.db.execute(
            select(self.model).offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    async def create(self, obj_in: T) -> T:
        self.db.add(obj_in)
        await self.db.commit()
        await self.db.refresh(obj_in)
        return obj_in

    async def update(self, db_obj: T, obj_in: BaseModel | dict) -> T:
        if not db_obj:
            raise ValueError("Объект для обновления не существует")

        if not obj_in:
            return db_obj

        obj_data = (
            obj_in
            if isinstance(obj_in, dict)
            else obj_in.dict(exclude_unset=True)
        )

        for field, value in obj_data.items():
            setattr(db_obj, field, value)

        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def delete(self, id: int) -> None:
        await self.db.execute(delete(self.model).where(self.model.id == id))
        await self.db.commit()
