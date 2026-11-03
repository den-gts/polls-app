# Возможно тут стоило бы использовать slim. Но я люблю использовать alpine пока хватает его
FROM python:alpine

RUN pip install uv
WORKDIR /app
ENV UV_PROJECT_ENVIRONMENT=/usr/local
COPY pyproject.toml uv.lock ./
RUN uv sync  --frozen --no-dev
COPY . .
CMD ["uv", "run", "gunicorn", "config.wsgi:application", "-user-bind", "0.0.0.0:8000", "--workers", "4"]