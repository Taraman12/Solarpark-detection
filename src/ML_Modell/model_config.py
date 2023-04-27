# use dataclasses for config
# or use hydra for config

MODEL_CONFIG_EFF_B0 = dict(
    encoder_name="timm-efficientnet-b0",
    encoder_weights="imagenet",
    epochs=2,
    batch_size=32,
    max_lr=0.1,
    in_channels=4,  # model input channels (3 for RGB, etc.)
    classes=1,  # model output channels (number of classes in your dataset)
    activation="sigmoid",
    num_workers=0,
    shuffle=True,
    optimizer="Adam",
    scheduler="OneCycleLR",
    loss="DiceLoss_Scheduler",
    config_name="eff_b0",
    comment="log_loss=True_from_logits=True",
)

MODEL_CONFIG_DEFAULT = dict(
    encoder_name="resnet18",
    encoder_weights="imagenet",
    epochs=30,
    batch_size=32,
    max_lr=0.1,
    in_channels=3,
    classes=1,
    activation="sigmoid",
    num_workers=0,
    shuffle=True,
    optimizer="Adam",
    scheduler=None,
    loss="DiceLoss",
    config_name="default",
    comment="default",
)

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
