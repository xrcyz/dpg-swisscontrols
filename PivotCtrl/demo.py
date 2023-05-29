
import dearpygui.dearpygui as dpg
import pandas as pd
import numpy as np
from PivotCtrl import pivotCtrl

dpg.create_context()
dpg.create_viewport(title='Custom Title', width=800, height=600)
dpg.setup_dearpygui()

with dpg.window(tag="window", width=700, height=400):
    
    id_fruits = dpg.generate_uuid()
    pivotCtrl(id_fruits)

dpg.show_viewport()

while dpg.is_dearpygui_running():
    
    dpg.render_dearpygui_frame()

dpg.destroy_context()