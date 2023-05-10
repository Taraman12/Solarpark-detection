#!/bin/bash
# https://github.com/pytorch/serve/blob/master/model-archiver/README.md

torch-model-archiver --model-name test_model \
                     --version 1.0 \
                     --serialized-file model-store/eff_b0.pth \
                     --handler model-store/handler.py \
                     --extra-files model-store/model-config.yaml \
                     --requirements-file requirements.txt \
                     --export-path model-store \
                     --force
                    # Will be available at torchserve version 0.8.0 (current 0.7.1)
                    # --config-file ml-serve/app/model-store/model-config.yaml
