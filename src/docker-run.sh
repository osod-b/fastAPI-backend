#!/bin/bash
#docker-run.sh

redis-server --port 6379 --daemonize yes
uvicorn app.main:app --host 0.0.0.0 --port 8000