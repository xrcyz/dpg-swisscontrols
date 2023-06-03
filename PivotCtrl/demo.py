
import dearpygui.dearpygui as dpg
import pandas as pd
import numpy as np
import itertools
from PivotData import get_pivot_data
from GridSelector import GridSelector

dpg.create_context()
dpg.create_viewport(title='Custom Title', width=800, height=600)
dpg.setup_dearpygui()

ID_TABLE = dpg.generate_uuid()

df = get_pivot_data()
print(df)
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
        with dpg.table(parent=dpg.last_item(), header_row=True, resizable=True):
            dpg.add_table_column(label=column_names[depth])
            with dpg.table_row():
                add_index_recursive(column_names, depth+1)
    else:
        with dpg.table(header_row=True, resizable=True):
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
        with dpg.table(header_row=True, resizable=True):
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
# print(index_map)  
grid_selector = GridSelector(ID_TABLE, width=df.shape[1], height=df.shape[0])

with dpg.window(tag="window", width=700, height=400):
    with dpg.table(header_row=True, resizable=True, borders_outerH=True, borders_outerV=True):
        
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

# i think we need some map from the cell to [parent_id, i, j]
# also when we build the widget_grid, we need to map from 
# we can get the local column index from len(nx_level.values())
# and the row is just row_index
# 
# cell = grid_selector.widget_grid[8][1]
# parent_table = dpg.get_item_parent(dpg.get_item_parent(cell))
# print(dpg.highlight_table_cell(parent_table, 10, 1, [34, 83, 118, 100]))
# print(dpg.get_item_info(cell))


dpg.show_viewport()

while dpg.is_dearpygui_running():
    
    dpg.render_dearpygui_frame()

dpg.destroy_context()