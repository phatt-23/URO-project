from dataclasses import dataclass
from tkinter import Misc, ttk
from typing import Dict
from comps.component import Component

from lib import event_bus as eb
from lib.image_manager import ImageManager
from comps import email_preview_toolbar


class EventNames:
    MAIL = "layout_sidebar.mail_view_button#click"
    COMPOSE = "layout_sidebar.compose_view_button#click"
    ADDRESS_BOOK = "layout_sidebar.address_book_view_button#click"
    CALENDAR = "layout_sidebar.calendar_view_button#click"
    LOG_OUT = "layout_sidebar.logout_button#click"


@dataclass
class ButtonConfig:
    parent: Misc
    event_name: str 
    icon_image_key: str


class PublishingButton(ttk.Button):
    def __init__(self, text: str, config: ButtonConfig):
        super().__init__(
            config.parent, 
            text=" ".join([word.capitalize() for word in text.split("_")]),
            command=lambda: eb.bus.publish(config.event_name, data={
                "name": text
            }),
            image=ImageManager().get(config.icon_image_key),
            compound="left",
        )


class LayoutSidebar(Component):
    def __init__(self, parent: Misc):
        Component.__init__(self, parent, label=__name__)

        self.top_frame = ttk.Frame(self)

        buttons_configs = {
            "mail"         : ButtonConfig(self.top_frame, EventNames.MAIL, "icon_email"),
            "compose"      : ButtonConfig(self.top_frame, EventNames.COMPOSE, "icon_create"),
            "address_book" : ButtonConfig(self.top_frame, EventNames.ADDRESS_BOOK, "icon_contacts"),
            # "calendar"     : ButtonConfig(self.top_frame, EventNames.CALENDAR, "icon_calendar_month"),
        }

        self.top_buttons: Dict[str, ttk.Button] = {}

        for name, config in buttons_configs.items():
            self.top_buttons[name] = PublishingButton(name, config)

        self.logout_btn = PublishingButton("Log-Out", ButtonConfig(self, EventNames.LOG_OUT, "icon_logout"))

        eb.bus.subscribe(email_preview_toolbar.EventNames.EDIT, self._on_email_preview_toolbar_edit_click)

        eb.bus.subscribe(EventNames.MAIL, self._on_sidebar_button_click)
        eb.bus.subscribe(EventNames.COMPOSE, self._on_sidebar_button_click)
        eb.bus.subscribe(EventNames.ADDRESS_BOOK, self._on_sidebar_button_click)
        eb.bus.subscribe(EventNames.CALENDAR, self._on_sidebar_button_click)

        self.set_highlighted_button("mail")

    def set_highlighted_button(self, name: str):
        style = ttk.Style()
        style.configure("LeftAlign.TButton", anchor="w")
        style.configure("Highlighted.TButton", font=("Arial", 10, "underline"), borderwidth=2, relief="ridge", anchor="w")

        for btn in self.top_buttons.values():
            btn.configure(style="LeftAlign.TButton")
        self.top_buttons[name].configure(style="Highlighted.TButton")


    def _on_sidebar_button_click(self, e: eb.Event):
        button_name = e.data["name"]
        self.set_highlighted_button(button_name) 
        return False

    def _on_email_preview_toolbar_edit_click(self, _: eb.Event):
        self.top_buttons["compose"].invoke()
        return False


    def render(self):
        for _, button in self.top_buttons.items():
            button.pack(anchor="n", pady=2, fill="x", expand=True)

        self.top_frame.pack(anchor="n", fill="x", padx=2, pady=0, expand=True)
        self.logout_btn.pack(anchor="s", padx=2, pady=2, fill="x", expand=True)


