app_name=bloodyspy
tag_version=1.0.0
port=8000
UPLOAD_API=False

# stop all container and remove images
# docker system prune -a

# Launch docker daemon if stopped
if [[ "$(pidof dockerd 2> /dev/null)" == "" ]]; then
    echo Launching docker daemon ...
    sudo service docker start
fi

# ==========================================================================================
# ========= FAST API IMAGE =================================================================
# ==========================================================================================

# stop all container and remove images
if [[ "$(docker images -q paultessier/${app_name}:${tag_version} 2> /dev/null)" != "" ]]; then
    docker container stop ${app_name}-container
    docker container rm ${app_name}-container
    docker image rm -f ${app_name}:${tag_version}
fi

if [ $UPLOAD_API == True ]; then
    # ------ Log in to DockerHub fill username & password ------------------------------------
    docker login
    # ------ build image ---------------------------------------------------------------------
    docker build -t paultessier/${app_name}:${tag_version} ./fastapi
    # docker tag ${app_name}:${tag_version} paultessier/${app_name}:${tag_version}
    # ------ push and remove image locally ---------------------------------------------------
    docker image push paultessier/${app_name}:${tag_version}
    docker image rm paultessier/${app_name}:${tag_version}
    # ------ Log out from DockerHub ----------------------------------------------------------
    docker logout

fi

# TEST
# docker run -it -d --rm --name ${app_name} -p ${port}:8000 paultessier/${app_name}:${tag_version}

# ==========================================================================================
# ========= TESTS IMAGES ===================================================================
# ==========================================================================================

# ------ delete containers and images relative to tests ------------------------------------

# docker container stop test-curl-container test-py-container
# docker container rm test-curl-container test-py-container
# docker image rm -f ${app_name}:curl_test ${app_name}:py_test

if [[ "$(docker images -q ${app_name}:curl_test 2> /dev/null)" != "" ]]; then
    docker container stop test-curl-container
    docker container rm test-curl-container
    docker image rm -f ${app_name}:curl_test
fi
if [[ "$(docker images -q ${app_name}:py_test 2> /dev/null)" != "" ]]; then
    docker container stop py-curl-container
    docker container rm py-curl-container
    docker image rm -f ${app_name}:py_test
fi

# rebuild docker images
docker build -t ${app_name}:curl_test ./tests/curl
docker build -t ${app_name}:py_test ./tests/python


# TEST TO LAUNCH CONTAINERS
# docker run -it -d --rm --name test-curl-container -v ${PWD}/data:/app/data -v ${PWD}/log:/app/log ${app_name}:curl_test
# docker run -it -d --rm --name test-py-container -v ${PWD}/data:/app/data -v ${PWD}/log:/app/log ${app_name}:py_test

# TEST CURL
# chmod 700 ./tests/curl/test_api.sh
# ./tests/curl/test_api.sh

# TEST PYTHON
# pip3 install -r ./tests/python/requirements.txt
# python3 ./tests/python/test_api.py 


# ==========================================================================================
# ========= DOCKER COMPOSE =================================================================
# ==========================================================================================

docker-compose up