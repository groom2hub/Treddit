FROM python:3.11-slim AS base

# konlpy(Okt)는 JVM이 필요하다
RUN apt-get update \
    && apt-get install -y --no-install-recommends default-jre-headless \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .


# CI용: docker build --target test -t treddit-server-test . && docker run --rm treddit-server-test
FROM base AS test
COPY requirements-dev.txt .
RUN pip install --no-cache-dir -r requirements-dev.txt
CMD ["pytest", "-v"]


FROM base AS runtime
RUN rm -rf tests requirements-dev.txt pytest.ini \
    && useradd --create-home app && chown -R app /app
USER app

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
