#!/bin/bash
# https://github.com/pytorch/serve/blob/master/model-archiver/README.md


torch-model-archiver --model-name solar-park-detection \
                     --version 1.0 \
                     --serialized-file model-store/resnest14d_best_model.pt \
                     --handler model-store/handler.py \
                     --extra-files model-store/model-config.yaml \
                     --requirements-file requirements.txt \
                     --export-path model-store \
                     --force
                    # should be available in torchserve 0.8.0
                    # --config-file ml-serve/app/model-store/model-config.yaml
