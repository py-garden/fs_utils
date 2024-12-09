import os
import time
import shutil
import argparse 
import configparser
import importlib.util
import sys
from typing import List, Callable
import json

BASE_DIR_LAST_MOD_FILE = ".base_dir_last_modified.json"

# Function to get the modification times of all files in a directory
def get_modification_times(directory):
    mod_times = {}
    for root, _, files in os.walk(directory):
        for filename in files:
            filepath = os.path.join(root, filename)
            mod_times[filepath] = os.path.getmtime(filepath)
    return mod_times

def load_last_mod_times():
    """Load the stored modification times from the last run"""
    if os.path.exists(BASE_DIR_LAST_MOD_FILE):
        with open(BASE_DIR_LAST_MOD_FILE, "r") as f:
            return json.load(f)
    return {}

def save_mod_times(mod_times):
    """Save the current modification times for future comparison"""
    with open(BASE_DIR_LAST_MOD_FILE, "w") as f:
        json.dump(mod_times, f)

def find_modified_files(last_mod_times, current_mod_times) -> List[str]:
    """Compare the last known modification times with the current ones"""
    modified_files = []
    for filepath, current_time in current_mod_times.items():
        last_time = last_mod_times.get(filepath)
        # File is modified if it's new or has a different modification time
        if last_time is None or current_time > last_time:
            modified_files.append(filepath)
    return modified_files

def save_mod_times_for_base_dir(base_dir: str):
    last_mod_times = load_last_mod_times()
    current_mod_times = get_modification_times(base_dir)

    modified_files = find_modified_files(last_mod_times, current_mod_times)

    if modified_files:
        print("Modified files since last check:")
        for file in modified_files:
            print(file)
    else:
        print("No files have been modified since last check.")

    # Save the current modification times for the next run
    save_mod_times(current_mod_times)


def start_watching_directory(watch_directory: str, modification_callback: Callable):
    if not os.path.isdir(watch_directory):
        print("Error: gen dir doesn't exist, first run the program in non devel mode first")
    else:
        rate_to_check_for_changes_seconds = 1
        while True:
            base_dir_last_modified_times = load_last_mod_times()
            base_dir_current_modified_times = get_modification_times(args.base_dir)
            modified_files = find_modified_files(base_dir_last_modified_times, base_dir_current_modified_times)

            if modified_files:
                print("Modified files since last check:")
                for file in modified_files:
                    print(file)
                print("Now converting")
                # TODO don't use modified files we need it in the gneerated directory.
                copied_files = copy_specific_files_to_the_generated_directory(modified_files, args.base_dir, args.gen_dir)
                print(f"copied files {copied_files}")
                # convert_specific_content_files_to_valid_html(copied_files, base_template_file, custom_conversion_module)
                save_mod_times_for_base_dir(args.base_dir)
            else:
                print("No files have been modified since last check.")
            time.sleep(rate_to_check_for_changes_seconds)

