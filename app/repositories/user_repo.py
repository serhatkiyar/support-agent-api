from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import models
from ..schemas.schemas import UserCreate


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_user(self, user: UserCreate, hashed_password: str) -> models.User:
        new_user = models.User(
            name=user.name,
            email=user.email,
            password=hashed_password,
        )

        self.db.add(new_user)
        await self.db.commit()
        await self.db.refresh(new_user)
        return new_user

    async def get_user_by_id(self, user_id: int) -> models.User | None:
        stmt = select(models.User).where(models.User.id == user_id)
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()
        return user

    async def get_user_by_email(self, email: str) -> models.User | None:
        stmt = select(models.User).where(models.User.email == email)
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()
        return user

    async def delete_user(self, user_id: int) -> bool:
        stmt = delete(models.User).where(models.User.id == user_id)
        result = await self.db.execute(stmt)
        await self.db.commit()
        return (result.rowcount or 0) > 0
