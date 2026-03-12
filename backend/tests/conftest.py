from pathlib import Path
import os
import sys

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(BACKEND_DIR))

ADMIN_TOKEN = "test-token"

os.environ["FTSAAS_DATABASE_URL"] = "sqlite://"
os.environ["FTSAAS_ADMIN_TOKEN"] = ADMIN_TOKEN

from app.db import Base, get_db
from app.main import app


TEST_DATABASE_URL = "sqlite://"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


Base.metadata.create_all(bind=engine)
app.dependency_overrides[get_db] = override_get_db


def get_test_client(with_auth: bool = True) -> TestClient:
    client = TestClient(app)
    if with_auth:
        client.headers.update({"X-Admin-Token": ADMIN_TOKEN})
    return client
