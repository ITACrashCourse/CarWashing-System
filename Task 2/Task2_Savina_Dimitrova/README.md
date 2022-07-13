# Task2



## First Steps

Download the latest image of postgres.

```bash
docker pull postgres:latest
```
Then create connection.
```bash
docker run -p 5432:5432 --name container-postgresdb -e POSTGRES_PASSWORD=root -d postgres

OUTPUT:
latest: Pulling from library/postgres
461246efe0a7: Pull complete 
8d6943e62c54: Pull complete 
558c55f04e35: Pull complete 
186be55594a7: Pull complete 
f38240981157: Pull complete 
e0699dc58a92: Pull complete 
066f440c89a6: Pull complete 
ce20e6e2a202: Pull complete 
c0f13eb40c44: Pull complete 
3d7e9b569f81: Pull complete 
2ab91678d745: Pull complete 
ffc80af02e8a: Pull complete 
f3a57056b036: Pull complete 
Digest: sha256:3e2eba0a6efbeb396e086c332c5a85be06997d2cf573d34794764625f405df4e
Status: Downloaded newer image for postgres:latest
4e631324e1ec93e6d0632993891d21b220557252237776f7e47f78de1b582be2

```
Check to make sure container and images are all created.
```bash
docker ps -a

OUTPUT:
CONTAINER ID   IMAGE      COMMAND                  CREATED         STATUS         PORTS                                       NAMES
4e631324e1ec   postgres   "docker-entrypoint.s…"   7 minutes ago   Up 6 minutes   0.0.0.0:5432->5432/tcp, :::5432->5432/tcp   container-postgresdb

```
```bash
docker images

OUTPUT:
REPOSITORY   TAG       IMAGE ID       CREATED        SIZE
postgres     latest    1133a9cdc367   28 hours ago   376MB

```
Then connect. 
```bash
psql -h localhost -p port -U postgres -d postgres
```
