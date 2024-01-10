import os
from os.path import exists
import shutil


def _listdir(d):  # listdir with full path
    return [os.path.join(d, f) for f in os.listdir(d)]


def cleanup(reddit_id):
    # Define the path to the temporary directory
    temp_directory = f"assets/temp/{reddit_id}"

    # Initialize a counter for the number of files deleted
    files_deleted = 0

    # Check if the directory exists
    if os.path.exists(temp_directory) and os.path.isdir(temp_directory):
        # Iterate over all files in the directory and delete them
        for file_name in os.listdir(temp_directory):
            file_path = os.path.join(temp_directory, file_name)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                    files_deleted += 1
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
                    files_deleted += 1
            except Exception as e:
                print(f"Error deleting {file_path}: {e}")

    return files_deleted
