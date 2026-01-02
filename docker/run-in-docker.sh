IMAGE_NAME="learn-llms:latest"


# if ${1} is provided and is equal to "build", build the container
if [ "$1" = "build" ]; then
    docker build -t $IMAGE_NAME -f Dockerfile ..
else
    docker run --rm -it \
        -v "$(pwd)/..":/home/learn-llms \
        -w /home/learn-llms \
        --env-file ../.env \
        $IMAGE_NAME \
        bash
fi