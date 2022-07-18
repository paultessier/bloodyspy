version=v1
# chmod 700 ./setup.sh
zip zip/project_bloodyspy_Paul_Tessier_${version}.zip\
 ./docker-compose.yml\
 -r ./data_unlabelled\
 -r ./data_sample\
 -r ./resources/imgs\
 ./README.md\
 ./tests.sh

