import os
from typing import Optional

def recursively_find_directory(search_dir: str, dir_to_find: str) -> Optional[str]:
    for root, dirs, files in os.walk(search_dir):
        if dir_to_find in dirs:
            return os.path.join(root, dir_to_find)
    return None
