#!/bin/bash

echo -n "Cleaning up existing docker containers..."

docker kill $(docker ps -q --filter "name=rnr_rooms") >/dev/null 2>&1

docker system prune -a -f --volumes >/dev/null 2>&1

shopt -s extglob

echo "COMPLETE"

echo -n "Creating docker data directory..."

mkdir -p /www/docker_persistent/rnr_rooms/db >/dev/null 2>&1

echo "COMPLETE"

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)

cp -n "$SCRIPT_DIR/env.example" "$SCRIPT_DIR/.env"

echo -n "Bringing up docker container..."

docker-compose -f "$SCRIPT_DIR/docker-compose.yml" up -d

docker system prune -a -f >/dev/null 2>&1

echo "COMPLETE"

echo "Deployment completed successfully."
echo "========================================="
