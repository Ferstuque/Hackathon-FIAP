import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_upload_endpoint_no_file():
    """Erro 3: Tentativa de upload sem arquivo."""
    response = client.post("/internal/upload")
    assert response.status_code == 422 # Unprocessable Entity

def test_upload_invalid_file_type():
    """Erro 4: Rejeitar arquivos maliciosos ou não suportados."""
    files = {'file': ('ataque.sh', b'rm -rf /', 'application/x-sh')}
    response = client.post("/internal/upload", files=files)
    
    assert response.status_code == 400
    assert "Invalid file type" in response.text
