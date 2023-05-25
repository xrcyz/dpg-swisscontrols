import copy

class DataGrid:
    TXT_STRING = 0
    TXT_INT = 1
    TXT_FLOAT = 2
    COMBO = 3
    CHECKBOX = 4
    GRID = 5
    COLOR = 6
    
    def __init__(self, title, columns, dtypes, defaults, combo_lists = None, data=None):
        """
        Create a new DataGrid.

        :param title: Display title
        :param columns: List of column names.
        :param dtypes: List of data types for each column.
        :param defaults: List of default values for each column.
        :param combo_lists: List of combo lists for each column.
        :param data: 2D list for grid data, ordered data[col][row].
        """
        if not isinstance(columns, list) or not isinstance(dtypes, list) or not isinstance(defaults, list):
            raise ValueError("Columns, dtypes, and defaults must be lists.")
        
        if len(columns) != len(dtypes) or len(columns) != len(defaults):
            raise ValueError("Columns, dtypes, and defaults must have the same length.")

        if combo_lists is not None and (not isinstance(combo_lists, list) or len(columns) != len(combo_lists)):
            raise ValueError("Combo_lists must be a list with the same length as columns.")
        
        self.title = title
        self.columns = columns
        self.dtypes = dtypes
        self.defaults = defaults
        self.combo_lists = combo_lists or [None] * len(columns)
        self.data = data if data is not None else [[] for _ in columns]

    @property
    def shape(self):
        # follow pandas convention [rows, columns]
        return len(self.data[0] if self.data else 0), len(self.columns)

    def copy(self):
        ret = self.empty_like()
        ret.data = copy.deepcopy(self.data)
        return ret

    def empty_like(self):
        empty_grid = DataGrid(
            title = self.title,
            columns = [col for col in self.columns],
            dtypes = [dt for dt in self.dtypes],
            defaults = [val for val in self.defaults],
            combo_lists = [cl for cl in self.combo_lists]
        )
        return empty_grid

    def append(self, row):
        if row is None:
            row = self.defaults
        elif len(row) != len(self.columns):
            raise ValueError("Row does not match the column structure")
        for col in range(len(row)):
            if(isinstance(row[col], DataGrid)): # fails
                self.data[col].append(row[col].copy())
            else:
                self.data[col].append(row[col])

    def drop(self, row_idx):
        """Remove a row from the data grid by its index."""
        for col in range(len(self.columns)):
            if row_idx < len(self.data[col]):  # Make sure the row exists
                del self.data[col][row_idx]

    def swap_rows(self, row_idx_a, row_idx_b):
        if row_idx_a == row_idx_b:
            return

        if not (0 <= row_idx_a < len(self.data[0]) and 0 <= row_idx_b < len(self.data[0])):
            raise ValueError("Invalid row indices.")

        for column in self.data:
            column[row_idx_a], column[row_idx_b] = column[row_idx_b], column[row_idx_a]

    def get_row(self, row):
        return [col[row] for col in self.data]

    def get_cell(self, col_idx, row_idx):
        return self.data[col_idx][row_idx]
    
    def execute_callback(self, col_idx, row_idx):
        callback = self.callbacks[col_idx]
        if callback:
            callback(self, row_idx)

    def display(self):
        for column in self.columns:
            print(f"{column:15s}", end=" ")
        print()
        
        for row in range(len(self.data[0])):
            for col in range(len(self.data)):
                if self.dtypes[col] == DataGrid.GRID:
                    print(f"{self.data[col][row].title:15s}", end=" ")
                else:
                    print(f"{str(self.data[col][row]):15s}", end=" ")
            print()


