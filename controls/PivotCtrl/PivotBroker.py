from DataSource import get_flat_data
import pandas as pd
import numpy as np

class PivotBroker:
    # mediator between PivotCtrl and DataSource
    # receives pivot parameters from the UI
    # sends pivoted dataframe to the UI
    # handles all pandas operations separately from UI 
    # tells the UI the available fields names and types

    def __init__(self):

        # if df is multiindex raise exception
        # should be flat data
        self.df = get_flat_data()

    def get_field_list(self):
        # return sorted(self.df.columns)
        # assume the data source, in its infinite wisdom, has given us a column order
        return self.df.columns
    
    def get_pivot(self, 
                  filter: list[str], 
                  rows: list[str], 
                  cols: list[str], 
                  aggs: list[str]):
        
        """
        :param rows: A list of fields to become index in the returned dataframe
        :param cols: A list of fields to become columns in the returned dataframe
        :param aggs: A list of fields to be grouped by rows and cols

        A special string '(Data)' indicates the level of the `aggs` fields in one of the MultiIndexes.
        """

        transpose = False
        if('(Data)' in rows):
            """
            If '(Data)' is in the rows, then swap rows with columns and transpose at the end. 
            """
            cols, rows = rows, cols
            transpose = True
            
        cols_init = ['(Data)'] + [col for col in cols if col != '(Data)'] # initial dataframe.columns.names
        col_levels_dict = {col: cols_init.index(col) for col in cols_init} # index of each item in initial df
        col_level_order = [col_levels_dict[item] for item in cols] # where we want the cols to be
        
        # Remove '(Data)' from cols list
        cols.remove('(Data)') 
        
        # give thanks to pandas
        group_by = (self.df.copy()[rows+cols+aggs]
                    .groupby(rows+cols)
                    .sum(numeric_only=True)
                    .unstack(cols)    
                    .reorder_levels(order=col_level_order, axis=1)
                    .fillna(0)
                )
        
        # create a rename dict for custom field ordering
        agg_order = {str: f'"@$%"+{idx}' for idx, str in enumerate(aggs)} 
        group_by.rename(columns=agg_order, inplace=True)
        group_by = group_by.sort_index(axis=1)
        group_by.rename(columns={v: k for k, v in agg_order.items()}, inplace=True)

        if(transpose):
            group_by = group_by.T
        
        return group_by
    
