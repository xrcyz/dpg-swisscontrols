import dearpygui.dearpygui as dpg

def pivotCtrl(table_id):
    table_id = dpg.generate_uuid()
    with dpg.table(tag=table_id, header_row=False, resizable=True, policy=dpg.mvTable_SizingStretchProp, #mvTable_SizingStretchProp 
                        row_background=False, no_host_extendX=True, no_pad_innerX=True,
                        borders_outerH=True, borders_innerV=True, borders_outerV=True):

                dpg.add_table_column(label="", init_width_or_weight=1) 
                dpg.add_table_column(label="", init_width_or_weight=1) 
                dpg.add_table_column(label="", init_width_or_weight=4) 

                with dpg.table_row(parent = table_id) as row_id:
                        dpg.add_text("")
                        dpg.add_text("Fruit")

                        with dpg.table(header_row=False):
                            dpg.add_table_column() 
                            dpg.add_table_column() 
                            with dpg.table_row():
                                dpg.add_text("Apples")
                                dpg.add_text("Pears")

                with dpg.table_row(parent = table_id) as row_id:
                        dpg.add_text("")
                        dpg.add_text("Property")

                        with dpg.table(header_row=False):
                            dpg.add_table_column() 
                            dpg.add_table_column() 
                            dpg.add_table_column() 
                            dpg.add_table_column() 
                            with dpg.table_row():
                                dpg.add_text("Weight")
                                dpg.add_text("Volume")
                                dpg.add_text("Weight")
                                dpg.add_text("Volume")

                with dpg.table_row(parent = table_id) as row_id:
                        dpg.add_text("Year")
                        dpg.add_text("Month")

                with dpg.table_row(parent = table_id) as row_id:
                        with dpg.table(header_row=False):
                            dpg.add_table_column() 
                            with dpg.table_row():
                                dpg.add_text("2022")
                        
                        with dpg.table(header_row=False):
                            dpg.add_table_column() 
                            with dpg.table_row():
                                dpg.add_text("Nov")
                            with dpg.table_row():
                                dpg.add_text("Dec")

                        with dpg.table(header_row=False):
                            dpg.add_table_column() 
                            dpg.add_table_column() 
                            dpg.add_table_column() 
                            dpg.add_table_column() 
                            with dpg.table_row():
                                dpg.add_text("0")
                                dpg.add_text("1")
                                dpg.add_text("2")
                                dpg.add_text("3")
                            with dpg.table_row():
                                dpg.add_text("1")
                                dpg.add_text("2")
                                dpg.add_text("3")
                                dpg.add_text("4")

                with dpg.table_row(parent = table_id) as row_id:
                        with dpg.table(header_row=False):
                            dpg.add_table_column() 
                            with dpg.table_row():
                                dpg.add_text("2023")

                        with dpg.table(header_row=False):
                            dpg.add_table_column() 
                            with dpg.table_row():
                                dpg.add_text("Jan")
                            with dpg.table_row():
                                dpg.add_text("Feb")

                        with dpg.table(header_row=False):
                            dpg.add_table_column() 
                            dpg.add_table_column() 
                            dpg.add_table_column() 
                            dpg.add_table_column() 
                            with dpg.table_row():
                                dpg.add_text("0")
                                dpg.add_text("1")
                                dpg.add_text("2")
                                dpg.add_text("3")
                            with dpg.table_row():
                                dpg.add_text("1")
                                dpg.add_text("2")
                                dpg.add_text("3")
                                dpg.add_text("4")
