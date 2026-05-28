from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from src.database.base import Base
from src.database.session import get_db
from src.main import app
from src.models import Movement, Product, User  # noqa: F401

engine = create_engine(
    "sqlite+pysqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db() -> Generator[Session, None, None]:
    """Provide an isolated test database session."""

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def reset_database() -> Generator[None, None, None]:
    """Recreate all tables before each test."""

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    """Return a FastAPI test client with database dependency overridden."""

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def admin_headers(client: TestClient) -> dict[str, str]:
    """Register and authenticate the bootstrap administrator."""

    client.post(
        "/api/v1/auth/register",
        json={"nome": "Admin User", "email": "admin@example.com", "senha": "strongpass123"},
    )
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "admin@example.com", "password": "strongpass123"},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def product_payload() -> dict[str, object]:
    """Return a valid product payload."""

    return {
        "nome": "Notebook Dell",
        "sku": "note-001",
        "descricao": "Notebook corporativo",
        "categoria": "Eletronicos",
        "preco_custo": "2500.00",
        "preco_venda": "3200.00",
        "quantidade_estoque": 10,
        "estoque_minimo": 3,
        "ativo": True,
    }
