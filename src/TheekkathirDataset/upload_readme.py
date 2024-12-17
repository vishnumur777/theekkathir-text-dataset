import requests
from dotenv import load_dotenv
from huggingface_hub import HfApi
import os

load_dotenv()
token = os.getenv("HF_TOKEN")

def response_texts(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        else:
            print(f"Error: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None
    
url = "https://huggingface.co/datasets/aiwithvarun7/theekkathir-text-dataset/resolve/main/README.md"
current_readme = response_texts(url)

api = HfApi(token=token)

readme1 = ""
readme2 = ""

readme1_path="READMEs/README1.md"
readme2_path="READMEs/README2.md"

with open(readme1_path,"r") as file:
    for line in file:
        readme1 += line

with open(readme2_path,"r") as file:
    for line in file:
        readme2 += line

if current_readme == readme1:
    api.upload_file(
        path_or_fileobj=readme2_path,
        path_in_repo="aiwithvarun7/theekkathir-text-dataset/README.md",
        repo_id="aiwithvarun7/theekkathir-text-dataset",
        commit_message="Update README.md",
        repo_type="dataset"
    )
    print("README.md 1 has updated")

elif current_readme == readme2:
    api.upload_file(
        path_or_fileobj=readme1_path,
        path_in_repo="aiwithvarun7/theekkathir-text-dataset/README.md",
        repo_id="aiwithvarun7/theekkathir-text-dataset",
        commit_message="Update README.md",
        repo_type="dataset"
    )
    print("README.md 2 has updated")
else:
    print("No README.md were matched.")