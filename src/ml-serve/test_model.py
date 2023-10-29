import numpy as np
import segmentation_models_pytorch as smp
import torch
import yaml

# from ..config import INPUT_SHAPE, OUTPUT_SHAPE

MODEL_PATH = "model-store/resnest14d_best_model.pt"


def test_load_model_with_config():
    """Test that the config file is loaded."""
    with open("model-store/model-config.yaml", "r") as f:
        model_config = yaml.safe_load(f)
    # check if keys are in the config file
    assert "encoder_name" in model_config.keys()
    assert "encoder_weights" in model_config.keys()
    assert "in_channels" in model_config.keys()
    assert "classes" in model_config.keys()
    assert "activation" in model_config.keys()
    model = smp.Unet(
        encoder_name=model_config["encoder_name"],
        encoder_weights=model_config["encoder_weights"],
        in_channels=model_config["in_channels"],
        classes=model_config["classes"],
        activation=model_config["activation"],
    )
    model.load_state_dict(torch.load(MODEL_PATH, map_location="cpu"))
    model.eval()
    assert model is not None


def test_model_dimensions():
    """Test that the model has the correct dimensions."""
    with open("model-store/model-config.yaml", "r") as f:
        model_config = yaml.safe_load(f)
    # check if keys are in the config file
    assert "encoder_name" in model_config.keys()
    assert "encoder_weights" in model_config.keys()
    assert "in_channels" in model_config.keys()
    assert "classes" in model_config.keys()
    assert "activation" in model_config.keys()
    model = smp.Unet(
        encoder_name=model_config["encoder_name"],
        encoder_weights=model_config["encoder_weights"],
        in_channels=model_config["in_channels"],
        classes=model_config["classes"],
        activation=model_config["activation"],
    )
    model.load_state_dict(torch.load(MODEL_PATH, map_location="cpu"))
    model.eval()
    input_tensor = torch.randn(1, 4, 256, 256)
    output = model(input_tensor)
    assert output.shape == (1, 1, 256, 256)


def test_model_prediction_with_solarpark():
    """Test that the model makes a prediction."""
    with open("model-store/model-config.yaml", "r") as f:
        model_config = yaml.safe_load(f)
    # check if keys are in the config file
    model = smp.Unet(
        encoder_name=model_config["encoder_name"],
        encoder_weights=model_config["encoder_weights"],
        in_channels=model_config["in_channels"],
        classes=model_config["classes"],
        activation=model_config["activation"],
    )
    model.load_state_dict(torch.load(MODEL_PATH, map_location="cpu"))
    model.eval()
    image = torch.load(
        r"C:\Users\Fabian\Documents\Github_Masterthesis\Solarpark-detection\data_local\data_splitted_undersampling_cleaned\train\images\32UNA_1598_2018-9-27.pt"
    )
    pred = model(image.unsqueeze(0))
    pred = pred.detach().numpy()  # ! .squeeze()
    mask = np.where(pred[0] < 0.5, 0, 1)
    assert mask.sum() > 0


def test_model_prediction_no_solarpark():
    """Test that the model makes a prediction."""
    with open("model-store/model-config.yaml", "r") as f:
        model_config = yaml.safe_load(f)
    # check if keys are in the config file
    model = smp.Unet(
        encoder_name=model_config["encoder_name"],
        encoder_weights=model_config["encoder_weights"],
        in_channels=model_config["in_channels"],
        classes=model_config["classes"],
        activation=model_config["activation"],
    )
    model.load_state_dict(torch.load(MODEL_PATH, map_location="cpu"))
    model.eval()
    image = torch.load(
        r"C:\Users\Fabian\Documents\Github_Masterthesis\Solarpark-detection\data_local\data_splitted_undersampling_cleaned\val\images\32UPU_598_2018-4-7.pt"
    )
    pred = model(image.unsqueeze(0))
    pred = pred.squeeze().detach().numpy()
    print(pred.shape)
    mask = np.where(pred[0] < 0.5, 0, 1)
    assert mask.sum() == 0
    # load image with no solar panels
    # C:\Users\Fabian\Documents\Github_Masterthesis\Solarpark-detection\data_local\data_splitted_undersampling_cleaned\upload
    # C:\Users\Fabian\Documents\Github_Masterthesis\Solarpark-detection\data_local\data_splitted_undersampling_cleaned\val\images
    # 32UPU_598_2018-4-7.tif
    # 32UPU_598_2018-7-31.tif
    # solarpark
    # 32UNA_1598_2018-9-27.tif
