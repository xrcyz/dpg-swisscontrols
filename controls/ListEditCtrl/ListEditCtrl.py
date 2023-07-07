from typing import List, Dict, Tuple, Callable
import dearpygui.dearpygui as dpg
from controls.ListEditCtrl.DataGrid import DataGrid
from controls.ListEditCtrl.TableHelpers import swap_row_values

def listEditCtrlDialog(grid: DataGrid, send_grid: Callable[[DataGrid], None]):
    """
    Creates a ListEditCtrl dialog.

    :param grid: The input data source for the control. 
    :param send_grid: Callback method to the parent control. 
    """    
    # TODO - change tag to support a dialog within a dialog
    with dpg.window(label="Modal Dialog", 
                    modal=True, 
                    show=True, 
                    no_title_bar=True, 
                    pos=dpg.get_mouse_pos(local=False), 
                    width=430, 
                    height=400) as id_modal:
        
        table_id = dpg.generate_uuid()
        get_grid = listEditCtrl(table_id, grid, height=360)

        def on_ok():
            send_grid(get_grid())
            dpg.delete_item(id_modal)

        with dpg.group(horizontal=True):
            dpg.add_button(label="Accept", width=75, callback=on_ok)
            dpg.add_button(label="Cancel", width=75, callback=lambda: dpg.delete_item(id_modal))


