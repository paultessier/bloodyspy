echo "================================================="
echo TEST1: STATUS
echo "================================================="
curl -X GET -i 'http://127.0.0.1:8000/api/status'

echo " "
echo "================================================="
echo TEST2: UPLOAD FILE
echo "================================================="
curl -X 'POST' \
  'http://localhost:8000/uploadfile/' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'file=@data_unlabelled/10030044131_188.jpg;type=image/jpeg'

echo " "
echo "================================================="
echo TEST3: FILE
echo "================================================="
  curl -X 'POST' \
  'http://localhost:8000/files/' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'file=@data_unlabelled/10028001812_206.jpg;type=image/jpeg'