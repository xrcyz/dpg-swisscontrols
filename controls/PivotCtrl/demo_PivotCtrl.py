
import dearpygui.dearpygui as dpg
import pandas as pd
import numpy as np
import itertools
import dataclasses
from DataSource import get_pivot_data
from GridSelector import GridSelector
from PivotBroker import PivotBroker
from ListSelectCtrl import listSelectCtrl

from enum import Enum

class MvItemTypes(Enum):
    Button = 'mvAppItemType::mvButton'
    Text = 'mvAppItemType::mvText'
    # Add other item types as needed

# print(f"Test: {MvItemTypes.Button.value == 'mvAppItemType::mvButton'}")

dpg.create_context()
dpg.create_viewport(title='Custom Title', width=800, height=600)
dpg.setup_dearpygui()

ID_PIVOT_PARENT = dpg.generate_uuid()
ID_FIELDLIST = dpg.generate_uuid()
ID_ROWSLIST = dpg.generate_uuid()
ID_COLSLIST = dpg.generate_uuid()
ID_DATALIST = dpg.generate_uuid()
ID_GRID_SELECT = dpg.generate_uuid()
ID_PIVOT_TABLE = dpg.generate_uuid()

pivotBroker = PivotBroker()
df = pivotBroker.get_pivot(filter=None, 
                           rows=['Year', 'Quarter'], # '(Data)', 
                           cols=['Fruit', 'Shape', '(Data)'],
                           aggs=['Volume', 'Weight'])

# print(df)
# print(df.columns)
# print(df.shape)
# print(df.index)

def get_column_map(df):
    """
    Get a mapping from hierarchical column levels to DataFrame column indices.

    Args:
    df (pandas.DataFrame): The DataFrame to map.

    Returns:
    dict: A nested dictionary where the keys at each level correspond to the
    values at each level of the DataFrame's columns. The values at the deepest
    level are the indices of the corresponding columns in the DataFrame.
    """

    # Initialize an empty dictionary
    lookup = {}

    # Iterate over the DataFrame's columns
    for i, col in enumerate(df.columns):

        # Extract the values at each level of the column
        level_values = col[:len(df.columns.names)]
        
        # Traverse the lookup dictionary, creating new dictionaries as needed
        current_dict = lookup
        for value in level_values[:-1]:
            if value not in current_dict:
                current_dict[value] = {}
            current_dict = current_dict[value]

        # Add the final level to the lookup dictionary
        if level_values[-1] not in current_dict:
            current_dict[level_values[-1]] = i

    return lookup

def get_index_map(column_map, current_keys=[], index_map={}):
    """
    Recursively create an index map for a nested column structure.
    
    Args:
    column_map (dict): The column map dict.
    current_keys (list): The current position within the column map, at each level of the hierarchy.
    index_map (dict): The index map to populate. This is also the return value.
    
    Returns:
    dict: The populated index map, mapping indices to positions.
    """
    current_level = column_map
    for key in current_keys:
        current_level = current_level[key]
        
    for key, value in current_level.items():
        if isinstance(value, dict):
            get_index_map(column_map, current_keys + [key], index_map)
        else:
            index_map[value] = current_keys + [key]

    return index_map

def add_index_recursive(column_names, depth):
    # called inside a row

    if depth < len(column_names)-1:
        with dpg.table(parent=dpg.last_item(), header_row=True, resizable=True, no_host_extendX=True):
            dpg.add_table_column(label=column_names[depth])
            with dpg.table_row():
                add_index_recursive(column_names, depth+1)
    else:
        with dpg.table(header_row=True, resizable=True, no_host_extendX=True):
            for name in df.index.names:
                dpg.add_table_column(label=name)
            prev_keytuple = None
            for keytuple in df.index:
                with dpg.table_row():
                    for i in range(len(df.index.names)):
                        label = keytuple[i] if prev_keytuple is None or keytuple[i] != prev_keytuple[i] else ""
                        dpg.add_selectable(label=label)
                    prev_keytuple = keytuple


