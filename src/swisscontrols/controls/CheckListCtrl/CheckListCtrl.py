import dearpygui.dearpygui as dpg
from typing import List, Tuple, Callable

"""
TODO
- pull the checklist stuff out of PivotFilter.py and into here as CheckListWidget
- wrap PivotFilter.py around CheckListWidget

"""

def checkListCtrl(title: str, data: List[Tuple[bool, str]], send_data: Callable[[List[Tuple[bool, str]]], None]):
    """
    :param data: A list of [checkbox state, item label] pairs
    :param callback: Callback to send back the user selection
    """
    ID_MODAL = dpg.generate_uuid()
    ID_CHILD_WINDOW = dpg.generate_uuid()
    ID_OK = dpg.generate_uuid()
    ID_WINDOW_HANDLER = dpg.generate_uuid()

    # resize the child window on resize modal window
    def resize_window(sender, data):
        windowHeight = dpg.get_item_height(ID_MODAL)
        dpg.configure_item(ID_CHILD_WINDOW, height = windowHeight - 70)

        pos = [dpg.get_item_width(ID_MODAL) - 75*2-16, dpg.get_item_height(ID_MODAL) - 30]
        dpg.configure_item(ID_OK, pos = pos)


    with dpg.window(label=title, 
                    tag=ID_MODAL,
                    modal=True, 
                    show=True, 
                    no_title_bar=True, 
                    pos=dpg.get_mouse_pos(local=False), 
                    width=210, 
                    height=320):
        
        state = []

        dpg.add_text("Select items")
        dpg.add_separator()
        with dpg.child_window(tag=ID_CHILD_WINDOW, height=250):
            for [checkbox_state, item_label] in data:
                with dpg.group(horizontal=True):
                    b = dpg.add_checkbox(default_value=checkbox_state)
                    t = dpg.add_text(item_label)
                    state.append((b, t))

        def on_ok():
            ret = [(dpg.get_value(e[0]), dpg.get_value(e[1])) for e in state]
            send_data(ret)
            dpg.delete_item(ID_MODAL)

        def on_cancel():
            dpg.delete_item(ID_MODAL)
            dpg.delete_item(ID_WINDOW_HANDLER)

        with dpg.group(horizontal=True):
            pos = [dpg.get_item_width(ID_MODAL) - 75*2-16, dpg.get_item_height(ID_MODAL) - 30]
            dpg.add_button(tag=ID_OK, label="Accept", width=75, callback=on_ok, pos=pos)
            dpg.add_button(label="Cancel", width=75, callback=on_cancel)
    
    # register the resize method to ID_MODAL
    with dpg.item_handler_registry(tag=ID_WINDOW_HANDLER):
        dpg.add_item_resize_handler(callback=resize_window)
    dpg.bind_item_handler_registry(ID_MODAL, ID_WINDOW_HANDLER)

    return

