FROM python:alpine

WORKDIR /app

RUN apk add poetry

COPY poetry.lock pyproject.toml ./

RUN poetry install --no-root

COPY . .

CMD ["poetry", "run", "python", "main.py"]