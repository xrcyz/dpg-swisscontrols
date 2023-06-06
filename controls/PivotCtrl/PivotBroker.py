from DataSource import get_flat_data
import pandas as pd

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
    
    def get_pivot(self, filter, rows, cols, aggs):
        
        col_order = list(range(1, len(cols)+1)) + [0]
        agg_order = {str: idx for idx, str in enumerate(aggs)}

        group_by = (self.df.copy()[rows+cols+aggs]
                    .groupby(rows+cols)
                    .sum(numeric_only=True)
                    .unstack(cols)    
                    .reorder_levels(order=col_order, axis=1)
                    .fillna(0)
                )
        
        group_by.rename(columns=agg_order, inplace=True)
        group_by = group_by.sort_index(axis=1)
        group_by.rename(columns={v: k for k, v in agg_order.items()}, inplace=True)
        
        # Ensure the order of levels in MultiIndex
        
        return group_by
    
