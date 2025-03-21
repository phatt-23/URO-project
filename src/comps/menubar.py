from enum import StrEnum
from tkinter import Menu, Tk
from tkinter import ttk

from lib import event_bus as eb
from lib.logger import log
from comps.component import Component
from comps.log_viewer import LogViewer


class EventNames(StrEnum):
    FILE_QUIT           = "menu_bar.file_menu.quit_button#click"
    EDIT_PREFERENCES    = "menu_bar.edit_menu.preferences_button#click"

    DEBUG_PRINT_HIERARCHY = "menu_bar.debug_menu.print_hierarchy_button#click"
    DEBUG_SHOW_HIERARCHY = "menu_bar.debug_menu.show_hierarchy_button#click"
    DEBUG_SHOW_WIDGET_DETAIL = "menu_bar.debug_menu.print_comp_detail_button#click"


class MenuBar(Component):
    def __init__(self, parent_window: Tk):
        Component.__init__(self, parent_window, label=__name__)

        self.menu = Menu(parent_window)
        parent_window.configure(menu=self.menu)

        file_menu = Menu(self.menu, tearoff=False)
        edit_menu = Menu(self.menu, tearoff=False)
        view_menu = Menu(self.menu, tearoff=False)
        debug_menu = Menu(self.menu, tearoff=False)

        file_menu.add_command(label="Quit", command=lambda: eb.bus.publish(EventNames.FILE_QUIT))

        edit_menu.add_command(label="Preferences", command=lambda: eb.bus.publish(EventNames.EDIT_PREFERENCES))

        debug_menu.add_command(label="Print Hierarchy", command=lambda: eb.bus.publish(EventNames.DEBUG_PRINT_HIERARCHY))
        debug_menu.add_command(label="Show Hierarchy", command=lambda: eb.bus.publish(EventNames.DEBUG_SHOW_HIERARCHY))
        debug_menu.add_command(label="Show Widget Detail", command=lambda: eb.bus.publish(EventNames.DEBUG_SHOW_WIDGET_DETAIL))
        debug_menu.add_command(label="Open Log Viewer", command=lambda: LogViewer(parent_window, log.get_logger()))

        self.menu.add_cascade(label="File", menu=file_menu)
        self.menu.add_cascade(label="Edit", menu=edit_menu)
        self.menu.add_cascade(label="View", menu=view_menu)
        self.menu.add_cascade(label="Debug", menu=debug_menu)

