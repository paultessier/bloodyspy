app_name=bloodyspy
prev_version=1.0.0
version=1.0.1
port=5050

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

# LOGIN TO DOCKER HUB and fill username & password
docker login

# UPLOAD IMAGE
docker tag ${app_name}:${version} paultessier/${app_name}:${version}
docker image push paultessier/${app_name}:${version}

# LOGOUT FROM DOCKER HUB
docker logout


# LAUNCH THE APPLICATION
docker container stop ${app_name}${previous_version}
docker run -it -d --name ${app_name}${version} -p ${port}:8000 ${app_name}:${version}
echo "=============================================================="
echo "=============================================================="
echo application address: http://localhost:${port}
echo to investigate: docker exec -it ${app_name}${version} /bin/bash
echo "=============================================================="
echo "=============================================================="