def add_data_recursive(column_map, keys):
    """
    Recursively build nested table structure for DearPyGui based on a multi-level column map.

    Args:
    column_map (dict): Multi-level column map from DataFrame column hierarchy to indices. 
                        The values of the map are either further dictionaries (for non-leaf nodes)
                        or integers (for leaf nodes), referring to column indices in the DataFrame.
    keys (list): Keys to the current level in the column map.
    """
    # Retrieve current level dictionary from column map
    current_level = column_map
    for key in keys:
        current_level = current_level[key]

    # implicitly, we are in a row at this step
    # adding a table to each column in the row
    for key in current_level.keys():
        with dpg.table(header_row=True, resizable=True, policy=dpg.mvTable_SizingStretchProp,
                   row_background=False, no_host_extendX=True, no_pad_innerX=False,
                   borders_outerH=False, borders_innerV=True):
            nx_level = current_level[key]
            for nx_key in nx_level:
                dpg.add_table_column(label=nx_key)

            if isinstance(next(iter(nx_level.values())), dict):
                # if the values of nx_level are dicts, keep going 
                with dpg.table_row():
                    add_data_recursive(column_map, keys + [key])  
            else:
                # multi-index offset row 
                # with dpg.table_row():
                #     for i in range(8):
                #         dpg.add_text("")
                # if the values of nx_level are strings, write table 
                for row_index in range(df.shape[0]):
                    with dpg.table_row():
                        for relative_column_index, absolute_column_index in enumerate(nx_level.values()):
                            val = df.iloc[row_index, absolute_column_index]
                            cell = dpg.add_selectable(label="{:.2f}".format(val))
                            grid_selector.widget_grid[row_index][absolute_column_index] = cell
                            grid_selector.dpg_lookup[row_index][absolute_column_index] = [
                                dpg.get_item_parent(dpg.get_item_parent(cell)), 
                                row_index , # offset for multi-index row
                                relative_column_index # + len(df.index[0])
                            ]



column_map = get_column_map(df)
# print(column_map)
index_to_column_names = get_index_map(column_map)
# print(index_to_column_names)  
# grid_selector = GridSelector(ID_GRID_SELECT, width=df.shape[1], height=df.shape[0])


# ===========================

def swap_labels(selected_tag, forward=True):
    parent_group = dpg.get_item_parent(selected_pivot_index)
    children = dpg.get_item_children(parent_group, 1)
    
    # Ensure selected index is not the last one
    if selected_tag in children:
        
        # Get the tags of the selected item and the next item
        idx = children.index(selected_tag)
        
        if forward and idx == len(children) - 1:
            return
        if not forward and idx == 0:
            return
        

        next_tag = children[idx + (1 if forward else -1)]

        # Get the labels of the selected item and the next item
        selected_label = dpg.get_item_label(selected_tag)
        next_label = dpg.get_item_label(next_tag)

        # Swap the labels
        dpg.set_item_label(selected_tag, label=next_label)
        dpg.set_item_label(next_tag, label=selected_label)

        on_pidx_button_press(next_tag, None, None)


# ===========================


def select_fields():
    
    # TODO pause gridselect when dialog launched

    fields = pivotBroker.get_field_list()
    current_sel = [dpg.get_item_label(id) for id in dpg.get_item_children(ID_FIELDLIST, 1)]
    data = [(label in current_sel, label) for label in fields]

    listSelectCtrl(title="Select fields", data=data, send_data=select_fields_callback)

