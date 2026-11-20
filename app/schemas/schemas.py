from pydantic import BaseModel, EmailStr, field_validator


class UserBase(BaseModel):
    name: str
    email: EmailStr


class UserCreate(UserBase):
    password: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, password: str):
        if len(password) < 8:
            raise ValueError("Şifre en az 8 karakterli olmalıdır.")
        if not any(char.isupper() for char in password):
            raise ValueError("Şifre en az bir büyük harf içermelidir.")
        if not any(char.isdigit() for char in password):
            raise ValueError("Şifre en az bir rakam içermelidir.")
        return password


class Conversation(BaseModel):
    id: int
    user_id: int


class Message(BaseModel):
    id: int
    conversation_id: int
    role: str
    content: str
    token_usage: int | None = None
    latency_ms: float | None = None
    confidence_score: float | None = None


class KnowledgeDocument(BaseModel):
    title: str
    source_type: str


class KnowledgeDocumentIn(KnowledgeDocument):
    pass


class DocumentChunk(BaseModel):
    document_id: int
    content: str
    chunk_index: int
    embedding: list[float]
    search_vector: list[float]


class DocumentChunkIn(DocumentChunk):
    pass
