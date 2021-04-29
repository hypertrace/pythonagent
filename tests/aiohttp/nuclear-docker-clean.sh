#!/bin/bash
set -x
docker ps -aq
docker stop $(docker ps -aq)
docker rm $(docker ps -aq)
docker rmi $(docker images -q)
docker image prune -a -f
docker volume prune -f
