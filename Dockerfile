FROM python:3.12.2-slim

RUN pip install poetry
COPY poetry.lock pyproject.toml ./
RUN poetry install --only main --no-root

COPY ozon_importer /ozon_importer

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

ENTRYPOINT ["poetry", "run", "faststream", "run", "ozon_importer/main:app", "--log-level", "debug"]