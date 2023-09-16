import dearpygui.dearpygui as dpg
import numpy as np
import itertools

def is_between(a, b, c):
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
        
        self.widget_grid = [[None for _ in range(width)] for _ in range(height)]
        self.dpg_lookup = [[(0,0,0) for _ in range(width)] for _ in range(height)] # [table_id, i, j] for each cell
        self.mouse_drag_coords = [[0,0], [0,0]] # pixel coords
        self.range_coords = [[0,0], [0,0]] # index coords
        self.is_dragging_range = False
        self._is_paused = False
        self.mouse_registry = -1
        with dpg.handler_registry() as mouse_registry:
            self.mouse_registry = mouse_registry
            # dpg.add_mouse_click_handler(button=dpg.mvMouseButton_Left, callback=self.test)
            dpg.add_mouse_click_handler(button=dpg.mvMouseButton_Left, callback=self.on_mouse_down)
            dpg.add_mouse_release_handler(button=dpg.mvMouseButton_Left, callback=self.on_mouse_up)
            dpg.add_mouse_drag_handler(button=dpg.mvMouseButton_Left, callback=self.on_mouse_drag)
        
    def __del__(self):
        self.deregister()

    def is_empty(self):
        return (len(self.widget_grid) == 0 or len(self.widget_grid[0]) == 0)

    def pause(self):
        self._is_paused = True

    def unpause(self):
        self._is_paused = False

    def on_mouse_down(self, sender, app_data):
        
        # bail if paused
        if(self._is_paused): 
            return

        # bail if widget grid is empty
        if self.is_empty():
            return

        # print(self._is_paused)

        # test if mouse inside table bounding box
        rect_min = dpg.get_item_rect_min(self.widget_grid[0][0])
        rect_max = dpg.get_item_rect_max(self.widget_grid[-1][-1])
        mouse_pos = dpg.get_mouse_pos(local=False)
        if((rect_min[0] < mouse_pos[0] < rect_max[0]) and (rect_min[1] < mouse_pos[1] < rect_max[1])):
            self.mouse_drag_coords[0] = mouse_pos
            self.is_dragging_range = True
            widget_widths = [dpg.get_item_rect_size(w)[0]+1 for w in self.widget_grid[0]]
            widget_heights = [dpg.get_item_rect_size(r[0])[1] for r in self.widget_grid] # y element of (first item in each row)
            column = int(np.searchsorted(np.cumsum(widget_widths), mouse_pos[0] - rect_min[0]))
            row = int(np.searchsorted(np.cumsum(widget_heights), mouse_pos[1] - rect_min[1]))
            self.range_coords[0] = [column, row]
            
            print(f"Mouse down: {column}, {row}")

    def on_mouse_drag(self, sender, app_data):
        
        # bail if paused
        if(self._is_paused): 
            return  None, None
        
        # bail if widget grid is empty
        if self.is_empty():
            return None, None
        
        # print(self._is_paused)

        # Get the ending position of the drag
        rect_min = dpg.get_item_rect_min(self.widget_grid[0][0])
        rect_max = dpg.get_item_rect_max(self.widget_grid[-1][-1])
        mouse_pos = dpg.get_mouse_pos(local=False)
        # print(f"self.is_dragging_range: {self.is_dragging_range}")


        if(self.is_dragging_range and (rect_min[0] < mouse_pos[0] < rect_max[0]) and (rect_min[1] < mouse_pos[1] < rect_max[1])):
            self.mouse_drag_coords[1] = mouse_pos
            widget_widths = [dpg.get_item_rect_size(w)[0]+1 for w in self.widget_grid[0]]
            widget_heights = [dpg.get_item_rect_size(r[0])[1] for r in self.widget_grid]
            column = int(np.searchsorted(np.cumsum(widget_widths), mouse_pos[0] - rect_min[0]))
            row = int(np.searchsorted(np.cumsum(widget_heights), mouse_pos[1] - rect_min[1]))
            self.range_coords[1] = [column, row]

            for j,i in itertools.product(range(self.height), range(self.width)):
                
                table_id, table_j, table_i = self.dpg_lookup[j][i]
                if is_between(self.range_coords[0][0], i, self.range_coords[1][0]) and is_between(self.range_coords[0][1], j, self.range_coords[1][1]):
                    dpg.highlight_table_cell(table_id, table_j, table_i, [34, 83, 118, 100])
                else:
                    dpg.unhighlight_table_cell(table_id, table_j, table_i)
                    dpg.set_value(self.widget_grid[j][i], False)

            return row, column
        else:
            return None, None
                    

    def on_mouse_up(self, sender, app_data):
        
        # bail if paused
        if(self._is_paused): 
            return 

        row, column = self.on_mouse_drag(sender, app_data)
        self.is_dragging_range = False
        print(f"Mouse up: {column}, {row}")

    def deregister(self):
        if (self.mouse_registry > 0 and dpg.does_item_exist(self.mouse_registry)):
            dpg.delete_item(self.mouse_registry)
        self.mouse_registry = -1