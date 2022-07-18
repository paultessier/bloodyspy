app_name=bloodyspy
version=1.0.0
port=8000

# docker container run -it -d\
#  --name ${app_name}\
#  -p ${port}:8000
#  --volume ./data_sample:/app/data_sample\
#  --volume ./data_unlabelled:/app/data_unlabelled\
#  --rm\
#  ${app_name}:${version}
docker login

docker container run -it -d --rm\
 --name ${app_name}\
 -p ${port}:8000\
 --volume ${PWD}/data_sample:/app/data_sample\
 paultessier/${app_name}:${version}

 
