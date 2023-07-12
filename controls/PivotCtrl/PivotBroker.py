
import dataclasses
from enum import Enum
from typing import List, Dict, Callable

import pandas as pd
import numpy as np

from controls.PivotCtrl.DataSource import get_flat_data, get_field_data
from controls.PivotCtrl.PivotFields import PivotField, PivotFieldTypes
from controls.Scripting.scripting import create_combined_lambdas

class PivotBroker:
    # mediator between PivotCtrl and DataSource
    # receives pivot parameters from the UI
    # sends pivoted dataframe to the UI
    # handles all pandas operations separately from UI 
    # tells the UI the available fields names and types

    df: pd.DataFrame
    field_data: Dict[str, PivotField]

    def __init__(self):

        # if df is multiindex raise exception
        # should be flat data
        self.df = get_flat_data()
        assert not isinstance(self.df.columns, pd.MultiIndex), "DataFrame columns should not be a MultiIndex"
        assert not isinstance(self.df.index, pd.MultiIndex), "DataFrame index should not be a MultiIndex"
        assert isinstance(self.df.index, pd.RangeIndex), "DataFrame index should be a default integer-based index (RangeIndex)"

        self.field_data = get_field_data()

        # assign the aggregation functions to local PivotBroker functions
        self.aggregation_functions = {
            PivotFieldTypes.Aggregate.SUM: 'sum',
            PivotFieldTypes.Aggregate.WEIGHTED_AVERAGE: self.custom_weighted_average,
            PivotFieldTypes.Aggregate.COUNT: 'count',
            # define other aggregation functions here...
        }

        for name, field in self.field_data.items():
            if isinstance(field.field_type, PivotFieldTypes.Aggregate):
                field.agg_func = self.aggregation_functions[field.field_type]

    def get_field_list(self):
        # return sorted(self.df.columns)
        # assume the data source, in its infinite wisdom, has given us pre-ordered columns
        return self.df.columns
    
    def get_field_type(self, field_name):
        if (field_name == "(Data)"):
            return PivotFieldTypes.GroupBy.CATEGORY
        
        if field_name not in self.field_data:
            raise Exception(f"The field '{field_name}' does not exist.")
        return self.field_data[field_name].field_type

    def custom_weighted_average(self, series: pd.Series) -> float:
        weight_col = self.field_data[series.name].weight_field
        return np.average(series, weights=self.df.loc[series.index, weight_col])

    def get_filtered(self, filter):
        return self.df[self.df.apply(filter, axis=1)]

    def get_pivot(self, 
                  filters: List[Callable], 
                  rows: List[str], 
                  cols: List[str], 
                  aggs: List[str]):
        
        """
        :param rows: A list of fields to become index in the returned dataframe
        :param cols: A list of fields to become columns in the returned dataframe
        :param aggs: A list of fields to be grouped by rows and cols

        A special string '(Data)' indicates the level of the `aggs` fields in one of the MultiIndexes.
        """
        
        if not filters:
            filtered_df = self.df
        else:
            combined_lambda = create_combined_lambdas(lambdas=filters)
            filtered_df = self.df[self.df.apply(combined_lambda, axis=1)]

        agg_dict = {field: self.field_data[field].agg_func for field in aggs}
        # if 'Price/kg' in agg_dict:
        #     agg_dict['Price/kg'] = self.custom_weighted_average

        # before anything else, figure out the transpose situation
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
        
         # deal with special cases
        if not (rows+cols+aggs):
            # special case: [rows, cols, aggs] are all empty
            result = pd.DataFrame(index=[""], columns=[""]).fillna(0 )

            return result    
        elif not (aggs):
            # special case: [rows, cols] populated but [aggs] empty
            result = (filtered_df[rows+cols+aggs]
                        .groupby(rows+cols)
                        .sum(numeric_only=True)
                        # .agg(agg_dict)
                    )
            
            # if rows is empty list, insert a 'Value' level 
            if not rows:  
                result = pd.concat([result], axis=0, keys=['Value'])

        elif not (rows+cols):
            # special case: [aggs] populated but [rows, cols] empty
            result = (filtered_df.copy()[aggs]
                    #   .sum(numeric_only=True)
                      .agg(agg_dict)
                      .to_frame().T # convert series back to dataframe
                    )
            
            # set column name to 'Value'
            result = result.rename(index={0: 'Value'})
        else:
            # general case: [rows, cols, aggs] populated
            result = (filtered_df.copy()[rows+cols+aggs]
                        .groupby(rows+cols)
                        # .sum(numeric_only=True)
                        .agg(agg_dict)
                    )
        
            # if rows is empty list, insert a 'Value' level 
            if not rows:  
                result = pd.concat([result], axis=0, keys=['Value'])
        
        # unstack columns
        result = result.unstack(cols).fillna(0)

        # reorder cols if not empty list
        if cols: 
            # name the '(Data)' level
            new_names = list(result.columns.names)
            new_names[0] = "Field"
            result.columns.set_names(new_names, inplace=True)
            # order the columns
            result = result.reorder_levels(order=col_level_order, axis=1)

        # create a rename dict for custom field ordering
        agg_order = {str: f'"@$%"+{idx}' for idx, str in enumerate(aggs)} 
        result.rename(columns=agg_order, inplace=True)
        result = result.sort_index(axis=1)
        result.rename(columns={v: k for k, v in agg_order.items()}, inplace=True)

        if(transpose):
            result = result.T
        
        
        return result
    
