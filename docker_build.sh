app_name=bloodyspy
version=1.0.0
port=8000

# stop all container and remove images
docker container stop ${app_name}
docker container rm ${app_name}
docker image rm ${app_name}:${version}

# Launch docker daemon if stopped
if [[ "$(pidof dockerd 2> /dev/null)" == "" ]]; then
    echo Launching docker daemon ...
    sudo service docker start
fi

# Build image if not existing
if [[ "$(docker images -q ${app_name}:${version} 2> /dev/null)" == "" ]]; then
    echo building docker image ${app_name}:${version} ...
    docker build -t ${app_name}:${version} .
fi

# CHECKS
# docker image ls | grep ${app_name}
# docker container ls | grep ${app_name}${version}
docker image ls
docker container ls


# LAUNCH THE APPLICATION
docker run -it -d --rm --name ${app_name} -p ${port}:8000 ${app_name}:${version}
echo "=============================================================="
echo "=============================================================="
echo application address: http://localhost:${port}
echo to investigate: docker exec -it ${app_name} /bin/bash
echo "=============================================================="
echo "=============================================================="


