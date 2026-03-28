FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY pyproject.toml README.md ./
RUN pip install --no-cache-dir \
    fastapi \
    uvicorn[standard] \
    pydantic-settings \
    python-dotenv \
    sqlmodel \
    PyPDF2 \
    python-docx \
    python-multipart \
    sentence-transformers \
    httpx \
    langchain \
    langgraph \
    openai \
    qdrant-client \
    minio

COPY app ./app
COPY scripts ./scripts
COPY main.py ./main.py

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
