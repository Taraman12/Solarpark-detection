# build-in
import csv
import logging

# import os
from pathlib import Path
from typing import Any, Optional, Union

# third-party
import segmentation_models_pytorch as smp
import torch
import torch.nn as nn

# local modules
from dataset_class import GeoImageDataset
from torch.optim import Adam
from torch.optim.lr_scheduler import OneCycleLR
from torch.utils.data import DataLoader, random_split
from torch.utils.tensorboard import SummaryWriter
from torchmetrics.classification import BinaryJaccardIndex


class TrainerS2Unet:
    def __init__(
        self,
        image_dir: Path,
        mask_dir: Path,
        model_settings: dict,
        log_dir: Path = Path(""),
    ) -> None:
        self.model_settings = model_settings
        self.encoder_name = model_settings["encoder_name"]
        self.encoder_weights = model_settings["encoder_weights"]
        self.epochs = model_settings["epochs"]
        self.batch_size = model_settings["batch_size"]
        self.max_lr = model_settings["max_lr"]
        self.in_channels = model_settings["in_channels"]
        self.classes = model_settings["classes"]
        self.activation = model_settings["activation"]
        self.num_workers = model_settings["num_workers"]
        self.shuffle = model_settings["shuffle"]
        self.loss = model_settings["loss"]
        self.config_name = model_settings["config_name"]
        self.comment = model_settings["comment"]
        self.dataset = GeoImageDataset(image_dir, mask_dir)
        self.writer = SummaryWriter(log_dir=(log_dir / self.config_name))

        self.loss_fn = smp.losses.DiceLoss(
            mode="binary", log_loss=True, from_logits=False
        )

        self.device = self._get_device()

    def train_model(
        self,
        model_dir: Path,
        pretrained_model_path: Optional[Path] = None,
    ) -> None:
        train_ds, test_ds = random_split(self.dataset, [0.8, 0.2])

        logging.info(f"Using {self.device} device")

        train_dataloader = DataLoader(
            train_ds,
            batch_size=self.batch_size,
            shuffle=self.shuffle,
            num_workers=self.num_workers,
        )

        test_dataloader = DataLoader(
            test_ds,
            batch_size=self.batch_size,
            shuffle=self.shuffle,
            num_workers=self.num_workers,
        )
        # train_dataloader, test_dataloader = DataLoader(
        #     self.dataset,
        #     batch_size=self.batch_size,
        #     # shuffle=self.shuffle,
        #     num_workers=self.num_workers,
        #     sampler=random_split(self.dataset, [0.8, 0.2]),
        # )

        model = self._load_model(pretrained_model_path=pretrained_model_path)

        optimizer = Adam(model.parameters(), lr=self.max_lr)

        scheduler = OneCycleLR(
            optimizer,
            max_lr=self.max_lr,
            steps_per_epoch=len(train_dataloader),
            epochs=self.epochs,
        )

        jaccard_idx_temp = []

        self.writer.add_text(
            "Hyperparameter", self.dict2mdtable(self.model_settings), 1
        )

        for epoch in range(self.epochs):
            # to start printing with 1
            epoch = epoch + 1
            print(f"Epoch {epoch}\n-------------------------------")

            train_loss = self.train(train_dataloader, model, optimizer)
            test_loss, jaccard_idx = self.test(test_dataloader, model)
            scheduler.step()

            jaccard_idx_temp.append(jaccard_idx)

            self.writer.add_scalar("Loss/train", train_loss, epoch)
            self.writer.add_scalar("Loss/test", test_loss, epoch)
            self.writer.add_scalar("Jaccard/test", jaccard_idx, epoch)

            if (epoch) % 10 == 0:
                torch.save(
                    model.state_dict(),
                    model_dir / f"{self.config_name}_epoch-{epoch}.pth",
                )

        torch.save(
            model.state_dict(),
            model_dir / f"{self.config_name}_epoch-{epoch}.pth",
        )
        # print(statistics.mean(jaccard_idx_temp))
        # self.write_to_csv(statistics.mean(jaccard_idx_temp[-20:]))

        self.writer.flush()
        self.writer.close()
        # print("Done!")

    def train(
        self,
        dataloader: Any,
        model: nn.Module,
        # Callable[[torch.Tensor, torch.Tensor], Union[Any, torch.Tensor]]
        optimizer: Any,
    ) -> torch.Tensor:
        size = len(dataloader.dataset)

        model.train()
        for batch, (X, y) in enumerate(dataloader):
            X, y = X.to(self.device), y.to(self.device)

            # Compute prediction error
            pred = model(X)
            loss = self.loss_fn(pred.squeeze(1), y.to(torch.float32))

            # Backpropagation
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            if batch % 10 == 0:
                loss, current = loss.item(), (batch + 1) * len(X)
                print(f"loss: {loss:>7f}  [{current:>5d}/{size:>5d}]")

        return loss

    def test(
        self,
        dataloader: Any,
        model: nn.Module,
    ) -> Union[torch.Tensor, torch.Tensor]:
        size = len(dataloader.dataset)
        num_batches = len(dataloader)
        model.eval()
        test_loss, correct = 0, 0

        metric = BinaryJaccardIndex().to(self.device)

        with torch.no_grad():
            for X, y in dataloader:
                X, y = X.to(self.device), y.to(self.device)
                pred = model(X)
                # test_loss += loss_fn(pred, y).item()
                test_loss += self.loss_fn(pred.squeeze(1), y.to(torch.float32)).item()
                loss = self.loss_fn(pred.squeeze(1), y.to(torch.float32)).item()

                # accuracy
                # correct += (pred.argmax(1) == y).type(torch.float).sum().item()

        # ToDo: fix typing
        test_loss /= num_batches  # type: ignore
        correct /= size  # type: ignore
        jaccard_idx = 100 * metric(pred.squeeze(1), y)
        print(
            f"Test Error: \n"
            f"Jaccard-Index: {(jaccard_idx):>0.3f}%, Avg loss: {test_loss:>5f} \n"
        )
        return loss, jaccard_idx.item()  # type: ignore

    def _load_model(
        self,
        pretrained_model_path: Optional[Path] = None,
    ) -> nn.Module:
        # ToDo: find better way to load default model
        model = smp.Unet(
            encoder_name=self.encoder_name,
            encoder_weights=self.encoder_weights,
            in_channels=self.in_channels,
            classes=self.classes,
            activation=self.activation,
        ).to(self.device)

        if pretrained_model_path is not None:
            model.load_state_dict(torch.load(pretrained_model_path))

        return model

    def _write_to_csv(self, avg_jaccard_idx: float) -> None:
        csv_path = r"C:\Users\Fabian\Documents\Masterarbeit_Daten\jaccard_idx.csv"
        # Öffne die CSV-Datei zum Lesen
        with open(csv_path, mode="r") as csv_file:
            # Lese die CSV-Datei ein und speichere die Daten als Liste von Dictionaries
            csv_reader = csv.DictReader(csv_file)
            data = [row for row in csv_reader]

        # Hänge neue Daten an die vorhandenen Daten an
        new_data = [
            {"Config_name": self.config_name, "avg_jaccard_idx": avg_jaccard_idx},
        ]
        data += new_data

        # Öffne die CSV-Datei zum Schreiben und schreibe die Daten zurück in die Datei
        with open(csv_path, mode="w", newline="") as csv_file:
            fieldnames = ["Config_name", "avg_jaccard_idx"]  # Die Spaltennamen
            csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

            # Schreibe die Spaltennamen in die Datei
            csv_writer.writeheader()

            # Schreibe die Daten in die Datei
            for row in data:
                csv_writer.writerow(row)

    def _get_device(self) -> str:
        if torch.cuda.is_available():
            return "cuda"
        elif torch.backends.mps.is_available():
            return "mps"
        else:
            return "cpu"

    def dict2mdtable(self, d: dict, key: str = "Name", val: str = "Value") -> str:
        rows = [f"| {key} | {val} |"]
        rows += ["|--|--|"]
        rows += [f"| {k} | {v} |" for k, v in d.items()]
        return "  \n".join(rows)

    def checkpoints(self) -> None:
        pass
