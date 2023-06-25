from enum import Enum

class PivotFieldTypes:
    class GroupBy(Enum):
        GROUPBY = 1

    class Aggregate(Enum):
        SUM = 2
        WEIGHTED_AVERAGE = 3
        COUNT = 4