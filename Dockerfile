FROM python:3.10-slim

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY wait-for-it.sh /wait-for-it.sh
RUN chmod +x /wait-for-it.sh

COPY . .

EXPOSE 8000

ENTRYPOINT [ \
    "/wait-for-it.sh", \
    "db:5432", \
    "--timeout=30", \
    "--strict", \
    "--", \
    "sh", \
    "-c", \
    "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload" \
]
