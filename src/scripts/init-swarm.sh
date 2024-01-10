#!/bin/bash

# Initialize the Docker Swarm
docker swarm init

# Get the IP address of the machine
IP_ADDRESS=$(hostname -I | awk '{print $1}')

# Add the IP address to the environment variables
echo "export DOCKER_SWARM_MANAGER_IP=$IP_ADDRESS" >> ~/.bashrc

# Get the Docker Swarm join-token for a manager
JOIN_TOKEN_MANAGER=$(docker swarm join-token manager -q)

# Add the join-token to the environment variables
echo "export DOCKER_SWARM_JOIN_TOKEN_MANAGER=$JOIN_TOKEN_MANAGER" >> ~/.bashrc

# Get the Docker Swarm join-token for a worker
JOIN_TOKEN_WORKER=$(docker swarm join-token worker -q)

# Add the join-token to the environment variables
echo "export DOCKER_SWARM_JOIN_TOKEN_WORKER=$JOIN_TOKEN_WORKER" >> ~/.bashrc

# Source the .bashrc file to load the new environment variable
source ~/.bashrc

# export the environment variables
source .env

# start the docker stack with the docker-compose.yml file
envsubst < docker-compose.yml | sudo docker stack deploy -c - main
