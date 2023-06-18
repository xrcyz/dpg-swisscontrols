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

        assert not isinstance(self.df.columns, pd.MultiIndex), "DataFrame columns should not be a MultiIndex"
        assert not isinstance(self.df.index, pd.MultiIndex), "DataFrame index should not be a MultiIndex"
        assert isinstance(self.df.index, pd.RangeIndex), "DataFrame index should be a default integer-based index (RangeIndex)"

    def get_field_list(self):
        # return sorted(self.df.columns)
        # assume the data source, in its infinite wisdom, has given us pre-ordered columns
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
        elif not (rows+cols):
            # if rows and cols are empty, sum the aggs
            result = (self.df.copy()[aggs]
                      .sum(numeric_only=True)
                      .to_frame().T # convert series back to dataframe
                    )
            
            # set column name to Value
            result = result.rename(index={0: 'Value'})

        else:
            # give thanks to pandas
            result = (self.df.copy()[rows+cols+aggs]
                        .groupby(rows+cols)
                        .sum(numeric_only=True)
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
    
