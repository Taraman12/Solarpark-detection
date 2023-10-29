import pytest
from httpx import AsyncClient

from app.core.config import settings
from app.main import app

print(settings.HOST)
base_url = "http://localhost:8000/api/v1/"


@pytest.mark.anyio
async def test_root():
    async with AsyncClient(app=app, base_url=base_url) as ac:
        response = await ac.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "API is running"}
