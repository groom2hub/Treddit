FROM python:3.11-slim AS base

# konlpy(Okt)는 JVM이 필요하다
RUN apt-get update \
    && apt-get install -y --no-install-recommends default-jre-headless \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    TZ=Asia/Seoul

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY pipeline ./pipeline


# CI용: docker build --target test -t treddit-pipeline-test . && docker run --rm treddit-pipeline-test
FROM base AS test
COPY requirements-dev.txt pytest.ini ./
RUN pip install --no-cache-dir -r requirements-dev.txt
COPY tests ./tests
CMD ["pytest", "-v"]


FROM base AS runtime
RUN useradd --create-home app
USER app

ENTRYPOINT ["python", "-m", "pipeline"]
CMD ["run"]
