from fastapi import FastAPI, Header, UploadFile, File, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from app.db import get_db
from app.models.tables import Organization



app = FastAPI(title="RAG System API")


# later we'll add startup event to connet Postgres/Qdrant later

class QueryRequest(BaseModel):
    question: str


@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/")
async def root():
    return {"message": "Welcome to the RAG System API"}

@app.post("/query")
async def query_documents(
    request: QueryRequest,
    org_id: str = Header(...),
    db: AsyncSession = Depends(get_db)

):

    # this will eventually:
    #1. check org_id in Postgres
    #2. Search Qdrant
    #3. Call Azure OpenAI
    # For now, just return a placeholder

    # Check if org exists in database
    result = await db.execute(
        select(Organization).where(Organization.id == org_id)
    )
    org = result.scalar_one_or_none()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    return {
        "answer": "This is a placeholder answer",
        "question": request.question,
        "org_id": org_id,
            }

@app.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    org_id: str = Header(...)
):
    # This will eventually:
    # 1. Save file to blob storage
    # 2. Send message to Service Bus queue
    # For now, just confirm we received it
    return {
        "filename": file.filename,
        "org_id": org_id,
        "status": "received - processing queued"
    }