def select_fields_callback(user_sel):
    
    # delete current field list
    fields = dpg.get_item_children(ID_FIELDLIST, 1)
    for field in fields:
        dpg.delete_item(field)

    list_of_pivot_field_selectables = []

    # build field list from selection
    for sel, field in user_sel:
        if sel:
            create_pivot_sel(parent=ID_FIELDLIST, label=field)

    # delete any [rows, cols, data] if not in field list
    fields = ['(Data)'] + [sel[1] for sel in user_sel if sel[0]]
    row_btns = [item for item in dpg.get_item_children(ID_ROWSLIST, 1) if (dpg.get_item_type(item) == MvItemTypes.Button.value)]
    for btn in row_btns:
        if(dpg.get_item_label(btn) not in fields):
            dpg.delete_item(btn)
            list_of_pivot_index_buttons.remove(btn)
    col_btns = [item for item in dpg.get_item_children(ID_COLSLIST, 1) if (dpg.get_item_type(item) == MvItemTypes.Button.value)]
    for btn in col_btns:
        if(dpg.get_item_label(btn) not in fields):
            dpg.delete_item(btn)
            list_of_pivot_index_buttons.remove(btn)
    data_btns = [item for item in dpg.get_item_children(ID_DATALIST, 1) if (dpg.get_item_type(item) == MvItemTypes.Button.value)]
    for btn in data_btns:
        if(dpg.get_item_label(btn) not in fields):
            dpg.delete_item(btn)
            list_of_pivot_index_buttons.remove(btn)


    # print(user_sel)

# ===========================

@dataclasses.dataclass
class PivotFilterButton:
    id: str
    field: str
    label: str

selected_pivot_index = -1
list_of_pivot_field_selectables = []
list_of_pivot_index_buttons = []
list_of_pivot_filter_buttons = []

def on_pidx_swap(selected_tag, forward=True):
    swap_labels(selected_tag, forward)
    update_pivot()

def on_psel_drop(drop_sender, drag_sender):
    print(f"Dropped {drag_sender} onto {drop_sender}")

    # logic for dragging from rows and columns back to selected fields
    if drag_sender in list_of_pivot_index_buttons:
        dpg.delete_item(drag_sender)
        list_of_pivot_index_buttons.remove(drag_sender)
    # logic for dragging from filters back to selected fields

    update_pivot()

def on_pwhere_drop(drop_sender, drag_sender):
    print(f"Dropped {drag_sender} onto {drop_sender}")

def on_pidx_drop(drop_sender, drag_sender):
    print(f"Dropped {drag_sender} onto {drop_sender}")
    global list_of_pivot_index_buttons

    current_buttons = list_of_pivot_index_buttons

    # logic for dragging between rows and columns
    if drag_sender in list_of_pivot_index_buttons:
        create_pivot_idx(parent=drop_sender, label=dpg.get_item_label(drag_sender))
        dpg.delete_item(drag_sender)
        list_of_pivot_index_buttons.remove(drag_sender)
    # logic for dragging from field list to rows and columns
    elif drag_sender in list_of_pivot_field_selectables:
        # only add field to rows and cols if not already present
        field = dpg.get_item_label(drag_sender)

        list_of_pivot_index_buttons =  [item for item in list_of_pivot_index_buttons if dpg.get_item_label(item) != field]

        deletions = [item for item in current_buttons if item not in list_of_pivot_index_buttons]
        for e in deletions:
            dpg.delete_item(e)
            
        create_pivot_idx(parent=drop_sender, label=dpg.get_item_label(drag_sender))

    update_pivot()

def on_pidx_drag(sender):
    on_pidx_button_press(sender, None, None)

def on_pidx_button_press(sender, app_data, user_data): 
    global selected_pivot_index
    # highlight the button and unhighlight the rest
    for button in list_of_pivot_index_buttons:
        if button == sender:
            dpg.bind_item_theme(button, selected_button)
            selected_pivot_index = button
        else:
            dpg.bind_item_theme(button, 0)

def create_pivot_idx(parent, label):
    drag_tag = dpg.generate_uuid()
    b = dpg.add_button(tag=drag_tag, label=label, parent=parent, payload_type="PROW", drag_callback=on_pidx_drag, callback=on_pidx_button_press) # , width=8*len(label)
    list_of_pivot_index_buttons.append(b)
    with dpg.drag_payload(parent=b, payload_type="PROW", drag_data=drag_tag, drop_data="drop data"):
        dpg.add_text(label)

