
import dearpygui.dearpygui as dpg
import numpy as np 
from controls.CheckListCtrl.CheckListCtrl import checkListCtrl

data = []
for i in range(12):
    data.append((True, f"Item {i}"))

user_sel = []

def get_user_selection(user_sel):
    print(user_sel)

dpg.create_context()
dpg.create_viewport(title='Custom Title', width=800, height=600)
dpg.setup_dearpygui()

with dpg.window(tag="window", width=700, height=400):
    
    dpg.add_button(label="Select", tag=dpg.generate_uuid(), callback=lambda: checkListCtrl("Select items", data, get_user_selection))

dpg.show_viewport()

while dpg.is_dearpygui_running():
    
    dpg.render_dearpygui_frame()

dpg.destroy_context()