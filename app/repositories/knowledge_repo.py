from sqlalchemy import delete, func, literal, select, union_all
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import models
from ..schemas.schemas import DocumentChunkCreate, KnowledgeDocumentCreate

TS_CONFIG = "turkish"


class KnowledgeRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def add_document(
        self, document: KnowledgeDocumentCreate
    ) -> models.KnowledgeDocument:
        db_document = models.KnowledgeDocument(**document.model_dump())
        self.db.add(db_document)
        await self.db.commit()
        await self.db.refresh(db_document)
        return db_document

    async def add_chunks(
        self, document_chunk: DocumentChunkCreate
    ) -> models.DocumentChunk:
        chunk = models.DocumentChunk(
            **document_chunk.model_dump(),
            search_vector=func.to_tsvector(TS_CONFIG, document_chunk.content),
        )
        self.db.add(chunk)
        await self.db.commit()
        await self.db.refresh(chunk)
        return chunk

    async def get_document(
        self, document_id: int
    ) -> models.KnowledgeDocument | None:
        stmt = select(models.KnowledgeDocument).where(
            models.KnowledgeDocument.id == document_id
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_documents(
        self, limit: int = 50, offset: int = 0
    ) -> list[models.KnowledgeDocument]:
        stmt = (
            select(models.KnowledgeDocument)
            .order_by(models.KnowledgeDocument.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def delete_document(self, document_id: int) -> None:
        stmt = delete(models.KnowledgeDocument).where(
            models.KnowledgeDocument.id == document_id
        )
        await self.db.execute(stmt)
        await self.db.commit()

    async def search(
        self,
        query_text: str,
        query_embedding: list[float],
        limit: int = 5,
        rrf_k: int = 60,
    ) -> list[models.DocumentChunk]:
        """Hybrid search combining pgvector cosine similarity and PostgreSQL FTS via RRF."""
        candidate_limit = max(limit * 4, 20)

        semantic_cte = (
            select(
                models.DocumentChunk.id.label("id"),
                func.row_number()
                .over(
                    order_by=models.DocumentChunk.embedding.cosine_distance(
                        query_embedding
                    )
                )
                .label("rank"),
            )
            .limit(candidate_limit)
            .cte("semantic_results")
        )

        ts_query = func.websearch_to_tsquery(TS_CONFIG, query_text)
        keyword_cte = (
            select(
                models.DocumentChunk.id.label("id"),
                func.row_number()
                .over(
                    order_by=func.ts_rank_cd(
                        models.DocumentChunk.search_vector, ts_query
                    ).desc()
                )
                .label("rank"),
            )
            .where(models.DocumentChunk.search_vector.op("@@")(ts_query))
            .limit(candidate_limit)
            .cte("keyword_results")
        )

        semantic_scores = select(
            semantic_cte.c.id.label("chunk_id"),
            (1.0 / (literal(rrf_k) + semantic_cte.c.rank)).label("score"),
        )
        keyword_scores = select(
            keyword_cte.c.id.label("chunk_id"),
            (1.0 / (literal(rrf_k) + keyword_cte.c.rank)).label("score"),
        )

        combined = union_all(semantic_scores, keyword_scores).subquery("combined")
        rrf_scores = (
            select(
                combined.c.chunk_id,
                func.sum(combined.c.score).label("total_score"),
            )
            .group_by(combined.c.chunk_id)
            .order_by(func.sum(combined.c.score).desc())
            .limit(limit)
            .subquery("rrf_scores")
        )

        stmt = (
            select(models.DocumentChunk)
            .join(rrf_scores, models.DocumentChunk.id == rrf_scores.c.chunk_id)
            .order_by(rrf_scores.c.total_score.desc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
