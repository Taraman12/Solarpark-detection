### Notes on ml-serve
https://github.com/pytorch/serve/blob/master/docs/getting_started.md
cli:  
https://github.com/pytorch/serve/blob/master/model-archiver/README.md

install model-archiver first if torch-model-archiver is not in path variable:
https://pypi.org/project/model-archiver/

cli:
torch-model-archiver --model-name test_model --version 1.0 --serialized-file app/model-store/eff_b0.pth --handler app/handler.py --extra-files app/model-store/model-config.yaml
                     --extra-files requirements.txt

cli docs: https://pytorch.org/serve/server.html#command-line-interface
torchserve --start \
           --ncs \
           --ts-config config.properties \
           --model-store model \
           --models test_model.mar

File build_image.sh from:
https://github.com/pytorch/serve/tree/master/docker

docker run --rm --name torchserve_docker \
           -p8080:8080 -p8081:8081 -p8082:8082 \
           ubuntu-torchserve:latest \
           torchserve --model-store /home/model-server/model-store/ --models foodnet=foodnet_resnet18.mar

docker run --rm --name torchserve_docker \
-p8080:8080 -p8081:8081 -p8082:8082 \
pytorch/torchserve:0.1.1-cpu \
torchserve --model-store model --models solarDetection=test_model.mar

Management API:
https://pytorch.org/serve/management_api.html#list-models

check if model is loaded:
curl "http://localhost:8081/models"

#### make .mar file
##### run this in (git) bash shell (from ml-serve folder)
./make-archive.sh