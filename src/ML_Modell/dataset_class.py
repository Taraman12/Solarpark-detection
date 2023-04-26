# build-in
import os

# third-party
import torch
from torch.utils.data import Dataset


class GeoImageDataset(Dataset):
    def __init__(self, img_dir: str, mask_dir: str):  # transform=None
        self.img_dir = img_dir
        self.mask_dir = mask_dir
        self.img_files = os.listdir(self.img_dir)
        self.mask_files = os.listdir(self.mask_dir)
        # self.transform = transform

    def __len__(self) -> int:
        return len(self.img_files)

    def __getitem__(self, idx: int) -> tuple:
        # Load image
        img_path = os.path.join(self.img_dir, self.img_files[idx])
        # mask and img_file have so far the same name
        mask_path = os.path.join(self.mask_dir, self.img_files[idx])
        img = torch.load(img_path)
        # converts bool mask into integer (0/1)
        mask = torch.load(mask_path).long()
        # Apply transform (if any)
        # if self.transform:
        #     img = self.transform(img)

        return img, mask
