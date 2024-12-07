import os
import inspect
from typing import Optional, List


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

