from enum import StrEnum
from comps.component import Component
from models import UserModel, EmailModel
from tkinter import ttk, Misc
from lib import event_bus as eb


class EventNames(StrEnum):
    PREVIEW = "email_card.preview_button#click"


class EmailCard(Component):
    sender: UserModel
    email: EmailModel

    def __init__(self, parent: Misc, sender: UserModel, email: EmailModel):
        Component.__init__(self, parent, label=__name__)

        self.sender = sender
        self.email = email

        # sender name and email at top
        top_frame = ttk.Frame(self)
        top_frame.pack(padx=10, pady=(2, 0), fill="both", expand=True)

        top_frame.grid_rowconfigure(0, weight=1)
        top_frame.grid_columnconfigure((0, 1), weight=1)

        sender_name = f"{sender.first_name} {sender.last_name}" if sender.first_name and sender.last_name else ""
        sender_email = f"<{sender.email}>"
        sender_info = sender_name + " " + sender_email

        sent_at = email.sent_at
        ttk.Label(top_frame, text=sender_info, anchor="w").grid(row=0, column=0, padx=(0, 10), sticky="nsew")
        ttk.Label(top_frame, text=sent_at, anchor="e").grid(row=0, column=1, sticky="nsew")

        # subject and view button at the bottom
        bottom_frame = ttk.Frame(self)
        bottom_frame.pack(padx=10, pady=(0, 2), fill="both", expand=True)

        bottom_frame.grid_rowconfigure(0, weight=1)
        bottom_frame.grid_columnconfigure(0, weight=1)

        subject_label = ttk.Label(bottom_frame, text=email.subject, wraplength=300, anchor="w")
        subject_label.grid(row=0, column=0, padx=(0, 10), sticky="nsew")

        preview_button = ttk.Button(
            bottom_frame, 
            text="Preview", 
            command=lambda s=self.sender, e=self.email: eb.bus.publish(EventNames.PREVIEW, data={
                "sender": s,
                "email": e
            })
        )
        preview_button.grid(row=0, column=1, padx=(10, 0), pady=10, sticky="nsew")
   

    def render(self):
        self.pack(fill="x", padx=2, pady=2)

