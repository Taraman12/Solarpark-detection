import random
import string

# from fastapi.testclient import TestClient

# from app.core.config import settings


def random_lower_string() -> str:
    return "".join(random.choices(string.ascii_lowercase, k=32))
