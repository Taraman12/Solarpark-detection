# build-in
import gc
import logging
from pathlib import Path

# third-party
import torch
from torch.cuda import OutOfMemoryError


# local modules
import model_config as config
from Trainer_S2_Unet import TrainerS2Unet

"""
ToDo: Add save model with the highest IoU
"""

settings = [config.MODEL_CONFIG_EFF_B0]

root_dir = Path(__file__).resolve().parent.parent.parent

# pretrained_model_path = root_dir / "data_local/saved_models/timm-efficientnet-b0_imagenet_sigmoid_epoch-60.pth"

pretrained_model_path = None


def main() -> None:
    for model_settings in settings:
        config_name = model_settings["config_name"]
        model_dir = root_dir / "data_local/saved_models"
        logging.info(
            f"Training model with settings: {config_name}"
            f"and pretrained model: {pretrained_model_path}"
        )

        trainer = TrainerS2Unet(
            image_dir=root_dir / "data_local/images_only_AOI_all_seasons",
            mask_dir=root_dir / "data_local/masks_only_AOI_all_seasons",
            model_settings=model_settings,
            log_dir=root_dir / "data_local/runs",
        )

        try:
            trainer.train_model(model_dir=model_dir)

        # ToDo: fix typing
        except OutOfMemoryError:  # type: ignore
            logging.warning(f"Out of memory error for model {config_name}")
            gc.collect()
            torch.cuda.empty_cache()
            continue
        logging.info("Training finished")


if __name__ == "__main__":
    main()
