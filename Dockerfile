FROM python:3.8

WORKDIR /app

ENV APP_ENVIRONMENT=development
ENV APP_PORT=8080
ENV POETRY_VERSION=1.3.2

RUN pip install poetry==$POETRY_VERSION
COPY poetry.lock pyproject.toml /app
RUN poetry config virtualenvs.create false
RUN poetry install $([ "$APP_ENVIRONMENT" = 'production' ] && echo "--no-dev") --no-interaction --no-ansi

COPY . /app

EXPOSE $APP_PORT
CMD uvicorn server:app --port $APP_PORT --host 0.0.0.0 --reload
