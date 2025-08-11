import os
import inspect
import json
from typing import Optional, List, Callable, Dict
import re
from pathlib import Path

def path_ends_with_filename(file_path: str, file_name: str) -> bool:
    """
    Returns True if the file_path ends with the given file_name.
    """
    return os.path.basename(file_path) == file_name

def strip_first_path_component(path: str) -> str:
    """
    Removes the first component of a given path.
    """
    parts = Path(path).parts
    if len(parts) <= 1:
        return ''
    return str(Path(*parts[1:]))

def strip_last_path_component(path: str) -> str:
    """
    Removes the last component of a given path.
    Returns an empty string if there is no component to remove.
    """
    parts = Path(path).parts
    if len(parts) <= 1:
        return ''
    return str(Path(*parts[:-1]))

def get_last_path_component(path: str) -> str:
    """
    Returns the last component of a path (file or directory name).
    """
    return os.path.basename(path.rstrip('/\\'))

def concatenate_files(source_files, destination_file) -> None:
    """
    Concatenates the contents of source files into a destination file.

    Parameters:
        source_files (List[str]): List of paths to source files.
        destination_file (str): Path to the destination file (overwritten if exists).
    """
    with open(destination_file, 'w', encoding='utf-8') as dest:
        for src_path in source_files:
            with open(src_path, 'r', encoding='utf-8') as src:
                dest.write(src.read())

def find_files_matching_regex(
    base_directory: str,
    pattern: str,
    max_depth: int = None
) -> List[str]:
    """
    Recursively search for all files matching a regex pattern within a directory, 
    optionally up to a specified depth.

    Parameters:
        base_directory (str): The root directory to start the search.
        pattern (str): A regex pattern to match filenames.
        max_depth (int, optional): The maximum directory depth to recurse. 
                                   None means unlimited.

    Returns:
        List[str]: A list of full paths to each matching file.
    """
    regex = re.compile(pattern)
    matches: List[str] = []
    base_depth = base_directory.rstrip(os.path.sep).count(os.path.sep)

    for root, dirs, files in os.walk(base_directory):
        current_depth = root.count(os.path.sep) - base_depth
        if max_depth is not None and current_depth > max_depth:
            # prevent deeper traversal
            dirs[:] = []
            continue

        for filename in files:
            if regex.fullmatch(filename):
                matches.append(os.path.join(root, filename))

    return matches

def find_all_instances_of_file_in_directory_recursively(base_directory: str, target_filename: str) -> List[str]:
    """
    Recursively searches for all instances of a file with the given name in the specified directory.

    Parameters:
        base_directory (str): The root directory to start the search.
        target_filename (str): The name of the file to search for.

    Returns:
        List[str]: A list of full paths to each matching file.
    """
    matches :List[str] = []
    for root, dirs, files in os.walk(base_directory):
        if target_filename in files:
            matches.append(os.path.join(root, target_filename))
    return matches

def process_files_recursively(directory: str, filetypes: List[str], file_function: Callable[[str], None]) -> None:
    """
    Iterates over all files in a directory recursively, filters by a list of filetypes,
    and applies a function to each file.

    Args:
        directory (str): The directory to search in.
        filetypes (List[str]): A list of file extensions to filter (e.g., ['.txt', '.py']).
        file_function (Callable[[str], None]): A function to run with the path to each file.
    """
    # Normalize file extensions to ensure they start with a dot.
    normalized_filetypes = [ftype if ftype.startswith('.') else '.' + ftype for ftype in filetypes]

    for root, _, files in os.walk(directory):
        for file in files:
            if any(file.endswith(ftype) for ftype in normalized_filetypes):
                full_path = os.path.join(root, file)
                file_function(full_path)

def get_absolute_path_of_where_this_script_exists() -> str:
    """
    returns the path to the script in which this function was called.
    """
    # get the caller's file path, which will be `a.py` in this case.
    caller_frame = inspect.stack()[1]
    caller_file = caller_frame[0].f_globals["__file__"]
    
    # Get the directory of the caller's script
    return os.path.dirname(os.path.abspath(caller_file))

def recursively_find_directory(search_dir: str, dir_to_find: str) -> Optional[str]:
    for root, dirs, files in os.walk(search_dir):
        if dir_to_find in dirs:
            return os.path.join(root, dir_to_find)
    return None

