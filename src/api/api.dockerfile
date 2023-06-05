# commented code is for poetry
# https://fastapi.tiangolo.com/deployment/docker/#docker-compose
# FROM python:3.10 as requirements-stage

# WORKDIR /tmp

# RUN pip install poetry

# COPY ./pyproject.toml ./poetry.lock* /tmp/

# RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

FROM python:3.10-slim

WORKDIR /code

# COPY --from=requirements-stage /tmp/requirements.txt /code/requirements.txt
COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./app /code/app
COPY ./alembic /code/alembic
COPY ./alembic.ini /code/alembic.ini
COPY ./app/cloud/.env /code/app/.env
COPY ./app/cloud/docker-compose.yml /code/app/docker-compose.yml

#CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
CMD ["/bin/bash", "-c","alembic upgrade head; uvicorn app.main:app --host 0.0.0.0 --port 8000"]

# If running behind a proxy like Nginx or Traefik add --proxy-headers
# CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80", "--proxy-headers"]