def create_pivot_sel(parent, label):
    drag_tag = dpg.generate_uuid()
    b = dpg.add_selectable(tag=drag_tag, label=label, parent=parent, payload_type="PROW")
    list_of_pivot_field_selectables.append(b)
    with dpg.drag_payload(parent=b, payload_type="PROW", drag_data=drag_tag, drop_data="drop data"):
        dpg.add_text(label)

def create_pivot_filter(parent, field, label):
    drag_tag = dpg.generate_uuid()
    b = dpg.add_button(tag=drag_tag, label=label, parent=parent, payload_type="PROW")
    list_of_pivot_filter_buttons.append(PivotFilterButton(id=b, field=field, label=label))
    with dpg.drag_payload(parent=b, payload_type="PROW", drag_data=drag_tag, drop_data="drop data"):
        dpg.add_text(label)



with dpg.theme() as listbox_theme:
    with dpg.theme_component(dpg.mvSelectable):
        dpg.add_theme_color(dpg.mvThemeCol_Header, (0.26 * 255, 0.59 * 255, 0.98 * 255, 0.31 * 255))
    with dpg.theme_component(dpg.mvAll):
        # dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (150, 100, 100), category=dpg.mvThemeCat_Core)
        # dpg.add_theme_color(dpg.mvThemeCol_WindowBg, (255,255,255,255), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_ChildBg, (51,51,55,255), category=dpg.mvThemeCat_Core)

with dpg.theme() as transparent_button:
    with dpg.theme_component(dpg.mvButton):
        dpg.add_theme_color(dpg.mvThemeCol_Button, (255, 255, 255, 0))  # transparent background

with dpg.theme() as selected_button:
    with dpg.theme_component(dpg.mvButton):
        dpg.add_theme_color(dpg.mvThemeCol_Button, (0.26 * 255, 0.59 * 255, 0.98 * 255, 0.31 * 255))  #
        # myStyleVar_FrameRounding
        # myStyleVar_FrameBorderSize
        # FrameBorder


# ===========================


def delete_pivot():
    if dpg.does_item_exist(ID_PIVOT_TABLE):
        grid_selector.deregister()
        dpg.delete_item(ID_PIVOT_TABLE)
        

def update_pivot():
    delete_pivot()
    
    global grid_selector
    global df 
    global column_map
    global index_to_column_names

    rows = [dpg.get_item_label(item) for item in dpg.get_item_children(ID_ROWSLIST, 1) if (dpg.get_item_type(item) == MvItemTypes.Button.value)]
    cols = [dpg.get_item_label(item) for item in dpg.get_item_children(ID_COLSLIST, 1) if (dpg.get_item_type(item) == MvItemTypes.Button.value)]
    aggs = [dpg.get_item_label(item) for item in dpg.get_item_children(ID_DATALIST, 1) if (dpg.get_item_type(item) == MvItemTypes.Button.value)]
    
    df = pivotBroker.get_pivot(filter=None, 
                                rows=rows, 
                                cols=cols,
                                aggs=aggs)
    
    grid_selector = GridSelector(ID_GRID_SELECT, width=df.shape[1], height=df.shape[0])
    # print(df)
    column_map = get_column_map(df)
    # print(column_map)
    index_to_column_names = get_index_map(column_map)

    with dpg.table(tag=ID_PIVOT_TABLE, parent=ID_PIVOT_PARENT,
                   header_row=True, resizable=True, policy=dpg.mvTable_SizingStretchProp,
                   row_background=False, no_host_extendX=True, no_pad_innerX=False,
                   borders_outerH=True, 
                   borders_outerV=True,
                   borders_innerV=True):
        
        # first level name
        dpg.add_table_column(label=df.columns.names[0])
        # dpg.add_table_column(label="")
        # first level values
        top_level = column_map.keys()
        
        for key0 in top_level:
            dpg.add_table_column(label=key0)

        # a single row that contains all data in the table
        with dpg.table_row():
            
            # insert df.index into first column
            column_names = df.columns.names[1:]
            add_index_recursive(column_names, 0)

            add_data_recursive(column_map, keys=[])

