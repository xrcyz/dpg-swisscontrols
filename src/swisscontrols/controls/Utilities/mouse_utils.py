import threading

class ClickHandler:
    """
    A handler class to differentiate between single and double clicks.
    
    Example:
        def on_single_click(sender):
            print(f"Single click detected! Sender: {sender}")

        def on_double_click(sender):
            print(f"Double click detected! Sender: {sender}")

        click_handler = ClickHandler(on_single_click, on_double_click)

        def dpg_callback(sender):
            click_handler.handle_click(sender)
    """
    
    def __init__(self, single_click_callback, double_click_callback):
        self.single_click_timer = None
        self.single_click_callback = single_click_callback
        self.double_click_callback = double_click_callback

    def _single_click_callback(self, *args, **kwargs):
        self.reset_timer()
        if self.single_click_callback:
            self.single_click_callback(*args, **kwargs)

    def _double_click_callback(self, *args, **kwargs):
        self.reset_timer()
        if self.double_click_callback:
            self.double_click_callback(*args, **kwargs)

    def reset_timer(self):
        if self.single_click_timer is not None:
            self.single_click_timer.cancel()
            self.single_click_timer = None

    def handle_click(self, *args, **kwargs):
        if self.single_click_timer is not None:
            # This means the handle_click function has been called twice in quick succession
            self.reset_timer()  # Cancel the single click timer
            self._double_click_callback(*args, **kwargs)
        else:
            self.single_click_timer = threading.Timer(0.2, self._single_click_callback, args=args, kwargs=kwargs)  # 200 ms delay
            self.single_click_timer.start()