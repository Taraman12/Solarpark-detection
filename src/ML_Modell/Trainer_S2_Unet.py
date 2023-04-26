# build-in
import csv
import logging
import os

# third-party
import segmentation_models_pytorch as smp
import torch

# local modules
from dataset_class import GeoImageDataset
from torch.utils.data import DataLoader
from torch.utils.tensorboard import SummaryWriter
from torchmetrics.classification import BinaryJaccardIndex


class TrainerS2Unet:
    def __init__(
        self,
        image_dir: str,
        mask_dir: str,
        epochs: int=30,
        batch_size: int=32,
        shuffle: bool=True,
        config_name: str="",
        log_dir: str="",
    ) -> None:
        self.dataset = GeoImageDataset(image_dir, mask_dir)
        self.epochs = epochs
        self.batch_size = batch_size
        self.shuffle = shuffle
        self.writer = SummaryWriter(log_dir=os.path.join(log_dir, config_name))
        self.config_name = config_name
        self.device = (
            "cuda"
            if torch.cuda.is_available()
            else "mps"
            if torch.backends.mps.is_available()
            else "cpu"
        )

    def train_model(self, model_dir, pretrained_model_path=None, model_settings=None):
        train_ds, test_ds = torch.utils.data.random_split(self.dataset, [0.8, 0.2])

        logging.info(f"Using {self.device} device")

        train_dataloader = DataLoader(
            train_ds, batch_size=self.batch_size, shuffle=self.shuffle, num_workers=1
        )

        test_dataloader = DataLoader(
            test_ds, batch_size=self.batch_size, shuffle=self.shuffle, num_workers=1
        )

        model = self._load_model(model_settings=model_settings)

        loss_fn = smp.losses.DiceLoss(mode="binary", log_loss=True, from_logits=False)

        # metrics = [smp.utils.metrics.IoU(threshold=0.5)]
        
        # check different optimizer
        optimizer = torch.optim.SGD(model.parameters(), lr=0.0005, momentum=0.9)
        # ? Check for different max_lr (0.01)
        # ! should be implemented
        # scheduler = torch.optim.lr_scheduler.OneCycleLR(
        #     optimizer,
        #     max_lr=0.1,
        #     steps_per_epoch=len(train_dataloader),
        #     epochs=self.epochs,
        # )

        jaccard_idx_temp = []
        for epoch in range(self.epochs):
            # print(f"Epoch {epoch+1}\n-------------------------------")
            train_loss = self.train(train_dataloader, model, loss_fn, optimizer)
            self.writer.add_scalar("Loss/train", train_loss, epoch)
            test_loss, jaccard_idx = self.test(test_dataloader, model, loss_fn)
            self.writer.add_scalar("Loss/test", test_loss, epoch)
            self.writer.add_scalar("Jaccard/test", jaccard_idx, epoch)
            jaccard_idx_temp.append(jaccard_idx)
            if (epoch + 1) % 60 == 0:
                torch.save(
                    model.state_dict(),
                    os.path.join(
                        model_dir, f"{self.config_name}_epoch-{epoch + 1}.pth"
                    ),
                )

        torch.save(
            model.state_dict(),
            os.path.join(model_dir, f"{self.config_name}_epoch-{epoch + 1}.pth"),
        )
        # print(statistics.mean(jaccard_idx_temp))
        # self.write_to_csv(statistics.mean(jaccard_idx_temp[-20:]))

        self.writer.flush()
        self.writer.close()
        # print("Done!")

    # def _load_data(self):
    #     self.dataloader = DataLoader(
    #         self.dataset,
    #         batch_size=self.batch_size,
    #         shuffle=self.shuffle,
    #         num_workers=4,
    #         pin_memory=True,
    #     )
    #     return self.dataloader
    def write_to_csv(self, avg_jaccard_idx):
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

    def _load_model(self, pretrained_model_path=None, model_settings=None):
        # ToDo: find better way to load default model
        # select Unet with resnet34 as backbone
        model = smp.Unet(
            encoder_name="resnet34",  # choose encoder,
            # encoder_weights="imagenet", # pre-trained weights for encoder
            in_channels=4,  # model input channels (3 for RGB, etc.)
            classes=1,  # model output channels (number of classes in your dataset)
            # activation="sigmoid",
        ).to(self.device)

        if pretrained_model_path is not None:
            # model_dir = os.path.join(os.getcwd(), "models")
            model = model.load_state_dict(torch.load(pretrained_model_path))

        elif model_settings is not None:
            print(f'Using model settings: {model_settings["encoder_name"]}')
            model = smp.Unet(
                encoder_name=model_settings["encoder_name"],  # choose encoder
                encoder_weights=model_settings[
                    "encoder_weights"
                ],  # use `imagenet` pre-trained weights for encoder initialization
                in_channels=4,  # model input channels (3 for RGB, etc.)
                classes=1,  # model output channels (number of classes in your dataset)
                activation=model_settings["activation"],
            ).to(self.device)

        else:
            logging.info("No model settings provided. Using default model settings.")

        return model

    def train(self, dataloader, model, loss_fn, optimizer):
        size = len(dataloader.dataset)
        model.train()
        for batch, (X, y) in enumerate(dataloader):
            X, y = X.to(self.device), y.to(self.device)

            # Compute prediction error
            pred = model(X)
            # loss = loss_fn(pred, y)
            loss = loss_fn(pred.squeeze(1), y.to(torch.float32))

            # Backpropagation
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            if batch % 100 == 0:
                loss, current = loss.item(), (batch + 1) * len(X)
                print(f"loss: {loss:>7f}  [{current:>5d}/{size:>5d}]")
            return loss

    def test(self, dataloader, model, loss_fn):
        size = len(dataloader.dataset)
        num_batches = len(dataloader)
        model.eval()
        test_loss, correct = 0, 0
        with torch.no_grad():
            for X, y in dataloader:
                X, y = X.to(self.device), y.to(self.device)
                pred = model(X)
                # test_loss += loss_fn(pred, y).item()
                test_loss += loss_fn(pred.squeeze(1), y.to(torch.float32))
                loss = loss_fn(pred.squeeze(1), y.to(torch.float32))
                metric = BinaryJaccardIndex().to(self.device)

                # correct += (pred.argmax(1) == y).type(torch.float).sum().item()
        test_loss /= num_batches
        correct /= size
        jaccard_idx = 100 * metric(pred.squeeze(1), y)
        print(
            f"Test Error: \n"
            f"Jaccard-Index: {(jaccard_idx):>0.3f}%, Avg loss: {test_loss:>5f} \n"
        )
        return loss.item(), jaccard_idx.item()

    def checkpoints(self):
        pass
