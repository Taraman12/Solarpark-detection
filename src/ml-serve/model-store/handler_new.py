# https://pytorch.org/serve/custom_service.html
import os
import logging
from pathlib import Path
import yaml
import segmentation_models_pytorch as smp


class ModelHandler(object):
    """
    A custom model handler implementation.
    """

    def __init__(self):
        self._context = None
        self.initialized = False
        self.model = None
        self.device = None

    def initialize(self, context):
        """
        Invoke by torchserve for loading a model
        :param context: context contains model server system properties
        :return:
        """
        logger = logging.getLogger("ts_log")
        logger.setLevel(logging.INFO)
        logger.warning("initialize...")
        logging.info("initialize...")
        #  load the model
        self.manifest = context.manifest

        properties = context.system_properties
        model_dir = properties.get("model_dir")
        print("model_dir: ", model_dir)
        self.device = "cpu"
        # self.device = torch.device("cuda:" + str(properties.get("gpu_id")) if torch.cuda.is_available() else "cpu")

        # Read model serialize/pt file
        serialized_file = self.manifest["model"]["serializedFile"]
        # model_pt_path = os.path.join(model_dir, serialized_file)
        # model_pt_path = Path(r"/app/model-store/eff_b0.pth")
        if not os.path.isfile("eff_b0.pth"):
            raise RuntimeError("Missing the model.pt file")

        # model_config_path = r"/app/model-store/model-config.yaml"

        with open("model-config.yaml", "r") as f:
            model_config = yaml.safe_load(f)

        # self.model = torch.jit.load(model_pt_path)
        self.model = smp.Unet(
            encoder_name=model_config["encoder_name"],
            encoder_weights=model_config["encoder_weights"],
            in_channels=model_config["in_channels"],
            classes=model_config["classes"],
            activation=model_config["activation"],
        )
        logger.info("Model initialized!")
        self.initialized = True

    def handle(self, data, context):
        """
        Invoke by TorchServe for prediction request.
        Do pre-processing of data, prediction using model and postprocessing of prediciton output
        :param data: Input data for prediction
        :param context: Initial context contains model server system properties.
        :return: prediction output
        """
        pred_out = self.model.forward(data)
        return pred_out
