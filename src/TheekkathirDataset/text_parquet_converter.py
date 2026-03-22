from huggingface_hub import HfFileSystem, hf_hub_download
from dotenv import load_dotenv
import os
import re

load_dotenv()
token = os.getenv("HF_TOKEN")
if token is None:
    raise ValueError("HF_TOKEN environment variable is not set")

fs = HfFileSystem(token=token)
repo_id = "aiwithvarun7/theekkathir-text-dataset"

def get_text_files_from_folder(folder_path: str) -> dict:
    """
    Get all text file contents from a specific HF dataset folder.
    
    Args:
        folder_path: Path like "TheekkathirDataset/texts/ஜனவரி 15, 2024"
    
    Returns:
        Dictionary with filename as key and file content as value
    """
    
    text_contents = {}
    files = fs.glob(f"{folder_path}/*.txt")
    
    for file in files:
        # Extract relative path from full path

        relative_path = re.sub(r'datasets/aiwithvarun7/theekkathir-text-dataset/', '', file)
        filename = os.path.basename(relative_path)
        print(filename)
        
        try:
            # Download and read file
            local_path = hf_hub_download(
                repo_id=repo_id,
                filename=relative_path,
                repo_type="dataset",
                revision="main"
            )
            
            with open(local_path, 'r', encoding='utf-8') as f:
                text_contents[filename] = f.read()
            
            print(f"✓ Read: {filename}")
        except Exception as e:
            print(f"✗ Error reading {filename}: {e}")
    
    return text_contents

def get_text_files_from_multiple_folders(folder_paths: list) -> dict:
    """
    Get text file contents from multiple folders.
    
    Args:
        folder_paths: List of folder paths
    
    Returns:
        Dictionary with folder name as key and text_contents dict as value
    """
    all_contents = {}

    for folders in folder_paths:
        folder_name = os.path.basename(folders)
        print(folder_name)
        all_contents[folder_name] = get_text_files_from_folder(folders)
    
    # for folder_path in folder_paths:
    #     print(folder_path)
    #     folder_name = os.path.basename(folder_path)
    #     all_contents[folder_name] = get_text_files_from_folder(folder_path)
    
    return all_contents

# Example usage:
if __name__ == "__main__":
    # Single folder
    # folder_contents = get_text_files_from_folder("TheekkathirDataset/texts/ஜனவரி 15, 2024")
    
    # Multiple folders
    folders = fs.glob(f"datasets/{repo_id}/TheekkathirDataset/texts/டிசம்பர்*2024/")
    
    all_text_contents = get_text_files_from_multiple_folders(folders)
    
    # Print results
    for folder_name, contents in all_text_contents.items():
        print(f"\n--- Folder: {folder_name} ---")
        for filename, text in contents.items():
            print(f"\n{filename}:\n{text[:200]}...")  # Print first 200 chars