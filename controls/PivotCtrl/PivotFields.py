from enum import Enum

class PivotFieldTypes:
    class GroupBy(Enum):
        GROUPBY = 1

    class Aggregate(Enum):
        SUM = 2
        WEIGHTED_AVERAGE = 3
        COUNT = 4

class PivotField:
    def __init__(self, name, field_type, weight_field=None, agg_func='sum', format=None):
        self.name = name
        self.field_type = field_type
        self.weight_field = weight_field
        self.agg_func = agg_func
        self.format = format
