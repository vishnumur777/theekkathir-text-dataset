from huggingface_hub import HfApi,login
import os
from dotenv import load_dotenv
from datetime import datetime,timedelta
from tamil_date_converter.tamil_date_converter import date_to_tamildate_converter

load_dotenv()

token = os.getenv("HF_TOKEN")
if token is None:
    raise ValueError("HF_TOKEN environment variable is not set")

api = HfApi(token=token)

dt_now = datetime.now()
yesterday = dt_now - timedelta(days=1)
yesterday = yesterday.replace(hour=0,minute=0,second=0, microsecond=0)

yesterday_tamildate = date_to_tamildate_converter(yesterday)

parquet_path = f"/home/TheekkathirDataset/parquets/{yesterday_tamildate}.parquet"
texts_path = f"/home/TheekkathirDataset/texts/{yesterday_tamildate}/"

if not os.path.isfile(parquet_path):
    # Happens when the newspaper had no new articles, so there is nothing to upload.
    print(f"Skipping upload: no parquet file at {parquet_path}")
    raise SystemExit(0)

api.upload_file(
    path_or_fileobj=parquet_path,
    path_in_repo=f"TheekkathirDataset/parquets/{yesterday_tamildate}.parquet",
    repo_id="aiwithvarun7/theekkathir-text-dataset",
    commit_message=f"Upload Parquet for {yesterday_tamildate}",
    repo_type="dataset"   
)

if os.path.isdir(texts_path) and os.listdir(texts_path):
    api.upload_folder(
        folder_path=texts_path,
        path_in_repo=f"TheekkathirDataset/texts/{yesterday_tamildate}",
        repo_id="aiwithvarun7/theekkathir-text-dataset",
        commit_message=f"Upload Texts for {yesterday_tamildate}",
        repo_type="dataset"
    )
    print(f"Uploaded Parquet and Texts for {yesterday_tamildate}")
else:
    print(f"Uploaded Parquet for {yesterday_tamildate} (no text files found)")
