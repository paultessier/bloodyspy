version=v_final

rm zip/project_bloodyspy_Paul_Tessier_${version}.zip

zip zip/project_bloodyspy_Paul_Tessier_${version}.zip\
 -r ./data\
 -r ./resources/imgs\
 -r ./tests\
 -r .fastapi\
 -r ./log\
 ./docker-compose.yml\
 ./main.sh\
 ./README.md

