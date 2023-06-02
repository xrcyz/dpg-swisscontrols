import dearpygui.dearpygui as dpg
import numpy as np
import itertools

def if_between(a, b, c):
    """Checks if b is between a and c (inclusive). Handles any order of a, b, c."""
    return min(a, c) <= b <= max(a, c)

def translate_index(flat_index, dimensions):
    """
    Translates a flat index into a nested index based on provided dimensions.

    Args:
        flat_index (int): The index to be translated.
        dimensions (list of ints): The dimensions of the nested structure.
    
    Returns:
        list of ints: The nested index corresponding to the flat_index.

    Examples:
        >>> translate_index(5, [3, 2, 2])
        [1, 0, 1]
    """
    nested_index = []
    for dimension in reversed(dimensions):
        nested_index.insert(0, flat_index % dimension)
        flat_index //= dimension
        
    return nested_index

def index_to_nested_index(index, dims):
    """
    Translates a single index to a corresponding nested index based on provided dimensions.

    Args:
        index (int): The index to be translated.
        dims (list of list of ints): The dimensions of the nested structure. Each sub-list represents the
            dimensions of each level of the nested structure.

    Returns:
        list of ints: The nested index corresponding to the provided index.

    Examples:
        >>> index_to_nested_index(7, [[1,2], [2,2,2]])
        [2, 0, 1] # third column, first child, second grandchild
    """
    offset = np.prod(dims[0])
    if index < offset:
        return [0] + translate_index(index, dims[0])
    else:
        ret = translate_index(index - offset, dims[1])
        ret[0] += 1
        return ret

class GridSelector:
    def __init__(self, table_id, width, height):
        self.table_id = table_id
        self.width = width
        self.height = height
        self.widget_grid = []
        self.mouse_drag_coords = [[0,0], [0,0]] # pixel coords
        self.range_coords = [[0,0], [0,0]] # index coords
        self.is_dragging_range = False
        self.mouse_registry = -1
        with dpg.handler_registry() as mouse_registry:
            self.mouse_registry = mouse_registry
            dpg.add_mouse_click_handler(button=dpg.mvMouseButton_Left, callback=self.on_mouse_down)
            dpg.add_mouse_release_handler(button=dpg.mvMouseButton_Left, callback=self.on_mouse_up)
            dpg.add_mouse_drag_handler(button=dpg.mvMouseButton_Left, callback=self.on_mouse_drag)

    def __del__(self):
        self.deregister()

    def on_mouse_down(self, sender, app_data):
        # test if mouse inside table bounding box
        rect_min = dpg.get_item_rect_min(self.widget_grid[0][0])
        rect_max = dpg.get_item_rect_max(self.widget_grid[-1][-1])
        mouse_pos = dpg.get_mouse_pos(local=False)
        if((rect_min[0] < mouse_pos[0] < rect_max[0]) and (rect_min[1] < mouse_pos[1] < rect_max[1])):
            self.mouse_drag_coords[0] = mouse_pos
            self.is_dragging_range = True
            widget_widths = [dpg.get_item_rect_size(w)[0]+1 for w in self.widget_grid[0]]
            widget_heights = [dpg.get_item_rect_size(w)[1] for w in self.widget_grid[1]]
            column = int(np.searchsorted(np.cumsum(widget_widths), mouse_pos[0] - rect_min[0]))
            row = int(np.searchsorted(np.cumsum(widget_heights), mouse_pos[1] - rect_min[1]))
            self.range_coords[0] = [column, row]
            # print(f"Address: {column}, {row}")

    def on_mouse_drag(self, sender, app_data):
        # Get the ending position of the drag
        rect_min = dpg.get_item_rect_min(self.widget_grid[0][0])
        rect_max = dpg.get_item_rect_max(self.widget_grid[-1][-1])
        mouse_pos = dpg.get_mouse_pos(local=False)
        if(self.is_dragging_range and (rect_min[0] < mouse_pos[0] < rect_max[0]) and (rect_min[1] < mouse_pos[1] < rect_max[1])):
            self.mouse_drag_coords[1] = mouse_pos
            widget_widths = [dpg.get_item_rect_size(w)[0]+1 for w in self.widget_grid[0]]
            widget_heights = [dpg.get_item_rect_size(w)[1] for w in self.widget_grid[1]]
            column = int(np.searchsorted(np.cumsum(widget_widths), mouse_pos[0] - rect_min[0]))
            row = int(np.searchsorted(np.cumsum(widget_heights), mouse_pos[1] - rect_min[1]))
            self.range_coords[1] = [column, row]
            # print(f"Address: {column}, {row}")

            for i,j in itertools.product(range(self.width), range(self.height)):
                if if_between(self.range_coords[0][0], i, self.range_coords[1][0]) and if_between(self.range_coords[0][1], j, self.range_coords[1][1]):
                    dpg.highlight_table_cell(self.table_id, j, i, [34, 83, 118, 100])
                else:
                    dpg.unhighlight_table_cell(self.table_id, j, i)
                    dpg.set_value(self.widget_grid[j][i], False)
                    

    def on_mouse_up(self, sender, app_data):
        is_dragging_range = False
        self.on_mouse_drag(sender, app_data)

    def deregister(self):
        dpg.delete_item(self.mouse_registry)
        self.mouse_registry = -1