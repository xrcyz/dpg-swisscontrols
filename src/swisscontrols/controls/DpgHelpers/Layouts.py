
from typing import List, Dict

from swisscontrols.controls.DpgHelpers.MvStyleVar import MvStyleVar

# this needs to be more than it is
# a tree of windows and elements where you can recursively call height and sum the lot

def calc_single_window_height_from_items(count_items, min_count = 1):
    # minimum window size
    if count_items < min_count:
        count_items = min_count

    return (
        # 2 * MvStyleVar.WindowPadding.value[1] + 
        count_items * (MvStyleVar.TextHeight.value + 2 * MvStyleVar.FramePadding.value[1]) + 
        (count_items-1) * MvStyleVar.ItemSpacing.value[1]
    )

def calc_multi_window_height_in_table_rows(count_items_in_each_window: List[int]):
    height = 2 * MvStyleVar.WindowPadding.value[1]
    for count_items in count_items_in_each_window:
        height += calc_single_window_height_from_items(count_items=count_items)
        height += 2*MvStyleVar.CellPadding.value[1]
    return height