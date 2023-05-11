import requests
import torch
from pathlib import Path
from io import BytesIO

if __name__ == "__main__":
    # get image:
    img_path = Path(r"data_local/images_only_AOI_test_color_corr_cleaned/31UGR_1_2018-4-20.pt")
    img_tensor = torch.load(img_path)
    im_numpy = img_tensor.numpy()
    stream = BytesIO(im_numpy)
    files = {"bytes_image": stream}

    
    
    req = requests.post("http://localhost:8080/predictions/test", data=im_numpy)
    print(req.status_code)
    if req.status_code == 200:
        res = req.json()