# ===========================

with dpg.window(tag=ID_PIVOT_PARENT, width=700, height=400):
    
    dpg.add_button(label='Update table', callback=update_pivot)
    
    with dpg.collapsing_header(label="Setup"):
        with dpg.child_window(height=135) as w:
            
            # ---- horizontal splot
            with dpg.group(horizontal=True): 
                # ---- field selector
                with dpg.group(horizontal=False):
                    dpg.add_button(label="Select: ", callback=select_fields)
                    with dpg.group(horizontal=True):
                        
                        with dpg.child_window(tag=ID_FIELDLIST, width=80, height=90, drop_callback= on_psel_drop, payload_type="PROW") as id_listbox:
                            with dpg.group(horizontal=False, width=80):
                                    
                                    items = pivotBroker.get_field_list()

                                    for item in items[:-1]:
                                        create_pivot_sel(parent=ID_FIELDLIST, label=item)  
                    
                dpg.bind_item_theme(id_listbox, listbox_theme)
                # --- field organiser
                with dpg.table(header_row=False, policy=dpg.mvTable_SizingStretchProp,
                                    no_host_extendX=True, no_pad_innerX=False,
                                    borders_outerH=False, 
                                    borders_outerV=False,
                                    borders_innerV=False):
                    dpg.add_table_column(width=40, width_fixed=True)
                    dpg.add_table_column(width_stretch=True, init_width_or_weight=0.0)

                    with dpg.table_row():
                        dpg.add_text("Where: ")
                        with dpg.group(horizontal=False, drop_callback= on_pwhere_drop, payload_type="PROW") as g:
                            create_pivot_filter(parent=g, field="Year", label="Year is in [2022, 2023]")
                            create_pivot_filter(parent=g, field="Weight", label="Weight > 0")
                            
                    with dpg.table_row():
                        with dpg.group(horizontal=False):
                            dpg.add_text("Groupby: ")
                            with dpg.group(horizontal=True):
                                pidx_left = dpg.add_button(arrow=True, direction=dpg.mvDir_Left)
                                pidx_right = dpg.add_button(arrow=True, direction=dpg.mvDir_Right)
                            # with dpg.group(horizontal=True):
                            #     dpg.add_text("T:", indent=4)
                            #     dpg.add_checkbox(default_value=True)

                        with dpg.group(horizontal=False):
                            with dpg.group(tag=ID_ROWSLIST, horizontal=True, drop_callback= on_pidx_drop, payload_type="PROW"):
                                dpg.add_text("Rows: ", indent=10)
                                
                                create_pivot_idx(parent=ID_ROWSLIST, label="Year")
                                create_pivot_idx(parent=ID_ROWSLIST, label="Quarter")
                                
                            with dpg.group(tag=ID_COLSLIST, horizontal=True, drop_callback= on_pidx_drop, payload_type="PROW"):
                                dpg.add_text("Columns: ", indent=10)
                                create_pivot_idx(parent=ID_COLSLIST, label="Fruit")
                                create_pivot_idx(parent=ID_COLSLIST, label="Shape")
                                create_pivot_idx(parent=ID_COLSLIST, label="(Data)")

                            with dpg.group(tag=ID_DATALIST, horizontal=True, drop_callback= on_pidx_drop, payload_type="PROW") as g:
                                dpg.add_text("Data: ", indent=10)
                                create_pivot_idx(parent=ID_DATALIST, label="Volume")
                                create_pivot_idx(parent=ID_DATALIST, label="Weight")
                                

                        dpg.set_item_callback(pidx_left, lambda: on_pidx_swap(selected_tag=selected_pivot_index, forward=False))
                        dpg.set_item_callback(pidx_right, lambda: on_pidx_swap(selected_tag=selected_pivot_index, forward=True))

    update_pivot()


dpg.show_viewport()

while dpg.is_dearpygui_running():
    
    dpg.render_dearpygui_frame()

dpg.destroy_context()