FROM python:3.11-slim

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

RUN useradd --create-home app
USER app

ENTRYPOINT ["python", "-m", "pipeline"]
CMD ["run"]
