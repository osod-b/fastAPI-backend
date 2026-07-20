#!/bin/bash

DOCK_CONTAINER=$(sudo docker ps --filter "publish=8000" --format "{{.ID}}")

echo "Stopping Container $DOCKER_CONTAINER"

sudo docker stop "$DOCK_CONTAINER"

echo "Stopped"

