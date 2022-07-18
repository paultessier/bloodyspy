app_name=bloodyspy
version=1.0.0

# LOGIN TO DOCKER HUB and fill username & password
echo " "
echo login to docker .....
docker login

# UPLOAD IMAGE
docker tag ${app_name}:${version} paultessier/${app_name}:${version}
docker image push paultessier/${app_name}:${version}

# LOGOUT FROM DOCKER HUB
docker logout

# TEST
echo ==== TEST
docker image rm paultessier/${app_name}:${version}
docker run -it -d --name ${app_name} -p ${port}:8000 paultessier/${app_name}:${version}

