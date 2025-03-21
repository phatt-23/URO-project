from enum import StrEnum
import tkinter as tk
from typing import Dict, Optional
from tkinter import BooleanVar, ttk, Misc, StringVar, Text, font
from comps.component import Component
from models import EmailModel, UserModel
from lib import event_bus as eb
from lib.image_manager import ImageManager
from comps.utils import hover_popup as hp
from comps import email_card
from database import Database
from debug import DEFAULT_LOGGED_IN_EMAIL


class EventNames(StrEnum):
    PREVIEW_FRAME_CHANGE = "email_preview_content.preview_frame#change"


class EmailPreviewContent(Component):
    has_rendered_content = False
    sender: Optional[UserModel] = None
    email: Optional[EmailModel] = None

    def __init__(self, parent: Misc):
        Component.__init__(self, parent, label=__name__)

        self.header = Component(self, show_label=False)
        self.header.pack(side="top", fill="both", expand=False)
        self.header.grid_columnconfigure(1, weight=1)

        self.header_vars: Dict[str, StringVar] = {
            "sender": StringVar(),
            "recipient": StringVar(),
            "all_recipients": StringVar(),
            "subject": StringVar(),
            "email": StringVar(),
        }

        self.body_frame = Component(self, show_label=False)
        self.body_frame.pack(pady=0)

        self.body_text = Text(self.body_frame, state="disabled", highlightthickness=0, relief="flat", width=3, height=3)

        body_scrollbar = ttk.Scrollbar(self.body_frame, orient="vertical", command=self.body_text.yview)
        self.body_text.configure(yscrollcommand=body_scrollbar.set)
        self.body_text.pack(side="left", fill="both", expand=True, padx=(2, 0), pady=2)
        body_scrollbar.pack(side="right", fill="y", padx=(0, 2), pady=2)

        self.body_text_var = StringVar(self.body_text)
        
        def on_body_text_var_write():
            self.body_text.config(state="normal")
            self.body_text.delete(1.0, "end")
            self.body_text.insert(1.0, self.body_text_var.get())
            self.body_text.config(state="disabled")

        self.body_text_var.trace_add(
            "write", 
            lambda name, index, mode: on_body_text_var_write()
        )

        self.attachments_frame = Component(self, show_border=True, show_label=False)
        self.attachments_frame.pack(fill="both", expand=False)
        self.attachments_frame.grid_columnconfigure(0, weight=1)
        self.attachments_frame.grid_rowconfigure(1, weight=1)

        self.attachments_show_var = BooleanVar(value=False)
        self.attachments_show_checkbutton = ttk.Checkbutton(self.attachments_frame, text="Show Attachments", compound="left", variable=self.attachments_show_var)
        self.attachments_show_checkbutton.grid(row=0, column=0, sticky="sw", padx=2, pady=2)
        
        self.attachments_tree_frame = ttk.Frame(self.attachments_frame)
        self.attachments_tree_frame.grid(row=1, column=0, sticky="nsew", padx=2, pady=2)
        self.attachments_tree_frame.grid_remove()

        self.attachments_tree = ttk.Treeview(self.attachments_tree_frame, selectmode="browse", show="tree", height=10)
        attachments_tree_scrollbar = ttk.Scrollbar(self.attachments_tree_frame, orient="vertical", command=self.attachments_tree.yview)
        attachments_tree_scrollbar.pack(side="right", fill="y", padx=0, pady=0)
        self.attachments_tree.configure(yscrollcommand=attachments_tree_scrollbar.set)
        self.attachments_tree.pack(side="left", fill="x", expand=True, pady=0)

        self.attachemnt_tree_popup_menu = tk.Menu(self.attachments_tree)
        self.attachemnt_tree_popup_menu.add_command(label="Open")
        self.attachemnt_tree_popup_menu.add_command(label="Download")

        def on_attachments_show_var_write():
            if self.attachments_show_var.get():
                self.attachments_tree_frame.grid()
            else:
                self.attachments_tree_frame.grid_remove()

        # events
        self.attachments_show_var.trace_add("write", lambda name, index, mode: on_attachments_show_var_write())

        self.attachments_tree.bind("<Button-3>", self._on_attachments_tree_right_click)

        eb.bus.subscribe(email_card.EventNames.PREVIEW, self._on_preview_button_click)

    def _on_attachments_tree_right_click(self, e: tk.Event):
        identifier = self.attachments_tree.identify_row(e.y)
        if identifier:
            self.attachments_tree.selection_set(identifier)
            self.attachemnt_tree_popup_menu.tk_popup(e.x_root + 10, e.y_root + 10)

    def render(self):
        if self.sender and self.email and not self.has_rendered_content:
            self.has_rendered_content = True
            
            font_title = font.Font(size=14, weight="bold")

            title = ttk.Frame(self.header)
            title.pack(fill="x", padx=10, pady=5)

            ttk.Label(
                title, 
                textvariable=self.header_vars["subject"],
                font=font_title,
                anchor="w",
            ).pack(fill="x")

            img = ImageManager()

            sender_frame = ttk.Frame(self.header)
            sender_frame.pack(fill="x", padx=10, pady=(4, 0))

            ttk.Label(sender_frame, image=img.get("icon_account_circle")).grid(row=0, column=0, padx=10, pady=4, sticky="ew")
            sender_label = ttk.Label(sender_frame, textvariable=self.header_vars["sender"])
            sender_label.grid(row=0, column=1, padx=10, pady=4, sticky="ew")

            recipient_frame = ttk.Frame(self.header)
            recipient_frame.pack(fill="x", padx=10, pady=(0, 5))

            ttk.Label(recipient_frame, image=img.get("icon_account_circle")).grid(row=1, column=0, padx=10, pady=(0, 10), sticky="ew")
            recipient_label = ttk.Label(recipient_frame, textvariable=self.header_vars["recipient"])
            recipient_label.grid(row=1, column=1, padx=10, pady=(0, 10), sticky="ew")

            hp.HoverPopupText(sender_label, text=self.header_vars["email"])
            hp.HoverPopupText(recipient_label, text=self.header_vars["all_recipients"])


    def _on_preview_button_click(self, e: eb.Event):
        # in drafts and sent mail the sender is the user
        sender = e.data["sender"]
        email = e.data["email"]

        assert isinstance(sender, UserModel)
        assert isinstance(email, EmailModel)

        self.sender = sender
        self.email = email 

        if sender.first_name and sender.last_name:
            sender_name = sender.first_name + " " + sender.last_name 
        else:
            sender_name = sender.email
        sender_info = "From " + sender_name + " on " + email.sent_at

        db = Database() 
        recipients = db.fetch_recipients_by_email_id(email.email_id)

        logged_user = None

        for r in recipients: 
            if r.email == DEFAULT_LOGGED_IN_EMAIL:
                logged_user = r
                recipients.remove(r)
                break
        
        if isinstance(logged_user, UserModel):
            recipient_info = f"To {logged_user.first_name} {logged_user.last_name}" 

            if recipients: 
                recipient_info += f" and {len(recipients)} others"

            all_recipients = "\n".join(f"{r.email} :: {r.first_name} {r.last_name}" for r in [logged_user] + recipients)
        else:
            if recipients:
                recipient_info = f"To {recipients[0].first_name} {recipients[0].last_name}"
                if len(recipients) > 1:
                    recipient_info += f" and {len(recipients)} others"
                all_recipients = "\n".join(f"{r.email} :: {r.first_name} {r.last_name}" for r in recipients)
            else:
                recipient_info = "No recipients"
                all_recipients = "no recipients"

        attachments = db.fetch_attachments_by_email_id(email.email_id)

        # update the state
        self.header_vars["sender"].set(sender_info)
        self.header_vars["recipient"].set(recipient_info)
        self.header_vars["all_recipients"].set(all_recipients)
        self.header_vars["subject"].set(email.subject)
        self.header_vars["email"].set(sender.email)
        self.body_text_var.set(email.body)

        # clear everything from the tree and insert the fetched ones
        self.attachments_tree.delete(*self.attachments_tree.get_children())
        for a in attachments:
            self.attachments_tree.insert("", "end", text=a.filepath)

        # render changes 
        self.render()

        # notify
        eb.bus.publish(EventNames.PREVIEW_FRAME_CHANGE)

        return False

    def _update_content(self):

        pass
