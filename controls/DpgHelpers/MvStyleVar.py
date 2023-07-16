from enum import Enum
from typing import List, Dict

class MvStyleVar(Enum):
    TextHeight = 13
    WindowPadding = [8,8]
    FramePadding = [4,3]
    CellPadding  = [4,2]
    ItemSpacing = [8,4]
    # Add other item types as needed

def calc_single_window_height_from_items(count_items, min_count = 1):
    # minimum window size
    if count_items < min_count:
        count_items = min_count

    return (
        2 * MvStyleVar.WindowPadding.value[1] + 
        count_items * (MvStyleVar.TextHeight.value + 2 * MvStyleVar.FramePadding.value[1]) + 
        (count_items-1) * MvStyleVar.ItemSpacing.value[1]
    )

def calc_multi_window_height_in_table_rows(count_items_in_each_window: List[int]):
    height = 2 * MvStyleVar.WindowPadding.value[1]
    for count_items in count_items_in_each_window:
        height += calc_single_window_height_from_items(count_items=count_items)
        height += 2*MvStyleVar.CellPadding.value[1]
    return height

    
