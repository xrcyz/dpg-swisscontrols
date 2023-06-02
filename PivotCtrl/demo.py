
import dearpygui.dearpygui as dpg
import pandas as pd
import numpy as np
import itertools
from PivotData import get_pivot_data

dpg.create_context()
dpg.create_viewport(title='Custom Title', width=800, height=600)
dpg.setup_dearpygui()

df = get_pivot_data()
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
                # if the values of nx_level are strings, write table 
                for row_index in range(df.shape[0]):
                    with dpg.table_row():
                        for column_index in nx_level.values():
                            val = df.iloc[row_index, column_index]
                            dpg.add_selectable(label="{:.2f}".format(val))



column_map = get_column_map(df)
# print(column_map)

with dpg.window(tag="window", width=700, height=600):
    with dpg.table(header_row=True, resizable=True, borders_outerH=True, borders_outerV=True):
        
        # first level name
        dpg.add_table_column(label=df.columns.names[0])
        # first level values
        top_level = column_map.keys()
        for key0 in top_level:
            dpg.add_table_column(label=key0)

        # a single row that contains all data in the table
        with dpg.table_row():
            
            # insert df.index into first column
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

            add_data_recursive(column_map, keys=[])



with dpg.window(tag="Table", width=700, height=400, pos=[300,300]):
    with dpg.table(header_row=True, resizable=True, borders_outerH=True, borders_outerV=True):
        dpg.add_table_column(label="Section")
        dpg.add_table_column(label="Fruit")
        dpg.add_table_column(label="Vegetables")

        # a single row that contains all data in the table
        with dpg.table_row():
            # index column
            with dpg.table(header_row=True):
                dpg.add_table_column(label="Product")

                with dpg.table_row():
                    with dpg.table(header_row=True, resizable=True):
                                dpg.add_table_column(label="Year")
                                dpg.add_table_column(label="Month")

                                with dpg.table_row():
                                    dpg.add_selectable(label="2022")
                                    dpg.add_selectable(label="Nov")
                                with dpg.table_row():
                                    dpg.add_selectable(label="")
                                    dpg.add_selectable(label="Dec")
                                with dpg.table_row():
                                    dpg.add_selectable(label="2023")
                                    dpg.add_selectable(label="Jan")
                                with dpg.table_row():
                                    dpg.add_selectable(label="")
                                    dpg.add_selectable(label="Feb")
                            

            # multiindex column 1
            with dpg.table(header_row=True, resizable=True):
                dpg.add_table_column(label="Apples")
                dpg.add_table_column(label="Oranges")

                with dpg.table_row():
                    with dpg.table(header_row=True, resizable=True):
                        dpg.add_table_column(label="Volume")
                        dpg.add_table_column(label="Weight")

                        with dpg.table_row():
                            dpg.add_selectable(label="5")
                            dpg.add_selectable(label="10")
                        with dpg.table_row():
                            dpg.add_selectable(label="15")
                            dpg.add_selectable(label="20")
                        with dpg.table_row():
                            dpg.add_selectable(label="5")
                            dpg.add_selectable(label="10")
                        with dpg.table_row():
                            dpg.add_selectable(label="15")
                            dpg.add_selectable(label="20")

                    with dpg.table(header_row=True, resizable=True):
                        dpg.add_table_column(label="Volume")
                        dpg.add_table_column(label="Weight")

                        with dpg.table_row():
                            dpg.add_selectable(label="5")
                            dpg.add_selectable(label="10")
                        with dpg.table_row():
                            dpg.add_selectable(label="15")
                            dpg.add_selectable(label="20")
                        with dpg.table_row():
                            dpg.add_selectable(label="5")
                            dpg.add_selectable(label="10")
                        with dpg.table_row():
                            dpg.add_selectable(label="15")
                            dpg.add_selectable(label="20")
                
            # multiindex column 2
            with dpg.table(header_row=True, resizable=True):
                dpg.add_table_column(label="Avacados")
                dpg.add_table_column(label="Chillies")

                with dpg.table_row():
                    with dpg.table(header_row=True, resizable=True):
                        dpg.add_table_column(label="Volume")
                        dpg.add_table_column(label="Weight")

                        with dpg.table_row():
                            dpg.add_selectable(label="5")
                            dpg.add_selectable(label="10")
                        with dpg.table_row():
                            dpg.add_selectable(label="15")
                            dpg.add_selectable(label="20")
                        with dpg.table_row():
                            dpg.add_selectable(label="5")
                            dpg.add_selectable(label="10")
                        with dpg.table_row():
                            dpg.add_selectable(label="15")
                            dpg.add_selectable(label="20")
                            
                    with dpg.table(header_row=True, resizable=True):
                        dpg.add_table_column(label="Volume")
                        dpg.add_table_column(label="Weight")

                        with dpg.table_row():
                            dpg.add_selectable(label="5")
                            dpg.add_selectable(label="10")
                        with dpg.table_row():
                            dpg.add_selectable(label="15")
                            dpg.add_selectable(label="20")
                        with dpg.table_row():
                            dpg.add_selectable(label="5")
                            dpg.add_selectable(label="10")
                        with dpg.table_row():
                            dpg.add_selectable(label="15")
                            dpg.add_selectable(label="20")

dpg.show_viewport()

while dpg.is_dearpygui_running():
    
    dpg.render_dearpygui_frame()

dpg.destroy_context()