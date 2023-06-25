import logging
import os
from typing import Any

import boto3
import numpy as np
import segmentation_models_pytorch as smp
import torch
import yaml
from ts.torch_handler.base_handler import BaseHandler

"""
ToDo: use jit to load the model instead on state_dict
Needs be be saved as a script model first
https://pytorch.org/tutorials/advanced/cpp_export.html
https://stackoverflow.com/questions/42703500/how-do-i-save-a-trained-model-in-pytorch
https://github.com/pytorch/serve/blob/master/ts/torch_handler/base_handler.py
"""

logger = logging.getLogger("model_log")
logger.setLevel(logging.INFO)


class ModelHandler(BaseHandler):
    """A custom model handler implementation."""

    def __init__(self) -> None:
        # super().__init__()
        self._context = None
        self.initialized = False
        self.explain = False
        self.target = 0

    def initialize(self, context: Any) -> None:
        """Initialize model.

        This will be called during model loading time
        :param context: Initial context contains model server system properties. (config.properties file)
        :return:
        """
        self._context = context
        logging.info("initialize...")
        self.manifest = context.manifest

        properties = context.system_properties  # noqa: F841
        # model_dir = properties.get("model_dir")

        self.device = (
            "cuda"
            if torch.cuda.is_available()
            else "mps"
            if torch.backends.mps.is_available()
            else "cpu"
        )
        if not os.path.isfile("eff_b0.pth"):
            raise RuntimeError("Missing the model.pt file")

        # model_config_path = r"/app/model-store/model-config.yaml"
        if PRODUCTION:
            s3 = boto3.client("s3")
            s3.download_file(
                "sagemaker-us-east-1-123456789012",
                "model-config.yaml",
                "model-config.yaml",
            )

        with open("model-config.yaml", "r") as f:
            model_config = yaml.safe_load(f)

        # https://pytorch.org/serve/custom_service.html
        # NOTE there are two ways to load the model
        # 1. load the model using torch.load
        # self.model = torch.jit.load(model_pt_path)
        # 2. load the model using load_state_dict
        # load the model, refer 'custom handler class' above for details
        self.model = smp.Unet(
            encoder_name=model_config["encoder_name"],
            encoder_weights=model_config["encoder_weights"],
            in_channels=model_config["in_channels"],
            classes=model_config["classes"],
            activation=model_config["activation"],
        )
        # load pretrained model
        self.model.load_state_dict(torch.load("eff_b0.pth", map_location=self.device))
        # set model to eval mode
        self.model.eval()
        logger.info("Model initialized!")
        self.initialized = True

    def preprocess(self, data: Any) -> Any:
        """Transform raw input into model input data.

        :param batch: list of raw requests, should match batch size
        :return: list of preprocessed model input data
        """
        # Take the input data and make it inference ready
        preprocessed_data = data[0].get("data")
        if preprocessed_data is None:
            preprocessed_data = data[0].get("body")
        # list to numpy array
        numpy_data = np.array(preprocessed_data)
        # tensor_data = torch.as_tensor(numpy_data, device=self.device)
        tensor_data = torch.as_tensor(numpy_data, device=self.device).float()

        return tensor_data

    def inference(self, model_input: Any) -> Any:
        """
        Internal inference methods
        :param model_input: transformed model input data
        :return: list of inference output in NDArray
        """
        # Do some inference call to engine here and return output
        model_output = self.model.forward(model_input.unsqueeze(0))
        logger.debug(f"model_output shape: {model_output.shape}")
        return model_output

    def postprocess(self, inference_output: Any) -> Any:
        """Return inference result.

        :param inference_output: list of inference output
        :return: list of predict results
        """
        # Take output from network and post-process to desired format
        postprocess_output = inference_output.tolist()
        logger.debug(f"postprocess_output type: {type(postprocess_output)}")
        return postprocess_output

    def handle(self, data: Any, context: Any) -> Any:
        """Invoke by TorchServe for prediction request.

        Do pre-processing of data, prediction using model and postprocessing of prediciton output
        :param data: Input data for prediction
        :param context: Initial context contains model server system properties.
        :return: prediction output
        """
        # model_input = self.preprocess(data)
        model_input = self.preprocess(data)
        model_output = self.inference(model_input)
        return self.postprocess(model_output)
