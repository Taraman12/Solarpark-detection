# build-in
import gc
import logging
from pathlib import Path

# third-party
import torch

# local modules
from Trainer_S2_Unet import TrainerS2Unet

# use hydra for config
ENCODER_NAMES = [
    "resnet18",
    "timm-resnest14d",
    "vgg16",
]  # 'resnet18', 'resnet34','resnext50_32x4d', 'timm-resnest14d',
ENCODER_WEIGHTS = ["imagenet", None]
ACTIVATIONS = ["sigmoid", None]

model_settings_eff_b2 = {
    "encoder_name": "efficientnet-b0",
    "encoder_weights": "imagenet",
    "activation": "sigmoid",
}

model_settings1 = {
    "encoder_name": "timm-resnest14d",
    "encoder_weights": "imagenet",
    "activation": "sigmoid",
}
model_settings2 = {
    "encoder_name": "vgg16",
    "encoder_weights": "imagenet",
    "activation": "sigmoid",
}


settings = [model_settings_eff_b2]

root_dir = Path(__file__).resolve().parent.parent.parent


def main():
    # for encoder_name in ENCODER_NAMES:
    #     for encoder_weight in ENCODER_WEIGHTS:
    #         for activation in ACTIVATIONS:
    for model_settings in settings:
        model_settings = {
            "encoder_name": model_settings["encoder_name"],
            "encoder_weights": model_settings["encoder_weights"],
            "activation": model_settings["activation"],
        }

        model_config = (
            f"{model_settings['encoder_name']}_"
            f"{model_settings['encoder_weights']}_"
            f"{model_settings['activation']}"
        )
        # logging.warning(f"Training model with settings: {model_config}")
        # set up the training
        try:
            trainer = TrainerS2Unet(
                image_dir=root_dir / "data_local/images_only_AOI4",
                mask_dir=root_dir / "data_local/masks_only_AOI4",
                epochs=160,
                batch_size=32,
                shuffle=True,
                config_name=model_config,
                log_dir=root_dir / "data_local/runs",
            )
            model_dir = root_dir / "data_local/saved_models"
            trainer.train_model(model_dir=model_dir, model_settings=model_settings)
        except torch.cuda.OutOfMemoryError:
            logging.warning(f"Out of memory error for model {model_config}")
            gc.collect()
            torch.cuda.empty_cache()
            continue
        logging.info("Training finished")


if __name__ == "__main__":
    main()
