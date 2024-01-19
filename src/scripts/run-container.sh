#!/bin/bash

sudo docker run \
    -e DOCKERIZED=True \
    -e POSTGRES_USER={POSTGRES_USER} \
    -e POSTGRES_PASSWORD={POSTGRES_PASSWORD} \
    -e POSTGRES_DB={POSTGRES_DB} \
    -e POSTGRES_HOST={POSTGRES_HOST} \
    -e POSTGRES_PORT={POSTGRES_PORT} \
    -e aws_access_key_id={aws_access_key_id} \
    -e aws_secret_access_key={aws_secret_access_key} \
    -e region_name={region_name} \
    -e aws_s3_bucket={BUCKET_NAME} \
    -e COPERNICUS_API_USER={COPERNICUS_API_USER} \
    -e COPERNICUS_API_SECRET={COPERNICUS_API_SECRET} \
    -e COPERNICUS_API_URL={COPERNICUS_API_URL} \
    -e DOCKER_SWARM_MANAGER_IP={DOCKER_SWARM_MANAGER_IP} \
    -e DOCKER_SWARM_JOIN_TOKEN_MANAGER={DOCKER_SWARM_JOIN_TOKEN_MANAGER} \
    -e DOCKER_SWARM_JOIN_TOKEN_WORKER={DOCKER_SWARM_JOIN_TOKEN_WORKER} \
    -e FIRST_SUPERUSER={FIRST_SUPERUSER} \
    -e FIRST_SUPERUSER_PASSWORD={FIRST_SUPERUSER_PASSWORD} \
    --name main_api \
    taraman12/solar-park-detection-api:latest
