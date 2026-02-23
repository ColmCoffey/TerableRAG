from sqlalchemy import Column, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.sql import func
from app.db import Base

class Organization(Base):
    __tablename__ = "organizations"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=func.now())

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True)
    email = Column(String, nullable=False, unique=True)
    role = Column(String, default="member")
    created_at = Column(DateTime, default=func.now())

class Document(Base):
    __tablename__ = "documents"

    id = Column(String, primary_key=True)
    org_id = Column(String, ForeignKey("organizations.id"), nullable=False)
    filename = Column(String, nullable=False)
    blob_path = Column(String, nullable=False)
    status = Column(String, default="uploaded")
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    metadata_json = Column(JSON, nullable=True)

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    action = Column(String, nullable=False)
    document_id = Column(String, ForeignKey("documents.id"), nullable=False)
    timestamp = Column(DateTime, server_default=func.now())

