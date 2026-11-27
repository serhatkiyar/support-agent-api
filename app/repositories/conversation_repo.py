from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import models
from ..models.enums import ConvStatus


class ConversationRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_conversation(
        self,
        user_id: int,
        context_metadata: dict | None = None,
    ) -> models.Conversation:
        conversation = models.Conversation(
            user_id=user_id,
            context_metadata=context_metadata,
        )
        self.db.add(conversation)
        await self.db.commit()
        await self.db.refresh(conversation)
        return conversation

    async def get_conversation(
        self, conversation_id: int
    ) -> models.Conversation | None:
        stmt = select(models.Conversation).where(
            models.Conversation.id == conversation_id
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_user_conversations(
        self, user_id: int, limit: int = 50, offset: int = 0
    ) -> list[models.Conversation]:
        stmt = (
            select(models.Conversation)
            .where(models.Conversation.user_id == user_id)
            .order_by(models.Conversation.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def update_status(
        self,
        conversation_id: int,
        status: ConvStatus,
        context_metadata: dict | None = None,
    ) -> models.Conversation | None:
        conversation = await self.get_conversation(conversation_id)
        if conversation is None:
            return None

        conversation.status = status.value
        if context_metadata is not None:
            conversation.context_metadata = context_metadata

        await self.db.commit()
        await self.db.refresh(conversation)
        return conversation

    async def add_message(
        self,
        conversation_id: int,
        role: str,
        content: str,
        token_usage: int | None = None,
        latency_ms: float | None = None,
        confidence_score: float | None = None,
    ) -> models.Message:
        message = models.Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            token_usage=token_usage,
            latency_ms=latency_ms,
            confidence_score=confidence_score,
        )
        self.db.add(message)
        await self.db.commit()
        await self.db.refresh(message)
        return message

    async def list_messages(
        self, conversation_id: int, limit: int = 50, offset: int = 0
    ) -> list[models.Message]:
        stmt = (
            select(models.Message)
            .where(models.Message.conversation_id == conversation_id)
            .order_by(models.Message.created_at.asc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
