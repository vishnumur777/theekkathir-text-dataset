import requests
from dotenv import load_dotenv
from huggingface_hub import HfApi
import os

load_dotenv()
token = os.getenv("HF_TOKEN")

api = HfApi(token=token)

readme1_path="READMEs/README1.md"
readme2_path="READMEs/README2.md"
log_path="https://huggingface.co/datasets/aiwithvarun7/theekkathir-text-dataset/resolve/main/value.log"
local_log_path = "/home/TheekkathirDataset/value.log"
log_value = requests.get(log_path)
log_value = log_value.text

if log_value == "1":
    api.upload_file(
        path_or_fileobj=readme2_path,
        path_in_repo="aiwithvarun7/theekkathir-text-dataset/README.md",
        repo_id="aiwithvarun7/theekkathir-text-dataset",
        commit_message="Update README.md",
        repo_type="dataset"
    )
    print("README.md 1 has updated")
    
    with open(local_log_value, "w") as file:
        file.write("2")

elif log_value == "2":
    api.upload_file(
        path_or_fileobj=readme1_path,
        path_in_repo="aiwithvarun7/theekkathir-text-dataset/README.md",
        repo_id="aiwithvarun7/theekkathir-text-dataset",
        commit_message="Update README.md",
        repo_type="dataset"
    )
    print("README.md 2 has updated")

    with open(local_log_path, "w") as file:
        file.write("1")
else:
    print("No logs found to update README")


api.upload_file(
        path_or_fileobj=local_log_path,
        path_in_repo="value.log",
        repo_id="aiwithvarun7/theekkathir-text-dataset",
        commit_message="Update log",
        repo_type="dataset"
    )
print("logs has updated")