def attempt_to_delete_files(file_paths: List[str]) -> bool:
    all_succeeded = True
    for file_path in file_paths:
        success = attempt_to_delete_file(file_path)
        if not success:
            all_succeeded = False
    return all_succeeded

def attempt_to_delete_file(file_path: str) -> bool:
    try:
        os.remove(file_path)
        print(f"File '{file_path}' has been deleted successfully.")
        return True
    except FileNotFoundError:
        print(f"File '{file_path}' does not exist.")
    except PermissionError:
        print(f"Permission denied: Unable to delete '{file_path}'.")
    except Exception as e:
        print(f"An error occurred while deleting '{file_path}': {e}")
    return False



# NOTE: in the future I might want to do something like filename to a 
# dictionary of checksum to day it was observed on or something.
BASE_DIR_LAST_MOD_FILE = ".base_dir_last_modified.json"

def make_regex_filter(whitelist: List[str], blacklist: List[str]) -> Callable[[str], bool]:
    """
    eg) path_filter = make_regex_filter([r"\.py$"], [r"test_", r"__pycache__"])
    """
    whitelist_re = [re.compile(r) for r in whitelist]
    blacklist_re = [re.compile(r) for r in blacklist]

    # true if path is allowed otherwise false
    def _filter(path: str) -> bool:
        if not any(r.search(path) for r in whitelist_re):
            return False
        if any(r.search(path) for r in blacklist_re):
            return False
        return True

    return _filter


def get_modification_times(
    directory: str,
    path_filter: Callable[[str], bool] = lambda _: True
) -> Dict[str, float]:
    """
    Get the last modification times for all files in a directory recursively,
    using a custom path filter to determine which files are included.

    Args:
        directory (str): The root directory to walk through.
        path_filter (Callable[[str], bool], optional): A function that takes a file path
            and returns True if the file should be included. Defaults to allowing all paths.

    Returns:
        Dict[str, float]: A dictionary mapping file paths to their last modification times.
    """
    mod_times = {}
    for root, _, files in os.walk(directory):
        for filename in files:
            filepath = os.path.join(root, filename)
            if path_filter(filepath):
                mod_times[filepath] = os.path.getmtime(filepath)
    return mod_times

def load_last_mod_times(mod_times_path: str = BASE_DIR_LAST_MOD_FILE) -> Dict[str, float]:
    """
    Load the stored modification times from the last run.

    Returns:
        Dict[str, float]: A dictionary of previously recorded file modification times.
                          Returns an empty dictionary if the file does not exist.
    """
    if os.path.exists(mod_times_path):
        with open(mod_times_path, "r") as f:
            return json.load(f)
    return {}

def save_mod_times(mod_times: Dict[str, float], mod_times_path: str = BASE_DIR_LAST_MOD_FILE) -> None:
    """
    Save the current file modification times to a JSON file for later comparison.

    Args:
        mod_times (Dict[str, float]): Dictionary of file paths and their modification times.
    """
    with open(mod_times_path, "w") as f:
        json.dump(mod_times, f)

def find_modified_files(
    last_mod_times: Dict[str, float],
    current_mod_times: Dict[str, float]
) -> List[str]:
    """
    Compare previous and current modification times to find updated or new files.

    Args:
        last_mod_times (Dict[str, float]): Previously saved file modification times.
        current_mod_times (Dict[str, float]): Current file modification times.

    Returns:
        List[str]: List of file paths that are new or have been modified.
    """
    modified_files = []
    for filepath, current_time in current_mod_times.items():
        last_time = last_mod_times.get(filepath)
        if last_time is None or current_time > last_time:
            modified_files.append(filepath)
    return modified_files

def find_new_files(
    last_mod_times: Dict[str, float],
    current_mod_times: Dict[str, float]
) -> List[str]:
    """
    Find newly created files by comparing previous and current file modification times.

    Args:
        last_mod_times (Dict[str, float]): Previously saved file modification times.
        current_mod_times (Dict[str, float]): Current file modification times.

    Returns:
        List[str]: List of file paths that are new (i.e. did not exist before).
    """
    new_files = []
    for filepath in current_mod_times:
        if filepath not in last_mod_times:
            new_files.append(filepath)
    return new_files
