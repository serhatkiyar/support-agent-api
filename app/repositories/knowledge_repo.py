from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import models
from ..schemas.schemas import DocumentChunkIn, KnowledgeDocumentIn


class KnowledgeRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def add_document(
        self, document: KnowledgeDocumentIn
    ) -> models.KnowledgeDocument:
        db_document = models.KnowledgeDocument(**document.model_dump())
        self.db.add(db_document)
        await self.db.commit()
        await self.db.refresh(db_document)
        return db_document

    async def add_chunks(
        self, document_chunk: DocumentChunkIn
    ) -> models.DocumentChunk:
        chunk = models.DocumentChunk(**document_chunk.model_dump())
        self.db.add(chunk)
        await self.db.commit()
        await self.db.refresh(chunk)
        return chunk

    async def delete_document(self, document_id: int) -> None:
        stmt = delete(models.KnowledgeDocument).where(
            models.KnowledgeDocument.id == document_id
        )
        await self.db.execute(stmt)
        await self.db.commit()

    async def search(self, embedding: list[float], search_vector: list[float]):
        pass
