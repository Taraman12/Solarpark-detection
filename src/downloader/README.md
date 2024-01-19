### At this service we can download Sentinel-2 data from the Copernicus Open Access Hub or AWS
This service is used to download the data locally, to create a custom trainings.

The are two possible ways to download Sentinel-2 data:
1. Download from the Copernicus Open Access Hub
2. Download from AWS

The first option is the default option. If you want to download from AWS, you have to set the variable `download_from_aws` to `True` in the `config.py` file.

Download from AWS is only for the first 100 GB per month free after that you have to pay for the download.

The download from the Copernicus Open Access Hub is always free.
But Copernicus Open Access Hub stores the data only for a shorter time. After that you can trigger a download from the LTA (Long Term Archive) but this can take a while. And you can trigger a retrieval from the LTA only every 30 minutes.

You can either download the latest data for prediction or you can download the data for a specific date to create a trainings set.

To create a trainings you can specify the seasons and the years in the `config.py` file.
And also the bands you want to use.

The data will be downloaded to the `data` folder.
