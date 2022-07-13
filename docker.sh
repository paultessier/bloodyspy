version=1.0.0
port=8001

if [[ "$(docker images -q spyblood:${version} 2> /dev/null)" == "" ]]; then
    echo building docker image spyblood:${version} ...
    docker build -t spyblood:${version} .
fi

docker run -it -d --name spyblood${version} -p ${port}:8000 spyblood:${version}

# CHECKS
# docker image ls | grep spyblood
# docker container ls | grep spyblood${version}
docker image ls
docker container ls

# LOGIN TO DOCKER HUB and fill username & password
docker login

# UPLOAD IMAGE
docker tag spyblood:${version} paultessier/spyblood:${version}
docker image push paultessier/spyblood:${version}

# LOGOUT FROM DOCKER HUB
docker logout