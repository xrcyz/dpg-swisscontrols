import dearpygui.dearpygui as dpg

BACKGROUND_COLOUR = (0,0,0)

dpg.create_context()
dpg.create_viewport(width=800, height=450)
dpg.setup_dearpygui()

with dpg.theme() as global_theme:
    with dpg.theme_component(dpg.mvTable):
        dpg.add_theme_color(dpg.mvThemeCol_HeaderHovered, (255, 0, 0, 100), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_HeaderActive, (0, 0, 0, 0), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_Header, (0, 0, 0, 0), category=dpg.mvThemeCat_Core)

dpg.bind_theme(global_theme)

def clb_selectable(sender, app_data, user_data):
    print(f"Row {user_data[0]}, {user_data[1]}")


with dpg.window(tag="Table"):
    with dpg.table(header_row=True, resizable=True):
        dpg.add_table_column(label="Section")
        dpg.add_table_column(label="Fruit")
        dpg.add_table_column(label="Vegetables")

        # a single row that contains all data in the table
        with dpg.table_row():
            # index column
            with dpg.table(header_row=True):
                dpg.add_table_column(label="Product")

                with dpg.table_row():
                    with dpg.table(header_row=True, resizable=True):
                                dpg.add_table_column(label="Year")
                                dpg.add_table_column(label="Month")

                                with dpg.table_row():
                                    dpg.add_text("2022")
                                    dpg.add_text("Nov")
                                with dpg.table_row():
                                    dpg.add_text("")
                                    dpg.add_text("Dec")
                                with dpg.table_row():
                                    dpg.add_text("2023")
                                    dpg.add_text("Jan")
                                with dpg.table_row():
                                    dpg.add_text("")
                                    dpg.add_text("Feb")
                            

                        

            # multiindex column 1
            with dpg.table(header_row=True, resizable=True):
                dpg.add_table_column(label="Apples")
                dpg.add_table_column(label="Oranges")

                with dpg.table_row():
                    with dpg.table(header_row=True, resizable=True):
                        dpg.add_table_column(label="Volume")
                        dpg.add_table_column(label="Weight")

                        with dpg.table_row():
                            dpg.add_text("5")
                            dpg.add_text("10")
                        with dpg.table_row():
                            dpg.add_text("15")
                            dpg.add_text("20")
                        with dpg.table_row():
                            dpg.add_text("5")
                            dpg.add_text("10")
                        with dpg.table_row():
                            dpg.add_text("15")
                            dpg.add_text("20")

                    with dpg.table(header_row=True, resizable=True):
                        dpg.add_table_column(label="Volume")
                        dpg.add_table_column(label="Weight")

                        with dpg.table_row():
                            dpg.add_text("5")
                            dpg.add_text("10")
                        with dpg.table_row():
                            dpg.add_text("15")
                            dpg.add_text("20")
                        with dpg.table_row():
                            dpg.add_text("5")
                            dpg.add_text("10")
                        with dpg.table_row():
                            dpg.add_text("15")
                            dpg.add_text("20")
                
            # multiindex column 2
            with dpg.table(header_row=True, resizable=True):
                dpg.add_table_column(label="Avacados")
                dpg.add_table_column(label="Chillies")

                with dpg.table_row():
                    with dpg.table(header_row=True, resizable=True):
                        dpg.add_table_column(label="Volume")
                        dpg.add_table_column(label="Weight")

                        with dpg.table_row():
                            dpg.add_text("5")
                            dpg.add_text("10")
                        with dpg.table_row():
                            dpg.add_text("15")
                            dpg.add_text("20")
                        with dpg.table_row():
                            dpg.add_text("5")
                            dpg.add_text("10")
                        with dpg.table_row():
                            dpg.add_text("15")
                            dpg.add_text("20")
                            
                    with dpg.table(header_row=True, resizable=True):
                        dpg.add_table_column(label="Volume")
                        dpg.add_table_column(label="Weight")

                        with dpg.table_row():
                            dpg.add_text("5")
                            dpg.add_text("10")
                        with dpg.table_row():
                            dpg.add_text("15")
                            dpg.add_text("20")
                        with dpg.table_row():
                            dpg.add_text("5")
                            dpg.add_text("10")
                        with dpg.table_row():
                            dpg.add_text("15")
                            dpg.add_text("20")


dpg.show_viewport()
dpg.set_primary_window("Table", True)
dpg.start_dearpygui()
dpg.destroy_context()