def listEditCtrl(table_id, grid: DataGrid, height=-1, **kwargs):
    """
    Creates a ListEditCtrl widget.

    :param table_id: The ID for the table.
    :param grid: The input data source for the control. 
    """    

    def _grid_ref():
        nonlocal grid
        # print(grid.data)
        return grid

    def _subgrid_callback(col_idx, row_idx, new_grid: DataGrid):
            """
            Callback method for child grids to update their data in the parent grid.
            """
            nonlocal grid
            # print(f"col_idx: {col_idx}")
            # print(f"row_idx: {row_idx}")
            grid.data[col_idx][row_idx] = new_grid

    def _add_row(use_defaults=True): 
        """
        Adds a new row to the DataGrid. 

        :param use_defaults: A boolean indicating whether to use default values for the new row. 
            If False, it uses the data from the corresponding row in the underlying DataGrid.

        This function creates a new row in the DataGrid and populates it with widgets appropriate for each column's 
        data type. The widgets are initialized with either default values (if use_defaults=True) or with the 
        corresponding data from the underlying DataGrid (if use_defaults=False).

        It uses the _set_focus callback to update the selected row index when any widget in the new row is clicked.

        If a new row is added that exceeds the current number of rows in the underlying DataGrid, 
        the DataGrid is expanded with a row of default values.

        TODO:
        1. Insertion of rows in the middle of the grid is currently not supported. Implement functionality to support 
        insertion into arbitrary positions in the grid.
        2. The row index is not currently passed to the callback functions for the individual widgets. Modify the 
        callbacks to accept the row index as an input. This will enable the callbacks to modify specific rows 
        in the DataGrid based on user interaction.

        :raises ValueError: If a column has an unsupported data type.
        """
        nonlocal grid
        nonlocal table_id
        nonlocal focus_index

        row_idx = len(dpg.get_item_children(table_id)[1])

        # if the row_idx is greater than the grid length, then expand the grid
        if row_idx >= grid.shape[0]:
            grid.append(grid.defaults)

        if focus_index < 0:
            focus_index = 0

        # need to feed in the row index for the callbacks
        with dpg.table_row(parent = table_id) as row_id:

            dpg.add_table_cell()

            for col_idx in range(len(grid.columns)):
                row = grid.defaults if use_defaults else _grid_ref().get_row(row_idx) # TODO grid.defaults if row_idx==None or row_idx >= grid.shape[0]

                if grid.dtypes[col_idx] == DataGrid.CHECKBOX:
                    dpg.add_checkbox(callback=_set_focus, 
                                     default_value=row[col_idx], 
                                     user_data=row_id)
                elif grid.dtypes[col_idx] == DataGrid.TXT_STRING:
                    id_input_text = dpg.generate_uuid()
                    dpg.add_input_text(tag=id_input_text, 
                                       default_value=row[col_idx], 
                                       hint="enter text here", width=200, callback=_set_focus, user_data=row_id)
                    _register_widget_click(id_input_text, row_id)
                elif grid.dtypes[col_idx] == DataGrid.COMBO:
                    id_input_combo = dpg.generate_uuid()
                    dpg.add_combo(tag=id_input_combo, 
                                  items=grid.combo_lists[col_idx], 
                                  default_value=grid.combo_lists[col_idx][row[col_idx]], 
                                  no_preview=False, width=200, callback=_set_focus, user_data=row_id)
                    _register_widget_click(id_input_combo, row_id)
                elif grid.dtypes[col_idx] == DataGrid.COLOR:
                    id_color_pikr = dpg.generate_uuid()
                    dpg.add_color_edit(tag=id_color_pikr, 
                                       default_value=row[col_idx], 
                                       no_inputs=True, callback=_set_focus, user_data=row_id)
                    _register_widget_click(id_color_pikr, row_id)
                elif grid.dtypes[col_idx] == DataGrid.GRID:
                    id_button = dpg.generate_uuid()

                    dpg.add_button(tag=id_button,
                                   label="Configure", 
                                   callback=lambda: listEditCtrlDialog(grid=_grid_ref().data[col_idx][row_idx], send_grid=lambda new_grid: _subgrid_callback(col_idx, row_idx, new_grid)),
                                   user_data=row_id)
                else:
                    raise ValueError("unsupported data type")
                
            # close out the row
            dpg.add_selectable(height=20, span_columns=True, callback=_set_focus, user_data=row_id)

        

    def _delete_row():
        nonlocal focus_index
        nonlocal table_id
        if focus_index < 0:
            return
        
        # delete the row from DPG
        row_id = dpg.get_item_children(table_id)[1][focus_index]
        dpg.delete_item(row_id)

        # delete the row from the grid
        grid.drop(focus_index)

        # move the focus_index up if list length is less than focus_index
        if(focus_index >= len(dpg.get_item_children(table_id)[1])):
            focus_index -= 1
        # call _set_focus on the current index
        if(focus_index >= 0):
            dpg.highlight_table_row(table_id, focus_index, [15,86,135])

    def _move_row_up():
        nonlocal focus_index
        nonlocal table_id

        row_ids = dpg.get_item_children(table_id, 1)
        if (focus_index == 0) or (len(row_ids) <= 1):
            return False
        
        swap_row_values(table_id, focus_index, focus_index-1)
        grid.swap_rows(focus_index, focus_index-1) 

        dpg.unhighlight_table_row(table_id, focus_index)
        focus_index -= 1
        dpg.highlight_table_row(table_id, focus_index, [15,86,135])

        return True

    def _move_row_down():
        nonlocal focus_index
        nonlocal table_id

        row_ids = dpg.get_item_children(table_id, 1)
        if (focus_index == len(row_ids)-1) or (len(row_ids) <= 1):
            return False
        
        swap_row_values(table_id, focus_index, focus_index+1)
        grid.swap_rows(focus_index, focus_index+1)

        dpg.unhighlight_table_row(table_id, focus_index)
        focus_index += 1
        dpg.highlight_table_row(table_id, focus_index, [15,86,135])

        return True

    focus_index=0
    def _set_focus(sender, app_data, user_data): # TODO fix this method sig or rename `_set_focus_from_widget`
        if (dpg.get_item_type(sender) == "mvAppItemType::mvSelectable"):
            dpg.set_value(sender, False)
        nonlocal focus_index
        nonlocal table_id
        dpg.unhighlight_table_row(table_id, focus_index)
        table_children = dpg.get_item_children(table_id, 1)
        focus_index = table_children.index(user_data)
        dpg.highlight_table_row(table_id, focus_index, [15,86,135])
    
    def _on_widget_click(row_id):  
            nonlocal focus_index
            nonlocal table_id
            dpg.unhighlight_table_row(table_id, focus_index)
            # this is slow but good enough for prototyping
            table_children = dpg.get_item_children(table_id, 1)
            focus_index = table_children.index(row_id)
            # print(table_children, row_id, focus_index)
            dpg.highlight_table_row(table_id, focus_index, [15,86,135])
            # highlight_row(table_id, focus_index)

    def _register_widget_click(sender, row_id):
        handler_tag = f"{row_id} handler"
        if not dpg.does_item_exist(handler_tag):
            with dpg.item_handler_registry(tag=handler_tag) as handler:
                dpg.add_item_clicked_handler(callback=lambda x: _on_widget_click(row_id)) 

        dpg.bind_item_handler_registry(sender, handler_tag)

    with dpg.child_window(menubar=True, height=height):
        with dpg.menu_bar():
                    dpg.add_text(grid.title)
        with dpg.group(horizontal=True):
            dpg.add_button(label="Add", tag=dpg.generate_uuid(), callback=lambda: _add_row(use_defaults=True))
            dpg.add_button(label="Remove", tag=dpg.generate_uuid(), callback=_delete_row)
            dpg.add_button(arrow=True, direction=dpg.mvDir_Up, callback=_move_row_up)
            dpg.add_button(arrow=True, direction=dpg.mvDir_Down, callback=_move_row_down)
        with dpg.child_window():
            with dpg.table(tag=table_id, header_row=True, resizable=True, policy=dpg.mvTable_SizingFixedFit, #mvTable_SizingStretchProp
                           row_background=False, no_host_extendX=True, no_pad_innerX=True,
                           borders_outerH=True, borders_innerV=True, borders_outerV=True):

                dpg.add_table_column() # index column
                for col in grid.columns:
                    dpg.add_table_column(label=col)
                dpg.add_table_column() # selector column

                for i in range(len(grid.data[0])):
                    _add_row(use_defaults=False)

    def evaluate_grid():
        nonlocal grid
        # create a new grid of the same structure
        new_grid = grid.empty_like()
        
        # populate the grid from the table
        for row_idx, row_id in enumerate(dpg.get_item_children(table_id)[1]):
            new_row = []
            cells = list(dpg.get_item_children(row_id)[1])
            for col_idx, col_id in enumerate(cells[1:-1]):  # Skip the first and last cell.
                if grid.dtypes[col_idx] == DataGrid.GRID:
                    # Get subgrid from grid
                    new_row.append(grid.get_cell(col_idx, row_idx))
                elif grid.dtypes[col_idx] == DataGrid.COMBO:
                    selection = dpg.get_value(col_id)
                    idx = grid.combo_lists[col_idx].index(selection)
                    new_row.append(idx)
                else:
                    # Get the value in the cell and append it to the new row.
                    new_row.append(dpg.get_value(col_id))
            # Add the new row to the data in the new grid.
            new_grid.append(new_row)

        return new_grid

    return evaluate_grid

