from pydantic import BaseModel
from typing import List, Optional
from datatime import datetime

# These are Pydantic models for API requests/responses
# Later we'll add SQLAlchemy models for actual database tab;es

class Organization(BaseModel):
    id: str
    email: str
    org_id: str
    role: str # "admin" or "member"

class Document(BaseModel):
    id: str
    org_id: str
    filename: str
    blob_path: str
    status: str # "uploaded", "processing", "indexed", "failed"
    updated_at: datetime
    metadata: Optional[dict] = None