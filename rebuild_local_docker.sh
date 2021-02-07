#!/bin/zsh
# A simple script to rebuild local docker based on a different compose
docker stop "$(docker ps -ql)" && docker build -t teachable . && docker-compose -f docker-compose-local.yml run -d  teachable && docker exec -it "$(docker ps -ql)" /bin/bash

