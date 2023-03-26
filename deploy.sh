docker volume create docker_volume
docker run -d --name board_app --mount source=docker_volume,target=/db