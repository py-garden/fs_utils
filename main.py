import os
import inspect
from typing import Optional, List, Callable

def concatenate_files(source_files, destination_file):
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

def find_all_instances_of_file_in_directory_recursively(base_directory, target_filename) -> List[str]:
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

