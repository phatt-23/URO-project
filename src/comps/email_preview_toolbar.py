
from dataclasses import dataclass
from enum import StrEnum
from tkinter import Button, font, ttk, Misc
from typing import Optional
from comps.component import Component
from lib.image_manager import ImageManager
from comps.utils.hover_popup import HoverPopupText
from preferences import FontBuilder
from lib import event_bus as eb
from models import EmailModel, EmailStatus
from comps import email_card
from stores.email_with_attachments_store import EmailWithAttachmentsStore


class EventNames(StrEnum):
    REPLY   = "email_preview_toolbar.reply_button#click"
    FORWARD = "email_preview_toolbar.forward_button#click"
    REMOVE  = "email_preview_toolbar.remove_button#click"
    EDIT    = "email_preview_toolbar.edit_button#click"
    CLOSE   = "email_preview_toolbar.close_button#click"


@dataclass
class ButtonSettings():
    icon: str
    event_name: str


class EmailPreviewToolbar(Component):
    email: Optional[EmailModel] = None

    def __init__(self, parent: Misc):
        Component.__init__(self, parent, label=__name__, show_border=True, show_label=False)
       
        self.buttons_frame = Component(self, show_border=False)

        self.buttons_settings = {
            "reply" : ButtonSettings("icon_reply", EventNames.REPLY),
            "forward" : ButtonSettings("icon_forward", EventNames.FORWARD),
            "remove" : ButtonSettings("icon_delete", EventNames.REMOVE),
            "edit" : ButtonSettings("icon_edit", EventNames.EDIT),
            "close" : ButtonSettings("icon_close", EventNames.CLOSE)
        }

        self.buttons: dict[str, ttk.Button] = {}

        img = ImageManager()
        button_style = ttk.Style()
        button_style.configure("SmallText.TButton", font=FontBuilder().size("small").weight("normal").build())

        for name, settings in self.buttons_settings.items():
            self.buttons[name] = ttk.Button(
                self.buttons_frame, 
                text=name.capitalize(), 
                image=img.get(settings.icon), 
                compound="top", 
                style="SmallText.TButton",
                state="disabled",
                command=lambda s=settings: eb.bus.publish(s.event_name, data={
                    "email": self.email
                })
            )
            HoverPopupText(self.buttons[name], name.capitalize())

        def on_edit_click():
            ewa = EmailWithAttachmentsStore()
            assert self.email, "Can click on edit iff some email is in the preview"
            ewa.set_editing_email_id(self.email.email_id)
            eb.bus.publish(EventNames.EDIT, data={
                "email": self.email
            })

        self.buttons["edit"].configure(command=on_edit_click)

        eb.bus.subscribe(email_card.EventNames.PREVIEW, self._on_preview_button_click)


    def render(self):
        self.buttons_frame.grid_columnconfigure(list(range(len(self.buttons))), weight=1, uniform="a")
        for index, btn in enumerate(self.buttons.values()):
            btn.grid(row=0, column=index, padx=2, sticky="nsew")
        self.buttons["close"].grid(padx=(20, 2))
        self.buttons_frame.pack(anchor="center", padx=1, pady=4, expand=False, fill="none")


    def _on_preview_button_click(self, e: eb.Event):
        self.email = e.data["email"] 
        assert isinstance(self.email, EmailModel)

        for btn in self.buttons.values():
            btn.configure(state="enabled")

        self.buttons["edit"].configure(
            state="enabled" if self.email.status == EmailStatus.DRAFT else "disabled"
        )

        return False



