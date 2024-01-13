#!/bin/bash

# https://gist.github.com/didip/ff5088fd023624aba7c0
set -ex

# PARENT_DIR=$(basename "${PWD%/*}")
PARENT_DIR="solar-park-detection"

CURRENT_DIR="${PWD##*/}"
IMAGE_NAME="$PARENT_DIR-$CURRENT_DIR"
REGISTRY="taraman12"
TAG="1"

docker build -t ${REGISTRY}/${IMAGE_NAME} -f ${CURRENT_DIR}.dockerfile .
docker push ${REGISTRY}/${IMAGE_NAME}
