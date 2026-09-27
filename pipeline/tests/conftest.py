import os

# pipeline.config.Settings는 import 시점에 환경변수를 읽으므로 먼저 테스트용 DB를 지정한다.
# 파일 기반 SQLite를 써서 여러 커넥션이 같은 DB를 보게 한다.
os.environ["DATABASE_URL"] = "sqlite:////tmp/pipeline-test.db"

import pytest

from pipeline.db import Base, SessionLocal, engine


@pytest.fixture
def session():
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as s:
        yield s
    Base.metadata.drop_all(bind=engine)
