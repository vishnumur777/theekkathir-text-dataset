from huggingface_hub import HfApi,login
import os
from dotenv import load_dotenv
from datetime import datetime,timedelta
from tamil_date_converter.tamil_date_converter import date_to_tamildate_converter

load_dotenv()

login(token=os.getenv("HF_TOKEN"))

api = HfApi()

dt_now = datetime.now()
yesterday = dt_now - timedelta(days=1)
yesterday = yesterday.replace(hour=0,minute=0,second=0, microsecond=0)

yesterday_tamildate = date_to_tamildate_converter(yesterday)

files_to_upload = [f"/home/hdd/pythonPract/TheekkathirDataset/parquets/{yesterday_tamildate}.parquet",f"/home/hdd/pythonPract/TheekkathirDataset/texts/{yesterday_tamildate}/"]


api.upload_file(
    path_or_fileobj=files_to_upload[0],
    path_in_repo=f"TheekkathirDataset/parquets/{yesterday_tamildate}.parquet",
    repo_id="aiwithvarun7/theekkathir-text-dataset",
    commit_message=f"Upload Parquet for {yesterday_tamildate}",
    repo_type="dataset"   
)

api.upload_folder(
    folder_path=files_to_upload[1],
    path_in_repo=f"TheekkathirDataset/texts/{yesterday_tamildate}",
    repo_id="aiwithvarun7/theekkathir-text-dataset",
    commit_message=f"Upload Texts for {yesterday_tamildate}",
    repo_type="dataset"
)

print(f"Uploaded Parquet and Texts for {yesterday_tamildate}")