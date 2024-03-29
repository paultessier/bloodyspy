sleep 5

exec 3>&1 4>&2
trap 'exec 2>&4 1>&3' 0 1 2 3
exec 1>log/api_tests_curl.log 2>&1
# Everything below will go to the file 'log/api_tests_curl.log':

echo =====================================================================
echo "The following base 64 conversion was done for authorization header:"
# echo Authorization: Basic $(echo root:root_password | base64)
echo Authorization: Basic $(printf '%s' "root:root_password" | base64)
# echo Authorization: Basic $(echo alice:wonderland | base64)
echo Authorization: Basic $(printf '%s' "alice:wonderland" | base64)
# echo Authorization: Basic $(echo paul:hello_pwd | base64)
echo Authorization: Basic $(printf '%s' "paul:hello_pwd" | base64)
echo =====================================================================

echo " "
echo " "
echo "===================================================================================="
echo "   TEST 1: STATUS"
echo "===================================================================================="
curl -X GET -i http://${API_CONTAINER_NAME}:8000/bloodyspy/status

echo " "
echo " "
echo "===================================================================================="
echo "   TEST 1 BIS: STATUS AUTHORIZED"
echo "===================================================================================="
curl -X GET \
  http://${API_CONTAINER_NAME}:8000/bloodyspy/authorization \
  -H 'Authorization: Basic YWxpY2U6d29uZGVybGFuZA==' \

echo " "
echo " "
echo "===================================================================================="
echo "   TEST 2: GET CELL BLOOD TYPE FOR 1 IMAGE"
echo "===================================================================================="
curl -X 'POST' \
  http://${API_CONTAINER_NAME}:8000/bloodyspy/image \
  -H 'accept: application/json' \
  -H 'Authorization: Basic cm9vdDpyb290X3Bhc3N3b3Jk' \
  -H 'Content-Type: multipart/form-data' \
  -F 'file=@data/unlabelled/10030044131_188.jpg;type=image/jpeg'


echo " "
echo " "
echo "===================================================================================="
echo "   TEST 2 BIS: SUBMIT A TEXT FILE -> ERROR EXPECTED"
echo "===================================================================================="
curl -X 'POST' \
  http://${API_CONTAINER_NAME}:8000/bloodyspy/image \
  -H 'accept: application/json' \
  -H 'Authorization: Basic cGF1bDpoZWxsb19wd2Q=' \
  -H 'Content-Type: multipart/form-data' \
  -F 'file=@data/unlabelled/text_file.txt;type=text/plain'


echo " "
echo " "
echo "===================================================================================="
echo "   TEST 3: GET CELL BLOOD TYPE FOR SEVERAL IMAGES"
echo "===================================================================================="
curl -X 'POST' \
  http://${API_CONTAINER_NAME}:8000/bloodyspy/images \
  -H 'accept: application/json' \
  -H 'Authorization: Basic YWxpY2U6d29uZGVybGFuZA==' \
  -H 'Content-Type: multipart/form-data' \
  -F 'files=@data/unlabelled/10030044131_254.jpg;type=image/jpeg' \
  -F 'files=@data/unlabelled/10028001812_147.jpg;type=image/jpeg' \
  -F 'files=@data/unlabelled/10028001812_201.jpg;type=image/jpeg'


echo " "
echo " "
echo "===================================================================================="
echo "   TEST 3 BIS: SUBMIT SEVERAL FILES WHOSE 1 TEXT FILE -> ERROR EXPECTED FOR THIS FILE"
echo "===================================================================================="
curl -X 'POST' \
  http://${API_CONTAINER_NAME}:8000/bloodyspy/images \
  -H 'accept: application/json' \
  -H 'Authorization: Basic YWxpY2U6d29uZGVybGFuZA==' \
  -H 'Content-Type: multipart/form-data' \
  -F 'files=@data/unlabelled/text_file.txt;type=text/plain' \
  -F 'files=@data/unlabelled/monocyt.jpg;type=image/jpeg'

echo " "
echo " "