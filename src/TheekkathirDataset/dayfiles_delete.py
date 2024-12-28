from huggingface_hub import HfApi
from huggingface_hub import HfFileSystem
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta
from tamil_date_converter.tamil_date_converter import date_to_tamildate_converter


load_dotenv()
token = os.getenv("HF_TOKEN")
if token is None:
    raise ValueError("HF_TOKEN environment variable is not set")

api = HfApi(token=token)
fs = HfFileSystem(token=token)

dt_now = datetime.now()
yesterday = dt_now - timedelta(days=1)
yesterday = yesterday.replace(hour=0,minute=0,second=0, microsecond=0)

yesterday_tamildate = date_to_tamildate_converter(yesterday)
yesterday_list = yesterday_tamildate.split(" ")
yesterday_month = yesterday_list[0]

repo_id = "aiwithvarun7/theekkathir-text-dataset"
files = fs.glob(f"datasets/{repo_id}/TheekkathirDataset/parquets/{yesterday_month}*.parquet")

for path in files:
    print(f"Deleting {path}...")
    api.delete_file(repo_id=repo_id, path_to_folder=path)
    print(f"{path} deleted successfully.")