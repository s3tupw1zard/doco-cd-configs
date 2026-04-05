# Bunkerweb Prerequisites

The Docker networks need to be created manually:

```
docker network create \
  --driver bridge \
  --subnet 10.20.30.0/24 \
  bw-universe

docker network create \
  --driver bridge \
  bw-services

docker network create \
  --driver bridge \
  bw-docker

docker network create \
  --driver bridge \
  bw-db
```