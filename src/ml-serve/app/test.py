# test
import yaml
import os

with open (r"src/ml-serve/app/model/model-config.yaml", "r") as f:
    model_config = yaml.safe_load(f)

print(model_config["encoder_name"])

