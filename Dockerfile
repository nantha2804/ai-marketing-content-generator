FROM python:3.12-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
	PYTHONDONTWRITEBYTECODE=1 \
	PORT=8080

COPY pyproject.toml uv.lock ./

RUN pip install --no-cache-dir uv \
	&& uv sync --frozen --no-install-project

COPY . .

EXPOSE 8080

CMD ["uv", "run", "--no-sync", "python", "app.py"]