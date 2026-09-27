import os

# config.Settings는 import 시점에 환경변수를 읽으므로, 앱을 import하기 전에 테스트용 값을 넣는다
os.environ.update(
    DATABASE_URL="sqlite://",
    JWT_SECRET_KEY="test-secret",
    NAVER_CLIENT_ID="",
    NAVER_CLIENT_SECRET="",
    OPENAI_KEY="",
)

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import models  # noqa: F401  모든 테이블을 Base.metadata에 등록한다
from database import Base, get_db
from main import app

# 인메모리 SQLite를 모든 커넥션이 공유하도록 StaticPool을 쓴다
engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
TestingSession = sessionmaker(bind=engine, autocommit=False, autoflush=False)


@pytest.fixture
def db():
    Base.metadata.create_all(bind=engine)
    session = TestingSession()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(db):
    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def signup(client, username="tester", email="tester@example.com", password="pw123456"):
    return client.post("/api/user/signup", json={
        "username": username,
        "email": email,
        "password": password,
        "confirm_password": password,
    })


def login(client, email="tester@example.com", password="pw123456"):
    response = client.post("/api/user/login", data={"username": email, "password": password})
    return response


@pytest.fixture
def auth_headers(client):
    signup(client)
    token = login(client).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
