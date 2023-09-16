from enum import Enum

"""
In pandas, you can represent this column as an ordered categorical dtype, which has an associated order and allows for comparison operations based on this order. Here's an example:

```
import pandas as pd

# Define the order
ordering = ['First', 'Second', 'Third']

# Create a categorical series with this order
s = pd.Series(['First', 'Second', 'Third', 'Second', 'First'], dtype=pd.CategoricalDtype(categories=ordering, ordered=True))

# Now you can perform comparisons
print(s >= 'Second')
```
"""

class PivotFieldType:
    class GroupBy(Enum):
        CATEGORY = 1
        ORDINAL = 2

    class Aggregate(Enum):
        SUM = 3
        WEIGHTED_AVERAGE = 4
        COUNT = 5

class PivotField:
    def __init__(self, name, field_type, weight_field=None, agg_func='sum', format=None):
        self.name = name
        self.field_type = field_type
        self.weight_field = weight_field
        self.agg_func = agg_func
        self.format = format
