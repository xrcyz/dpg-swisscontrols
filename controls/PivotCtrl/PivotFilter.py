import dearpygui.dearpygui as dpg
from typing import List, Tuple, Callable
from enum import Enum

from controls.DpgHelpers.MvItemTypes import MvItemTypes
from controls.DpgHelpers.MvStyleVar import MvStyleVar
from controls.Textures.TextureIds import TextureIds

def pivotFilterDialog(title: str, field: str, data: List[Tuple[bool, str]], send_data: Callable[[List[Tuple[bool, str]]], None]):
    """
    :param data: A list of [checkbox state, item label] pairs
    :param callback: Callback to send back the user selection

    TODO: 
    - change Tuple[bool, str] to a dataclass
    - dynamically set the checkbox size
        - checkbox_size = font_size + 2*frame_padding
    """
    
    ID_MODAL = dpg.generate_uuid()
    ID_HEADER = dpg.generate_uuid()
    ID_CHILD_WINDOW = dpg.generate_uuid()
    ID_TABBAR = dpg.generate_uuid()
    ID_TAB_LIST = dpg.generate_uuid()
    ID_TAB_RANGE = dpg.generate_uuid()
    ID_OK = dpg.generate_uuid()
    ID_WINDOW_HANDLER = dpg.generate_uuid()

    TEX_PARTIAL_CHECK = TextureIds.ID_PARTIAL_CHECK.UUID
    ID_MCB_CHECKBOX = dpg.generate_uuid()
    ID_MCB_LABEL = dpg.generate_uuid()
    ID_CHECKBOX_THEME = dpg.generate_uuid()

    ID_SCRIPT_INPUT = dpg.generate_uuid()

    child_checkboxes = []

    # resize the child window on resize modal window
    def resize_window(sender, data):
        windowHeight = dpg.get_item_height(ID_MODAL)
        windowWidth = dpg.get_item_width(ID_MODAL)

        dpg.configure_item(ID_CHILD_WINDOW, height = windowHeight - 95)
        dpg.configure_item(ID_SCRIPT_INPUT, width = windowWidth - 4*MvStyleVar.WindowPadding.value)

        pos = [dpg.get_item_width(ID_MODAL) - 75*2-16, dpg.get_item_height(ID_MODAL) - 30]
        dpg.configure_item(ID_OK, pos = pos)

    # get theme for partial checkbox
    with dpg.theme(tag=ID_CHECKBOX_THEME):
        with dpg.theme_component(dpg.mvImageButton):
            # remove frame padding around image button
            dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 0, 0)

    def on_mcb_click(sender):
        # on master checkbox click
        for ccb in child_checkboxes:
            dpg.set_value(ccb[0], dpg.get_value(sender))

    def on_mcb_check(init_state=True):
        # set ID_MCB_CHECKBOX to a checkbox
        if dpg.does_item_exist(ID_MCB_CHECKBOX):
            dpg.delete_item(ID_MCB_CHECKBOX)
        
        # print(init_state)
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
            dpg.add_image_button(before=ID_MCB_LABEL, tag=ID_MCB_CHECKBOX, texture_tag=TEX_PARTIAL_CHECK, height=19, width=19, callback=lambda: on_mcb_check(init_state=True), show=True)
            dpg.bind_item_theme(ID_MCB_CHECKBOX, ID_CHECKBOX_THEME)

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
            dpg.add_image_button(before=ID_MCB_LABEL, tag=ID_MCB_CHECKBOX, texture_tag=TEX_PARTIAL_CHECK, height=19, width=19, callback=lambda: on_mcb_check(init_state=True), show=True)
            dpg.bind_item_theme(ID_MCB_CHECKBOX, ID_CHECKBOX_THEME)

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
                dpg.add_text(field)
                dpg.add_combo(items=["is in", "is not in"], default_value="is in", width=100)
                # summary_checked = dpg.add_text("[2022, 2023]")
            # summary_checked = dpg.add_text("[2022, 2023]", wrap=195)
        
        # method to update displayed text
        # def checked_callback(sender):
        #     checked_items = [dpg.get_value(e[1]) for e in child_checkboxes if dpg.get_value(e[0])]
        #     display_text = f'[{", ".join(checked_items) }]'
        #     dpg.set_value(summary_checked, display_text)

        with dpg.child_window(tag=ID_CHILD_WINDOW):
            
            with dpg.tab_bar(tag=ID_TABBAR):
                # categorical filtering
                with dpg.tab(tag=ID_TAB_LIST, label="List", closable=False):
                    # master checkbox
                    with dpg.group(horizontal=True):
                        dpg.add_text("All Items", tag=ID_MCB_LABEL)
                        on_mcb_init() # inserts checkbox before 'All Items'
                        
                    # child checkboxes
                    dpg.add_separator()
                    for [checkbox_state, item_label] in data:
                        with dpg.group(horizontal=True):
                            b = dpg.add_checkbox(default_value=checkbox_state, callback=on_ccb_click)
                            t = dpg.add_text(item_label)
                            child_checkboxes.append((b, t))

                # range filtering
                with dpg.tab(tag=ID_TAB_RANGE, label="Range", closable=False):
                    with dpg.group(horizontal=True):
                        my_expr = "0 <= x < 100"
                        dpg.add_input_text(tag=ID_SCRIPT_INPUT, default_value=my_expr, multiline=True, height=100) # , 
                    

        def on_ok():
            # somehow we've got to return a lambda to the PivotBroker from the Range tab
            # so maybe we convert the checklist to a lambda?
            # df['Year'].isin(['2022', '2023']) doesn't sound that hard tbh.
            # otherwise we have to support two return methods
            # which is doable, we just have two callbacks in the method call.
            # we also need some guards around the field type to disable range filtering on sets
            # and consider whether this code is shared with range filters on value fields
            # maybe instead of `field: str` we have `field: PivotFilterField`
            # aaaand we have to send back some text to update the button sender

            if dpg.get_value(ID_TABBAR) == ID_TAB_LIST:
                # return from checklist tab
                # gather the data
                ret = [(dpg.get_value(e[0]), dpg.get_value(e[1])) for e in child_checkboxes]
                # delete the dialog
                on_cancel()
                # send the data
                send_data(ret)
            else: 
                # return from range tab
                ret = [(dpg.get_value(e[0]), dpg.get_value(e[1])) for e in child_checkboxes]
                # delete the dialog
                on_cancel()
                # send the data
                send_data(ret)

        def on_cancel():
            # delete the window and all children
            dpg.delete_item(ID_MODAL)
            # delete the resize callback handler
            dpg.delete_item(ID_WINDOW_HANDLER)
            # delete the checkbox theme
            dpg.delete_item(ID_CHECKBOX_THEME)
            # do not delete the texture - that is not our job
        
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

