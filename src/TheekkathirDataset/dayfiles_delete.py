from huggingface_hub import HfApi
from huggingface_hub import HfFileSystem
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta
from tamil_date_converter.tamil_date_converter import date_to_tamildate_converter
import re

load_dotenv()
token = os.getenv("HF_TOKEN")
if token is None:
    raise ValueError("HF_TOKEN environment variable is not set")

api = HfApi(token=token)
fs = HfFileSystem(token=token)

dt_now = datetime.now()
if dt_now.day > 1:
    dt_now = dt_now.replace(day=1)
yesterday = dt_now - timedelta(days=1)
yesterday = yesterday.replace(hour=0,minute=0,second=0, microsecond=0)


yesterday_tamildate = date_to_tamildate_converter(yesterday)
yesterday_list = yesterday_tamildate.split(" ")
yesterday_month = yesterday_list[0]
yesterday_year = yesterday_list[2]

repo_id = "aiwithvarun7/theekkathir-text-dataset"
files = fs.glob(f"datasets/{repo_id}/TheekkathirDataset/parquets/{yesterday_month}*{yesterday_year}*.parquet")
commit = "Deleted all 30 days files in a month."
for full_path in files:
    path = re.sub(r'datasets/aiwithvarun7/theekkathir-text-dataset/', '', full_path)
    print(f"Deleting {path}...")
    api.delete_file(repo_id=repo_id, path_in_repo=path, commit_message=commit, repo_type="dataset")
    print(f"{path} deleted successfully.")

api.upload_file(
    path_in_repo=f"TheekkathirDataset/parquets/{yesterday_month} - {yesterday_year}.parquet",
    repo_id=repo_id,
    path_or_fileobj=f"/home/TheekkathirDataset/parquets/outputs/{yesterday_month} - {yesterday_year}.parquet",
    repo_type="dataset",
    commit_message=f"Upload Parquet for {yesterday_tamildate}"
)
