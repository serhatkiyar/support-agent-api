from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, field_validator

from ..models.enums import ConvStatus, Priority, TicketStatus


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


class UserOut(UserBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class ConversationCreate(BaseModel):
    user_id: int
    context_metadata: dict | None = None


class ConversationOut(ConversationCreate):
    id: int
    status: ConvStatus
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class MessageCreate(BaseModel):
    conversation_id: int
    role: str
    content: str
    token_usage: int | None = None
    latency_ms: float | None = None
    confidence_score: float | None = None


class MessageOut(MessageCreate):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class KnowledgeDocumentCreate(BaseModel):
    title: str
    source_type: str


class KnowledgeDocumentOut(KnowledgeDocumentCreate):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class DocumentChunkBase(BaseModel):
    document_id: int
    content: str
    chunk_index: int


class DocumentChunkCreate(DocumentChunkBase):
    embedding: list[float]


class DocumentChunkOut(DocumentChunkBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class TicketCreate(BaseModel):
    conversation_id: int
    user_id: int
    reason: str
    summary: str
    priority: Priority
    status: TicketStatus


class TicketOut(TicketCreate):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
