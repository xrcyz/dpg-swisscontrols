import dearpygui.dearpygui as dpg
from typing import List, Tuple, Callable


def listSelectCtrl(data: List[Tuple[bool, str]], send_data: Callable[[List[Tuple[bool, str]]], None]):
    """
    :param data: A list of [checkbox state, item label] pairs
    :param callback: Callback to send back the user selection
    """
    with dpg.window(label="Modal Dialog", 
                    modal=True, 
                    show=True, 
                    no_title_bar=True, 
                    pos=dpg.get_mouse_pos(local=False), 
                    width=430, 
                    height=400) as id_modal:
        
        state = []

        dpg.add_text("Select items")
        dpg.add_separator()
        with dpg.child_window(height=330):
            for [checkbox_state, item_label] in data:
                with dpg.group(horizontal=True):
                    b = dpg.add_checkbox(default_value=checkbox_state)
                    t = dpg.add_text(item_label)
                    state.append((b, t))

        def on_ok():
            ret = [(dpg.get_value(e[0]), dpg.get_value(e[1])) for e in state]
            send_data(ret)
            dpg.delete_item(id_modal)

        with dpg.group(horizontal=True):
            dpg.add_button(label="Accept", width=75, callback=on_ok)
            dpg.add_button(label="Cancel", width=75, callback=lambda: dpg.delete_item(id_modal))


    return

