from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.deps import get_current_user, get_db
from app.api.router import api_router


@pytest.fixture
def db_mock() -> MagicMock:
    return MagicMock()


@pytest.fixture
def app(db_mock: MagicMock) -> FastAPI:
    test_app = FastAPI()
    test_app.include_router(api_router)

    def override_get_db():
        yield db_mock

    test_app.dependency_overrides[get_db] = override_get_db
    return test_app


@pytest.fixture
def client(app: FastAPI) -> TestClient:
    return TestClient(app)


@pytest.fixture
def staff_user():
    return SimpleNamespace(id="staff-1", role="staff", is_active=True, phone_number="+79990000002")


@pytest.fixture
def admin_user():
    return SimpleNamespace(id="admin-1", role="admin", is_active=True, phone_number="+79990000001")


def override_current_user(app: FastAPI, user) -> None:
    app.dependency_overrides[get_current_user] = lambda: user
