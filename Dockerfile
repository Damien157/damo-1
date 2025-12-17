FROM python:3.11-slim
WORKDIR /app
COPY pyproject.toml /app/
RUN pip install "poetry-core>=1.7.1"
RUN pip install --no-cache-dir fastapi uvicorn pydantic cryptography
COPY . /app
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
