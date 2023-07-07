
import dearpygui.dearpygui as dpg
import numpy as np 

from controls.ListEditCtrl.DataGrid import DataGrid
from controls.ListEditCtrl.ListEditCtrl import listEditCtrl

commit_grid = DataGrid(
    title="Commit History",
    columns = ["User", "Comment"],
    dtypes = [DataGrid.COMBO, DataGrid.TXT_STRING],
    defaults = [0, ""],
    combo_lists = [["Jane", "Tom", "Peter"], None]
)
commit_grid.append([0, "First commit"])

ticket_grid = DataGrid(
    title="Ticket System",
    columns = ['Closed', 'Ticket', 'Status', 'Color', 'Commits'],
    dtypes = [DataGrid.CHECKBOX, DataGrid.TXT_STRING, DataGrid.COMBO, DataGrid.COLOR, DataGrid.GRID],
    defaults = [False, "New Ticket", 0, (30, 179, 120, 128), commit_grid],
    combo_lists = [None, None, ["Avacado", "Banana", "Lemon", "Pear"], None, None]
)

ticket_grid.append([True, "Create table", 0, [212, 98, 223, 128], commit_grid])
ticket_grid.append([True, "Create data structure", 1, [48, 145, 213, 128], commit_grid])
ticket_grid.append([True, "Do callbacks", 2, [220, 165, 65, 128], commit_grid])

dpg.create_context()
dpg.create_viewport(title='Custom Title', width=800, height=600)
dpg.setup_dearpygui()

with dpg.window(tag="window", width=700, height=400):
    
    id_fruits = dpg.generate_uuid()
    eval_grid = listEditCtrl(id_fruits, grid=ticket_grid)

    dpg.add_button(label="Submit", tag=dpg.generate_uuid(), callback=lambda: print(eval_grid().display()))

dpg.show_viewport()

while dpg.is_dearpygui_running():
    
    dpg.render_dearpygui_frame()

dpg.destroy_context()