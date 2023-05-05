### Notes on ml-serve
https://github.com/pytorch/serve/blob/master/docs/getting_started.md
cli:  
https://github.com/pytorch/serve/blob/master/model-archiver/README.md

install model-archiver first if torch-model-archiver is not in path variable:
https://pypi.org/project/model-archiver/

cli:
torch-model-archiver --model-name test_model \
                     --version 1.0 \
                     --serialized-file model/eff_b0.pth \
                     --handler handler.py \
                     --extra-files model/model-config.yaml

cli docs: https://pytorch.org/serve/server.html#command-line-interface
torchserve --start \
           --ncs \
           --ts-config config.properties \
           --model-store model \
           --models test_model.mar