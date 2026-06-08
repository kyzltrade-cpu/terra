from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from backend.database import get_db
from backend.main import app


@pytest.fixture
def mock_db():
    session = MagicMock()
    return session


@pytest.fixture
def client(mock_db):
    app.dependency_overrides[get_db] = lambda: mock_db
    yield TestClient(app)
    app.dependency_overrides.clear()
