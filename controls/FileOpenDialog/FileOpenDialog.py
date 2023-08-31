import dearpygui.dearpygui as dpg
import os
from datetime import datetime

from dataclasses import dataclass
from typing import Optional, List, Tuple

from controls.DpgHelpers.MvThemeCol import MvThemeCol
from controls.DpgHelpers.MvStyleVar import MvStyleVar
from controls.Textures.TextureIds import TextureIds

@dataclass
class FileInfo:
    name: str
    date_modified: float  # Epoch time format
    type: str  # "File" or "Folder"
    size: Optional[int]  # None for folders

@dataclass
class FolderButtonInfo:
    path: str
    folder_btn_id: str = None
    caption_btn_id: str = None
    indent_level: int = 0

def format_date(timestamp: float) -> str:
    dt_object = datetime.fromtimestamp(timestamp)
    return dt_object.strftime('%Y/%m/%d')

def format_size(size_in_bytes: Optional[int]) -> str:
    if size_in_bytes is None:  # Handle the case for folders
        return ""

    size_in_kb = size_in_bytes / 1024
    return "{:,.0f} KB".format(size_in_kb)

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

def fileOpenDialog():

    HOME_PATH = os.path.expanduser("~")
    DEFAULT_PATH = os.path.join(HOME_PATH, 'Documents')
    if not os.path.exists(DEFAULT_PATH):
        DEFAULT_PATH = HOME_PATH
    
    current_path = DEFAULT_PATH
    current_breadcrumbs = path_to_breadcrumbs(current_path)
    breadcrumb_dict = {}  # A dictionary to map DPG IDs to path segments
    folderTreeDict = {}

    ID_WINDOW_DIALOG = dpg.generate_uuid()
    ID_GROUP_CONTAINER = dpg.generate_uuid()
    ID_GROUP_HEADER = dpg.generate_uuid()
    ID_GROUP_URL_BAR = dpg.generate_uuid()
    ID_GROUP_BODY = dpg.generate_uuid()
    ID_GROUP_FILENAME = dpg.generate_uuid()
    ID_GROUP_FOOTER = dpg.generate_uuid()
    ID_WINDOW_TREELIST = dpg.generate_uuid()
    ID_GROUP_TREELIST = dpg.generate_uuid()
    ID_WINDOW_LISTDIR = dpg.generate_uuid()
    ID_GROUP_LISTDIR = dpg.generate_uuid()

    ID_BUTTON_ACCEPT = dpg.generate_uuid()
    ID_BUTTON_CANCEL = dpg.generate_uuid()

    ID_TEX_FOLDER_ICON = TextureIds.ID_ICON_FOLDER.UUID

    ID_THEME_ICON_BUTTON = dpg.generate_uuid()
    ID_THEME_BUTTON_FILEPATH = dpg.generate_uuid()
    ID_THEME_BUTTON_NOCLICK  = dpg.generate_uuid()
    ID_THEME_NOSPACING = dpg.generate_uuid()
    ID_THEME_LISTBOX = dpg.generate_uuid()
    
    ID_HANDLER_DOUBLE_CLICK = dpg.generate_uuid()

    URL_BAR_SEPARATOR = ' > '
    
    def _on_double_click(sender, app_data):
        print("double clicked")

    def _on_breadcrumb_click(sender):
        nonlocal current_path
        nonlocal current_breadcrumbs
        
        breadcrumbs_to_join  = current_breadcrumbs[:1+breadcrumb_dict[sender].path_index]
        path_segments = [breadcrumb.path_segment for breadcrumb in breadcrumbs_to_join]

        current_path = os.path.join(*path_segments)
        current_breadcrumbs = path_to_breadcrumbs(current_path)

        _update_breadcrumbs()
        _update_listdir()

    def _update_breadcrumbs():
        nonlocal breadcrumb_dict
        breadcrumb_dict = {}
        
        for item in dpg.get_item_children(ID_GROUP_URL_BAR, 1):
            dpg.delete_item(item)

        for i, crumb in enumerate(current_breadcrumbs[:-1]):
            # add button
            btn_id = dpg.add_button(parent=ID_GROUP_URL_BAR, label=crumb.path_segment, callback=_on_breadcrumb_click)
            breadcrumb_dict[btn_id] = Breadcrumb(path_index=i, path_segment=crumb)
            # add separator
            sep = dpg.add_button(parent=ID_GROUP_URL_BAR, label=URL_BAR_SEPARATOR)
            dpg.bind_item_theme(sep, ID_THEME_BUTTON_NOCLICK)
        # add final button
        last_btn_id = dpg.add_button(parent=ID_GROUP_URL_BAR, label=current_breadcrumbs[-1].path_segment, callback=_on_breadcrumb_click) 
        breadcrumb_dict[last_btn_id] = Breadcrumb(path_index=len(current_breadcrumbs) - 1, path_segment=current_breadcrumbs[-1])
        # add final separator
        f = dpg.add_button(parent=ID_GROUP_URL_BAR, width=4)
        dpg.bind_item_theme(f, ID_THEME_BUTTON_NOCLICK)
        # button to activate textbox input
        dpg.add_button(parent=ID_GROUP_URL_BAR, width=-1)

    def _update_listdir():
        for item in dpg.get_item_children(ID_GROUP_LISTDIR, 1):
            dpg.delete_item(item)
        
        visible_items = list_files_and_folders(current_path)
        file_info_list = [get_file_info(item, current_path) for item in visible_items]
        folder_infos, file_infos = split_and_sort_file_info(file_info_list)

        def _sort_callback(sender, sort_specs):
            # this probably belongs in DpgHelpers, but for now:
            
            # No sorting case
            if sort_specs is None:
                return

            cols = dpg.get_item_children(sender, 0)
            rows = dpg.get_item_children(sender, 1)

            column_id, direction = sort_specs[0]
            column_idx = cols.index(column_id)
            
            # Create a list that can be sorted based on the specified cell
            sortable_list = []
            for row in rows:
                cell = dpg.get_item_children(row, 1)[column_idx]
                # assuming that the table cell holds a selectable...
                sortable_list.append([row, dpg.get_item_label(cell)])
            
            # Sort based on the value in the specified column
            sortable_list.sort(key=lambda x: x[1], reverse=direction < 0)
            # Create a list of sorted row ids
            new_order = [pair[0] for pair in sortable_list]
            
            dpg.reorder_items(sender, 1, new_order)

        with dpg.table(parent=ID_GROUP_LISTDIR,
                      header_row=True, row_background=True,
                      resizable=True, reorderable=True, hideable=True, 
                      sortable=True, context_menu_in_body=True, callback=_sort_callback):
            dpg.add_table_column(label='Name', init_width_or_weight=4, no_hide=True)
            dpg.add_table_column(label='Date Modified', init_width_or_weight=2)
            dpg.add_table_column(label='Size', init_width_or_weight=1, )

            for item in [*folder_infos, *file_infos]:
                with dpg.table_row():
                    dpg.add_selectable(label=item.name)
                    dpg.add_selectable(label=format_date(item.date_modified))
                    dpg.add_selectable(label=format_size(item.size))

    def _update_treelist(sender, indent_level: int, path: str):
        if not indent_level: indent_level = 0
        if not path: 
            path = None
            caption = 'This PC:'
        else:
            caption = get_last_folder_or_drive(path)
        
        # if sender is This PC then ...
        if not sender:
            destination_arg = {'parent': ID_GROUP_TREELIST}

            with dpg.group(horizontal=True, **destination_arg):
                icon_btn = dpg.add_image_button(texture_tag=ID_TEX_FOLDER_ICON, 
                                    height=19, width=19, indent=indent_level*8,
                                    callback=_update_treelist)
                dpg.bind_item_theme(dpg.last_item(), ID_THEME_ICON_BUTTON)
                caption_btn = dpg.add_button(label=caption)
                dpg.bind_item_handler_registry(dpg.last_item(), ID_HANDLER_DOUBLE_CLICK)

                folderButtonInfo = FolderButtonInfo(path=path, folder_btn_id=icon_btn, caption_btn_id=caption_btn, indent_level=indent_level)
                folderTreeDict[icon_btn] = folderButtonInfo
        else:
            sender_info: FolderButtonInfo = folderTreeDict[sender]
            parent_indent_level = sender_info.indent_level
            child_indent_level = parent_indent_level + 1
            
            parent_path = sender_info.path
            child_folders = list_folders(parent_path)
            
            # the sender is a button inside a group inside a list of groups
            # we need to insert a group after the current group
            current_group = dpg.get_item_parent(sender)
            list_of_groups = dpg.get_item_children(ID_GROUP_TREELIST, 1)
            sender_idx = list_of_groups.index(current_group) 

            expand_folder = True

            # _collapse_folder(): 
            if sender_idx + 1 < len(list_of_groups):
               
                child_index = sender_idx + 1

                while child_index < len(list_of_groups):
                    next_group = list_of_groups[child_index]
                    next_btn = dpg.get_item_children(next_group, 1)[0]
                    next_indent = folderTreeDict[next_btn].indent_level

                    if next_indent <= parent_indent_level:
                        break
                    
                    expand_folder = False
                    del folderTreeDict[next_btn]
                    dpg.delete_item(next_group)
                    child_index += 1

            # _expand_folder(): 
            if expand_folder:
                destination_arg = {}
                if sender_idx < len(list_of_groups) - 1:
                    destination_arg = {'before': list_of_groups[sender_idx+1]}
                else:
                    destination_arg = {'parent': ID_GROUP_TREELIST}
            
                for child_folder in sorted(child_folders):
                    child_path = os.path.join(parent_path, child_folder)
                    with dpg.group(horizontal=True, **destination_arg):
                        icon_btn = dpg.add_image_button(texture_tag=ID_TEX_FOLDER_ICON, 
                                            height=19, width=19, indent=child_indent_level*8,
                                            callback=_update_treelist)
                        dpg.bind_item_theme(dpg.last_item(), ID_THEME_ICON_BUTTON)
                        caption_btn = dpg.add_button(label=child_folder)
                        dpg.bind_item_handler_registry(dpg.last_item(), ID_HANDLER_DOUBLE_CLICK)

                        folderButtonInfo = FolderButtonInfo(path=child_path, folder_btn_id=icon_btn, caption_btn_id=caption_btn, indent_level=child_indent_level)
                        folderTreeDict[icon_btn] = folderButtonInfo

    # add double click handler
    with dpg.item_handler_registry(tag=ID_HANDLER_DOUBLE_CLICK):
        dpg.add_item_double_clicked_handler(callback=_on_double_click)

    def _register_themes():
        with dpg.theme(tag=ID_THEME_ICON_BUTTON):
            with dpg.theme_component(dpg.mvImageButton):
                # remove frame padding around image button
                dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 0, 0)

        with dpg.theme(tag=ID_THEME_BUTTON_FILEPATH):
            with dpg.theme_component(dpg.mvButton):
                dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 0, MvStyleVar.FramePadding.value[1])

        with dpg.theme(tag=ID_THEME_BUTTON_NOCLICK):
            with dpg.theme_component(dpg.mvButton):
                # dpg.add_theme_color(dpg.mvThemeCol_Button, (255, 255, 255, 0))
                dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, MvThemeCol.Button.value)
                dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, MvThemeCol.Button.value)

        with dpg.theme(tag=ID_THEME_NOSPACING):
            with dpg.theme_component(dpg.mvGroup):
                dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 0, MvStyleVar.FramePadding.value[1])
                dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing, 0, MvStyleVar.ItemSpacing.value[1])

        with dpg.theme(tag=ID_THEME_LISTBOX):
            with dpg.theme_component(dpg.mvSelectable):
                dpg.add_theme_color(dpg.mvThemeCol_Header, (0.26 * 255, 0.59 * 255, 0.98 * 255, 0.31 * 255))
            with dpg.theme_component(dpg.mvChildWindow):
                dpg.add_theme_color(dpg.mvThemeCol_ChildBg, (51,51,55,255), category=dpg.mvThemeCat_Core)
                dpg.add_theme_color(dpg.mvThemeCol_Border, (51,51,55,255), category=dpg.mvThemeCat_Core)
    
    _register_themes()

    def _on_accept():
        # send some data back to caller
        _on_close()

    def _on_close():
        dpg.delete_item(ID_WINDOW_DIALOG)
        dpg.delete_item(ID_THEME_ICON_BUTTON)

    with dpg.window(tag=ID_WINDOW_DIALOG, 
                    label="Open",
                    no_close=False, modal=False, no_collapse=True,
                    width=560, height=310):
        
        with dpg.group(tag=ID_GROUP_CONTAINER, horizontal=False):
            with dpg.group(tag=ID_GROUP_HEADER, horizontal=True):
                dpg.add_button(arrow=True, direction=dpg.mvDir_Left)
                dpg.add_button(arrow=True, direction=dpg.mvDir_Right)
                dpg.add_button(arrow=True, direction=dpg.mvDir_Up)
                # dpg.add_input_text(default_value="Documents", width=-1)

                dpg.add_group(id=ID_GROUP_URL_BAR, horizontal=True)
                
                _update_breadcrumbs()
                dpg.bind_item_theme(ID_GROUP_URL_BAR, ID_THEME_NOSPACING)

            # dpg.add_separator()
            with dpg.group(tag=ID_GROUP_BODY, horizontal=True):
                
                # folder tree
                with dpg.child_window(tag=ID_WINDOW_TREELIST,
                                      width=142, height=200):
                    with dpg.group(horizontal=False, tag=ID_GROUP_TREELIST):
                    
                        _update_treelist(None, indent_level=0, path=None)
                        _update_treelist(None, indent_level=1, path="C:/")
                        _update_treelist(None, indent_level=1, path="D:/")
                
                # folder contents
                with dpg.child_window(tag=ID_WINDOW_LISTDIR, width=-1, height=200):
                    
                    dpg.add_group(id=ID_GROUP_LISTDIR, horizontal=False)
                    _update_listdir()
                
                dpg.bind_item_theme(ID_WINDOW_TREELIST, ID_THEME_LISTBOX)
                dpg.bind_item_theme(ID_WINDOW_LISTDIR, ID_THEME_LISTBOX)

            # set theming here to add a gap
            with dpg.group(tag=ID_GROUP_FILENAME, horizontal=True):
                dpg.add_text("File name:")
                dpg.add_input_text(width=-100)
                dpg.add_combo(items=('.csv', '.xlsx'), default_value='.csv', width=-1)
            with dpg.group(tag=ID_GROUP_FOOTER, horizontal=True):
                dpg.add_button(tag=ID_BUTTON_ACCEPT, label="Accept", callback=_on_accept)
                dpg.add_button(tag=ID_BUTTON_CANCEL, label="Cancel", callback=_on_close)
                            



dpg.create_context()
dpg.create_viewport(title='Custom Title', width=800, height=600)
dpg.setup_dearpygui()

def load_textures():
    with dpg.texture_registry():
        for tex_info in TextureIds.get_tex_info():
            w_h_c_data = dpg.load_image(tex_info.PATH)
            if(w_h_c_data == None):
                raise Exception("Failed to load image, check current working directory is project folder.")
            width, height, channels, im_data = w_h_c_data
            dpg.add_static_texture(width=width, height=height, default_value=im_data, tag=tex_info.UUID)

load_textures()

with dpg.window(tag="window", width=700, height=400):
    
    dpg.add_button(label="Open File", callback=fileOpenDialog)

dpg.show_viewport()
# dpg.show_style_editor()

while dpg.is_dearpygui_running():
    
    dpg.render_dearpygui_frame()

dpg.destroy_context()