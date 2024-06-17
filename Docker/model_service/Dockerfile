FROM python:3.9.7

WORKDIR /code

ENV PYTHONPATH "${PYTHONPATH}:/code"

COPY environment /code/

RUN pip install --upgrade pip \
  && pip install --no-cache-dir requests==2.26.0

RUN poetry config virtualenvs.create false \
  && poetry install --no-dev --no-interaction --no-ansi --no-root

COPY src/backend /code/src/backend
COPY src/models /code/src/models
COPY .env /code/src/backend/.env

CMD ["uvicorn", "src.backend.app:app", "--host", "0.0.0.0", "--port", "8003"]
