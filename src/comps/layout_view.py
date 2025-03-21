from tkinter import Misc
from comps.component import Component

import lib.event_bus as eb

from comps.views.compose_view import ComposeView
from comps.views.email_view import EmailView
from comps.views.address_book_view import AddressBookView
from comps.views.calendar_view import CalendarView


class LayoutView(Component):
    current_view: Component

    def __init__(self, parent: Misc):
        Component.__init__(self, parent, label=__name__)

        self.views = {
            "mail_view" : EmailView(self),
            "compose_view" : ComposeView(self),
            "address_book_view" : AddressBookView(self),
            "calendar_view" : CalendarView(self),
        }

        self.current_view = self.views["mail_view"]

        for key in self.views:
            eb.bus.subscribe(f"layout_sidebar.{key}_button#click", self.on_view_button_click)

        eb.bus.subscribe("layout_sidebar.logout_button#click", self.on_logout_button_click)

    def on_logout_button_click(self, _: eb.Event):
        print("logout and show login view")
        return False

    def on_view_button_click(self, e: eb.Event):
        for name, comp in self.views.items():
            if name in e.name:
                self.current_view = comp
                break
        self.render()
        return False

    def render(self):
        for _, comp in self.views.items():
            comp.pack_forget()
        self.current_view.pack(padx=2, pady=2)
        self.current_view.render()


