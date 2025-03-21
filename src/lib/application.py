#!/usr/bin/env python3

from typing import Callable
from tkinter import Tk, ttk
from lib import event_bus as eb
from lib.types import Singleton
import tkinter as tk
from tkinterdnd2 import TkinterDnD


class Application(Singleton):
    main_frame: ttk.Frame
    tk_instance: TkinterDnD.Tk

    def __init__(self):
        self.tk_instance = TkinterDnD.Tk()
        self.tk_instance.option_add('*tearOff', False)

        self.main_frame = ttk.Frame(self.tk_instance)
        self.main_frame.pack_configure(fill="both", expand=True, padx=0, pady=0)

    def render(self):
        raise NotImplementedError("No rendering is probably wrong.")

    def mainloop(self, n: int = 0) -> None:
        self.main_frame.pack()

        self.render()
        Tk.mainloop(self.tk_instance, n)

    def start_capture(self):
        """Bind mouse clicks globally to capture the widget under the cursor."""
        self.tk_instance.bind("<Button-1>", self.on_click)

    def on_click(self, event: tk.Event):
        """Identify the widget at the clicked position and display its info."""
        self.tk_instance.unbind("<Button-1>")  

        widget = self.tk_instance.winfo_containing(event.x_root, event.y_root)
        eb.bus.publish("app_widget_capture#caught", { "tk_event": event, "captured_widget": widget })


def application_entry_point():
    """Will create and start the application at its calling point."""
    app = create_application()
    app.mainloop()


# Function pointer for application creation (to be overridden)
_create_application: Callable[[], Application] | None = None


def create_application() -> Application:
    """If an application is registered it will create one."""
    if _create_application is None:
        raise NotImplementedError("No application has been registered. Please call register_application().")
    return _create_application()


def register_application(factory: Callable[[], Application]):
    """Registers a callback creating an application."""
    global _create_application
    _create_application = factory


