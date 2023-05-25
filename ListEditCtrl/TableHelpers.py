import dearpygui.dearpygui as dpg

def swap_row_values(table_id, row_a_idx, row_b_idx):
    # Get the children of the table
    rows = dpg.get_item_children(table_id, 1)

    # Get the row IDs for the rows to be swapped
    row_a_id = rows[row_a_idx]
    row_b_id = rows[row_b_idx]

    # Get the cell IDs for each row
    cells_a = dpg.get_item_children(row_a_id, 1)
    cells_b = dpg.get_item_children(row_b_id, 1)

    # Temporarily store the values from row A
    temp_values = [dpg.get_value(cell) for cell in cells_a]

    # Set the values in row A to the values from row B
    for i, cell in enumerate(cells_a):
        dpg.set_value(cell, dpg.get_value(cells_b[i]))

    # Set the values in row B to the temporarily stored values from row A
    for i, cell in enumerate(cells_b):
        dpg.set_value(cell, temp_values[i])
