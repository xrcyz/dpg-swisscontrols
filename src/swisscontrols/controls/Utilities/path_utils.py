import os
from datetime import datetime

from dataclasses import dataclass
from typing import Optional, List, Tuple

@dataclass
class FileInfo:
    name: str
    date_modified: float  # Epoch time format
    type: str  # "File" or "Folder"
    size: Optional[int]  # None for folders


def get_last_folder_or_drive(path):
    normalized_path = os.path.normpath(path)
    base_name = os.path.basename(normalized_path)
    if not base_name and os.path.splitdrive(normalized_path)[0]:
        return '(' + normalized_path.replace('\\', '') + ')'
    return base_name

def list_folders(path: str):
    # List all items in the given directory
    all_items = [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]

    # Filter out hidden files and folders (Unix-like systems)
    visible_items = [item for item in all_items if not item.startswith('.')]

    # For Windows: further filter out system and hidden files/folders
    if os.name == 'nt':
        import ctypes

        FILE_ATTRIBUTE_HIDDEN = 0x2
        FILE_ATTRIBUTE_SYSTEM = 0x4

        def is_hidden_or_system(filepath: str) -> bool:
            try:
                attrs = ctypes.windll.kernel32.GetFileAttributesW(filepath)
                if attrs == -1:  # Invalid attributes
                    # print(f"Invalid attributes for: {filepath}")
                    return True  # Default to hidden
                return (attrs & FILE_ATTRIBUTE_HIDDEN) or (attrs & FILE_ATTRIBUTE_SYSTEM)
            except Exception as e:
                print(f"Exception for {filepath}: {e}")
                return True  # Default to hidden

        visible_items = [item for item in visible_items if not is_hidden_or_system(os.path.join(path, item))]

    return visible_items

def list_files_and_folders(path: str):
    # List all items in the given directory
    all_items = os.listdir(path)

    # Filter out hidden files and folders (Unix-like systems)
    visible_items = [item for item in all_items if not item.startswith('.')]

    # For Windows: further filter out system and hidden files/folders
    if os.name == 'nt':
        import ctypes

        FILE_ATTRIBUTE_HIDDEN = 0x2
        FILE_ATTRIBUTE_SYSTEM = 0x4

        def is_hidden_or_system(filepath: str) -> bool:
            try:
                attrs = ctypes.windll.kernel32.GetFileAttributesW(filepath)
                if attrs == -1:  # Invalid attributes
                    # print(f"Invalid attributes for: {filepath}")
                    return True  # Default to hidden
                return (attrs & FILE_ATTRIBUTE_HIDDEN) or (attrs & FILE_ATTRIBUTE_SYSTEM)
            except Exception as e:
                print(f"Exception for {filepath}: {e}")
                return True  # Default to hidden

        visible_items = [item for item in visible_items if not is_hidden_or_system(os.path.join(path, item))]

    return visible_items

def get_file_info(filename: str, folder_path: str) -> dict:
    full_path = os.path.join(folder_path, filename)
    file_info = os.stat(full_path)
    
    detail = FileInfo(
        name=filename,
        date_modified=file_info.st_mtime,
        type='Folder' if os.path.isdir(full_path) else 'File',  # Simplified type info
        size=file_info.st_size if os.path.isfile(full_path) else None
    )
    
    return detail

def split_and_sort_file_info(file_info_list: List[FileInfo], sort_key: str = 'name', reverse: bool = False) -> Tuple[List[FileInfo], List[FileInfo]]:
    """
    Splits the file_details_list into files and folders, and sorts each by the given sort_key.
    
    Parameters:
    - file_details_list: List of FileDetail objects containing file details.
    - sort_key: Attribute by which to sort the files and folders. Default is 'name'.
    - reverse: Whether to reverse the sort order. Default is False.

    Returns:
    - Tuple containing sorted lists: (sorted_folders, sorted_files)
    """

    # Split into files and folders
    folders = [detail for detail in file_info_list if detail.type == 'Folder']
    files = [detail for detail in file_info_list if detail.type == 'File']

    # Sort each list
    sorted_folder_info = sorted(folders, key=lambda x: getattr(x, sort_key), reverse=reverse)
    sorted_file_info = sorted(files, key=lambda x: getattr(x, sort_key), reverse=reverse)

    return sorted_folder_info, sorted_file_info


@dataclass
class Breadcrumb:
    path_index: int
    path_segment: str

def path_to_breadcrumbs(path: str) -> list[Breadcrumb]:
    # Handle the special case for Windows drive letters
    if os.name == "nt" and len(path) > 1 and path[1] == ":":
        path = path[0] + path[1] + path[2:].replace(":", "")
        path_segments = [segment for segment in path.split(os.sep) if segment]
        # Format the drive letter
        if len(path_segments) > 0 and ":" in path_segments[0]:
            drive_letter = path_segments[0][0]
            display_segment = f"({drive_letter}:)"
            path_segments[0] = drive_letter + ":\\"
        else:
            display_segment = path_segments[0]
    else:
        path_segments = [segment for segment in path.split(os.sep) if segment]
        display_segment = os.sep if path.startswith(os.sep) else path_segments[0]

    breadcrumbs = [Breadcrumb(path_index=i, path_segment=segment) 
                   for i, segment in enumerate(path_segments)]
    
    return breadcrumbs