# custom handler file
# source:
# https://medium.com/@SrGrace_/a-practical-guide-to-torchserve-197ec913bbd
# model_handler.py

"""
ModelHandler defines a custom model handler
"""
import os
import yaml
from pathlib import Path
from typing import Optional
import segmentation_models_pytorch as smp
from ts.torch_handler.base_handler import BaseHandler


class ModelHandler(BaseHandler):
    """
    A custom model handler implementation.
    """

    def __init__(self) -> None:
        # self._context = configparser.ConfigParser()
        self.initialized = False

    def initialize(self) -> None:
        """
        Initialize model. This will be called during model loading time
        :param context: Initial context contains model server system properties.
        :return:
        """
        # self._context = context
        # self.manifest = context.manifest
        # properties = context.system_properties
        model_dir = Path(r"src/ml-serve/app/model")  # context.get('model_dir')

        model_file_path = model_dir / "eff_b0.pth"
        model_config_path = model_dir / "model-config.yaml"

        with open(r"src/ml-serve/app/model/model-config.yaml", "r") as f:
            model_config = yaml.safe_load(f)

        # defining and loading smp model
        self.model = smp.Unet(
            encoder_name=model_config["encoder_name"],
            encoder_weights=model_config["encoder_weights"],
            in_channels=model_config["in_channels"],
            classes=model_config["classes"],
            activation=model_config["activation"],
        )  # .to(self.device)

        self.initialized = True

    def preprocess(self, data):
        """
        Transform raw input into model input data.
        :param batch: list of raw requests, should match batch size
        :return: list of preprocessed model input data
        """
        # Take the input data and make it inference ready
        preprocessed_data = data[0].get("data")
        if preprocessed_data is None:
            preprocessed_data = data[0].get("body")

        return preprocessed_data

    def inference(self, model_input):
        """
        Internal inference methods
        :param model_input: transformed model input data
        :return: list of inference output in NDArray
        """
        # Do some inference call to engine here and return output
        model_output = self.model.detect(model_input)
        return model_output

    def postprocess(self, inference_output):
        """
        Return inference result.
        :param inference_output: list of inference output
        :return: list of predict results
        """
        # Take output from network and post-process to desired format
        postprocess_output = inference_output
        return postprocess_output

    def handle(self, data, context):
        """
        Invoke by TorchServe for prediction request.
        Do pre-processing of data, prediction using model and postprocessing of prediction output
        :param data: Input data for prediction
        :param context: Initial context contains model server system properties.
        :return: prediction output
        """
        if not self.initialized:
            self.initialized()

        model_input = self.preprocess(data)
        model_output = self.inference(model_input)
        return self.postprocess(model_output)
