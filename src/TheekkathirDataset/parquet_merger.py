from huggingface_hub import HfFileSystem
from huggingface_hub import hf_hub_download
from dotenv import load_dotenv
import os
from tamil_date_converter.tamil_date_converter import date_to_tamildate_converter
from datetime import datetime,timedelta
import pandas as pd
import re

def merge_and_save_parquets(local_paths: list[str]) -> None:
    merged_dataframe = pd.DataFrame()
    for path in local_paths:
        df = pd.read_parquet(path)
        df = df.dropna(subset=["உள்ளடக்கம்"])
        merged_dataframe = pd.concat([merged_dataframe, df])
        merged_dataframe.sort_values(by="சேகரிக்கப்பட்ட தேதி",inplace=True)
    merged_dataframe.to_parquet(f"/home/TheekkathirDataset/parquets/outputs/{yesterday_month} - {yesterday_year}.parquet",index=False)
    print(f"{yesterday_month} - {yesterday_year}.parquet saved successfully to /home/TheekkathirDataset/parquets/outputs/")

load_dotenv()
token = os.environ.get('HF_TOKEN')
if token is None:
    raise ValueError("HF_TOKEN environment variable is not set")

fs = HfFileSystem(token=token)


dt_now = datetime.now()
yesterday = dt_now - timedelta(days=1)
yesterday = yesterday.replace(hour=0,minute=0,second=0, microsecond=0)

yesterday_tamildate = date_to_tamildate_converter(yesterday)
yesterday_list = yesterday_tamildate.split(" ")
yesterday_month = yesterday_list[0]
yesterday_year = yesterday_list[2]

repo_id = "aiwithvarun7/theekkathir-text-dataset"
files = fs.glob(f"datasets/{repo_id}/TheekkathirDataset/parquets/{yesterday_month}*{yesterday_year}.parquet")

local_paths = []

# download files from repository
for file in files:
    path = re.sub(r'datasets/aiwithvarun7/theekkathir-text-dataset/', '', file)
    local_path = hf_hub_download(repo_id=repo_id, filename=path, repo_type="dataset", revision="main",local_dir="/home/TheekkathirDataset/parquets/")
    local_paths.append(local_path)
    print(local_path)

merge_and_save_parquets(local_paths)
