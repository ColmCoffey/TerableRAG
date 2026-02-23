from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"} 

def test_root():
    response = client.get("/")
    assert response.status_code == 200

def test_query_requires_org_id():
    # should fail without org_id header
    response = client.post("/query", json={"question": "test question"})
    assert response.status_code == 422 #Validation error

def test_query_valid_org_id():
    response = client.post(
        "/query",
        json={"question": "What is machine learning?"},
        headers={"org-id": "org_123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["question"] == "What is machine learning?"
    assert data["org_id"] == "org_123"
    assert "answer" in data

def test_upload_document():
    #Create a fake file for testing
    file_content = b"fake pdf content"
    
    response = client.post(
        "/upload",
        files={"file": ("test.pdf", file_content, "application/pdf")},
        headers={"org-id": "org_123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "test.pdf"
    assert data["org_id"] == "org_123"
    assert data["status"] == "received - processing queued"
    
