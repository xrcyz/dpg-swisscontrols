import dearpygui.dearpygui as dpg
import os

from dataclasses import dataclass

from controls.DpgHelpers.MvThemeCol import MvThemeCol
from controls.DpgHelpers.MvStyleVar import MvStyleVar
from controls.Textures.TextureIds import TextureIds

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

    ID_FILE_OPEN_DIALOG = dpg.generate_uuid()
    ID_GROUP_CONTAINER = dpg.generate_uuid()
    ID_GROUP_HEADER = dpg.generate_uuid()
    ID_GROUP_URL_BAR = dpg.generate_uuid()
    ID_GROUP_BODY = dpg.generate_uuid()
    ID_GROUP_FILENAME = dpg.generate_uuid()
    ID_GROUP_FOOTER = dpg.generate_uuid()
    ID_WINDOW_TREELIST = dpg.generate_uuid()
    ID_WINDOW_LISTBOX = dpg.generate_uuid()

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
        dpg.delete_item(ID_FILE_OPEN_DIALOG)
        dpg.delete_item(ID_THEME_ICON_BUTTON)

    with dpg.window(tag=ID_FILE_OPEN_DIALOG, 
                    label="Open",
                    no_close=False, modal=False, no_collapse=True,
                    width=426, height=310):
        
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
                    with dpg.group(horizontal=False):
                    
                        with dpg.group(horizontal=True):
                            dpg.add_image_button(texture_tag=ID_TEX_FOLDER_ICON, height=19, width=19)
                            dpg.bind_item_theme(dpg.last_item(), ID_THEME_ICON_BUTTON)
                            dpg.add_button(label="This PC:")
                            dpg.bind_item_handler_registry(dpg.last_item(), ID_HANDLER_DOUBLE_CLICK)
                        with dpg.group(horizontal=True):
                            dpg.add_image_button(texture_tag=ID_TEX_FOLDER_ICON, height=19, width=19, indent=8)
                            dpg.bind_item_theme(dpg.last_item(), ID_THEME_ICON_BUTTON)
                            dpg.add_button(label="(D:)")
                            dpg.bind_item_handler_registry(dpg.last_item(), ID_HANDLER_DOUBLE_CLICK)
                        with dpg.group(horizontal=True):
                            dpg.add_image_button(texture_tag=ID_TEX_FOLDER_ICON, height=19, width=19, indent=16)
                            dpg.bind_item_theme(dpg.last_item(), ID_THEME_ICON_BUTTON)
                            dpg.add_button(label="Documents")
                            dpg.bind_item_handler_registry(dpg.last_item(), ID_HANDLER_DOUBLE_CLICK)
                        with dpg.group(horizontal=True):
                            dpg.add_image_button(texture_tag=ID_TEX_FOLDER_ICON, height=19, width=19, indent=16)
                            dpg.bind_item_theme(dpg.last_item(), ID_THEME_ICON_BUTTON)
                            dpg.add_button(label="Projects")
                            dpg.bind_item_handler_registry(dpg.last_item(), ID_HANDLER_DOUBLE_CLICK)
                
                
                items = list_files_and_folders(current_path)

                # folder contents
                with dpg.child_window(tag=ID_WINDOW_LISTBOX, width=-1, height=200):
                    
                    # dpg.add_listbox(items, num_items=9, width=-1)
                    with dpg.group(horizontal=False):
                        for item in items:
                            dpg.add_selectable(label=item)
                
                dpg.bind_item_theme(ID_WINDOW_TREELIST, ID_THEME_LISTBOX)
                dpg.bind_item_theme(ID_WINDOW_LISTBOX, ID_THEME_LISTBOX)

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
dpg.show_style_editor()

while dpg.is_dearpygui_running():
    
    dpg.render_dearpygui_frame()

dpg.destroy_context()