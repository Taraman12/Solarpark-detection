# import torchserve
# import torch_model_archiver
# import os
import json
import os


def lambda_handler(event, context):
    # Laden Sie das Modell und starten Sie den TorchServe-Server
    # os.system("torchserve --start --model-store /tmp/models --models solar-park-detection.mar")
    os.system(
        "torchserve --start --ncs --model-store /model-store --models solar-park-detection=solar-park-detection.mar"
    )
    return {"statusCode": 200, "body": "TorchServe started."}


# def lambda_handler(event, context):
#     message = "Hello {}!".format(event["first_name"])
#     return {"message": message}
