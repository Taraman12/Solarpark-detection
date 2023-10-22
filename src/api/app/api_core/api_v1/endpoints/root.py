# third-party
from fastapi import APIRouter

# import os
# import subprocess

# from app.preprocessing.main_preprocessing import main_preprocessing

router = APIRouter()


@router.get("/")
def root():
    return {"message": "API is running"}


# @router.get("/start-preprocess")
# async def start_preprocess():
#     # await os.system("type nul > filename.txt")
#     print("start preprocess")
#     await subprocess.run(["type nul", ">", "filename.txt"])
#     # await main_preprocessing()
#     return {"message": "start preprocess"}
