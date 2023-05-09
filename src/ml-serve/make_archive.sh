#!/bin/bash
# https://github.com/pytorch/serve/blob/master/model-archiver/README.md

torch-model-archiver --model-name test_model \
                     --version 1.0 \
                     --serialized-file ml-serve/model-store/eff_b0.pth \
                     --handler ml-serve/model-store/handler_new.py \
                     --extra-files ml-serve//model-store/model-config.yaml \
                     --requirements-file ml-serve/requirements.txt \
                     --export-path ml-serve/model-store \
                     --force
                    # BUG mentioned in the docs but doesn't work 
                    # --config-file ml-serve/app/model-store/model-config.yaml
