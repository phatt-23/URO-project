from tkinter import Misc, ttk
from comps.component import Component

from comps.category_list import CategoryList
from comps.email_list import EmailList 
from comps.email_preview import EmailPreview
from lib import event_bus as eb
from comps import email_card, email_list, email_preview_toolbar
from comps.email_list_views import email_list_view
from lib import logger
import tkinter as tk


class EmailView(Component):
    def __init__(self, parent: Misc):
        Component.__init__(self, parent, label=__name__)

        self.paned_window = tk.PanedWindow(self, orient="horizontal")

        self.category_list = CategoryList(self)
        self.email_list = EmailList(self)
        self.email_preview = EmailPreview(self)

        self.category_list_weight = 1
        self.email_list_weight = 3
        self.email_preview_weight = 4

        self.paned_window.add(self.category_list)
        self.paned_window.add(self.email_list)

        eb.bus.subscribe(email_card.EventNames.PREVIEW, self._on_preview_click)
        eb.bus.subscribe(email_preview_toolbar.EventNames.CLOSE, self._on_preview_close)
        
        self.paned_window.bind("<Configure>", self.on_resize)

    def on_resize(self, _: tk.Event | None):
        total_weight = self.category_list_weight + self.email_list_weight 

        if self.is_widget_in_paned_window(self.email_preview):
            total_weight += self.email_preview_weight

        total_width = self.paned_window.winfo_width()
        self.paned_window.paneconfig(self.category_list, width=int(total_width * (self.category_list_weight / total_weight)))
        self.paned_window.paneconfig(self.email_list, width=int(total_width * (self.email_list_weight / total_weight)))
        
        if self.is_widget_in_paned_window(self.email_preview):
            self.paned_window.paneconfig(self.email_preview, width=int(total_width * (self.email_preview_weight / total_weight)))


    def is_widget_in_paned_window(self, widget: Misc):
        return any(str(widget) in str(pane) for pane in self.paned_window.panes())

    def show_preview_frame(self):
        logger.log.info("preview frame SHOW")
        if not self.is_widget_in_paned_window(self.email_preview):
            self.paned_window.add(self.email_preview)
        self.on_resize(None)

    def hide_preview_frame(self):
        logger.log.info("preview frame HIDE")
        if self.is_widget_in_paned_window(self.email_preview):
            self.paned_window.remove(self.email_preview)
        self.on_resize(None)

    def _on_preview_click(self, _: eb.Event):
        self.show_preview_frame() 
        return False

    def _on_preview_close(self, _: eb.Event):
        self.hide_preview_frame()
        return False

    def render(self):
        self.paned_window.pack(fill="both", expand=True, padx=10, pady=10)



