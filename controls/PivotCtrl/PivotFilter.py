import dearpygui.dearpygui as dpg
from MvItemTypes import MvItemTypes
from typing import List, Tuple, Callable
from enum import Enum

def pivotFilterDialog(title: str, data: List[Tuple[bool, str]], send_data: Callable[[List[Tuple[bool, str]]], None]):
    """
    :param data: A list of [checkbox state, item label] pairs
    :param callback: Callback to send back the user selection
    """
    
    ID_MODAL = dpg.generate_uuid()
    ID_HEADER = dpg.generate_uuid()
    ID_CHILD_WINDOW = dpg.generate_uuid()
    ID_OK = dpg.generate_uuid()
    ID_WINDOW_HANDLER = dpg.generate_uuid()

    TEX_BASE = dpg.generate_uuid()
    ID_MCB_CHECKBOX = dpg.generate_uuid()
    ID_MCB_LABEL = dpg.generate_uuid()
    custom_checkbox_theme = dpg.generate_uuid()

    child_checkboxes = []

    #if I move this line down to `with dpg.texture_registry()`, then it fails to resolve..........????
    
    # print(w_h_c_data)
    # import os
    # print(os.getcwd())

    # resize the child window on resize modal window
    def resize_window(sender, data):
        windowHeight = dpg.get_item_height(ID_MODAL)
        dpg.configure_item(ID_CHILD_WINDOW, height = windowHeight - 95)

        pos = [dpg.get_item_width(ID_MODAL) - 75*2-16, dpg.get_item_height(ID_MODAL) - 30]
        dpg.configure_item(ID_OK, pos = pos)

    # get texture for partial checkbox
    with dpg.texture_registry():
        w_h_c_data = dpg.load_image("controls/assets/partial_check.png")
        if(w_h_c_data == None):
            raise Exception("Failed to load image, check current working directory is project folder.")
        width, height, channels, im_data = w_h_c_data
        dpg.add_static_texture(width=width, height=height, default_value=im_data, tag=TEX_BASE)
    
    # get theme for partial checkbox
    with dpg.theme(tag=custom_checkbox_theme):
        with dpg.theme_component(dpg.mvImageButton):
            dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 0, 0)

    def on_mcb_click(sender):
        # on master checkbox click
        for ccb in child_checkboxes:
            dpg.set_value(ccb[0], dpg.get_value(sender))

    def on_mcb_check(init_state=True):
        # set ID_MCB_CHECKBOX to a checkbox
        if dpg.does_item_exist(ID_MCB_CHECKBOX):
            dpg.delete_item(ID_MCB_CHECKBOX)
        
        dpg.add_checkbox(before=ID_MCB_LABEL, tag=ID_MCB_CHECKBOX, default_value=init_state, callback=on_mcb_click)

        for ccb in child_checkboxes:
            dpg.set_value(ccb[0], init_state)
    
    def on_mcb_init():
        # on first call, figure out whether to be checkbox or imagebutton
        # this method could potentially be merged with on_ccb_click
        set_checked = all(e[0] for e in data)
        set_unchecked = not any(e[0] for e in data)
        if set_checked or set_unchecked:
            on_mcb_check(set_checked)
        else:
            dpg.add_image_button(before=ID_MCB_LABEL, tag=ID_MCB_CHECKBOX, texture_tag=TEX_BASE, height=19, width=19, callback=on_mcb_check, show=True)
            dpg.bind_item_theme(ID_MCB_CHECKBOX, custom_checkbox_theme)

    def on_ccb_click():
        # on child checkbox click

        set_checked = all(dpg.get_value(e[0]) for e in child_checkboxes)
        set_unchecked = not any(dpg.get_value(e[0]) for e in child_checkboxes)

        # if all children are checked, check master
        if set_checked or set_unchecked:
            if(dpg.get_item_type(ID_MCB_CHECKBOX) == MvItemTypes.Checkbox.value):
                dpg.set_value(ID_MCB_CHECKBOX, set_checked)
            else:
                on_mcb_check(set_checked)
        else:
            dpg.delete_item(ID_MCB_CHECKBOX)
            dpg.add_image_button(before=ID_MCB_LABEL, tag=ID_MCB_CHECKBOX, texture_tag=TEX_BASE, height=19, width=19, callback=on_mcb_check, show=True)
            dpg.bind_item_theme(ID_MCB_CHECKBOX, custom_checkbox_theme)

    # build dialog
    with dpg.window(label=title, 
                    tag=ID_MODAL,
                    modal=True, 
                    show=True, 
                    no_title_bar=True, 
                    pos=dpg.get_mouse_pos(local=False), 
                    width=210, 
                    height=320):

        with dpg.group(tag=ID_HEADER, horizontal=False):
            with dpg.group(horizontal=True):
                dpg.add_text("Year")
                dpg.add_combo(items=["is in", "is not in"], default_value="is in", width=100)
                # summary_checked = dpg.add_text("[2022, 2023]")
            summary_checked = dpg.add_text("[2022, 2023]", wrap=195)
        
        # method to update displayed text
        def checked_callback(sender):
            checked_items = [dpg.get_value(e[1]) for e in child_checkboxes if dpg.get_value(e[0])]
            display_text = f'[{", ".join(checked_items) }]'
            dpg.set_value(summary_checked, display_text)

        # dpg.add_separator()
        with dpg.child_window(tag=ID_CHILD_WINDOW):
            # master checkbox
            with dpg.group(horizontal=True):
                # dpg.add_checkbox(default_value=False, tag=ID_MCB_CHECKBOX)
                dpg.add_text("All Items", tag=ID_MCB_LABEL)
                on_mcb_init()
                
            # child checkboxes
            dpg.add_separator()
            for [checkbox_state, item_label] in data:
                with dpg.group(horizontal=True):
                    b = dpg.add_checkbox(default_value=checkbox_state, callback=on_ccb_click)
                    t = dpg.add_text(item_label)
                    child_checkboxes.append((b, t))


        def on_ok():
            ret = [(dpg.get_value(e[0]), dpg.get_value(e[1])) for e in child_checkboxes]
            send_data(ret)
            dpg.delete_item(ID_MODAL)

        def on_cancel():
            dpg.delete_item(ID_MODAL)
            dpg.delete_item(ID_WINDOW_HANDLER)

            # delete custom theme
            # deregister texture
        
        with dpg.group(horizontal=True):
            # TODO figure out how to get element heights
            # print("---")
            # print(dpg.get_item_pos(ID_CHILD_WINDOW))
            # print(dpg.get_item_height(ID_CHILD_WINDOW))
            # print("---")
            pos = [dpg.get_item_width(ID_MODAL) - 75*2-16, dpg.get_item_height(ID_MODAL) - 30]
            dpg.add_button(tag=ID_OK, label="Accept", width=75, callback=on_ok, pos=pos)
            dpg.add_button(label="Cancel", width=75, callback=on_cancel)
                
    # register the resize method to ID_MODAL
    with dpg.item_handler_registry(tag=ID_WINDOW_HANDLER):
        dpg.add_item_resize_handler(callback=resize_window)
    dpg.bind_item_handler_registry(ID_MODAL, ID_WINDOW_HANDLER)


    return

