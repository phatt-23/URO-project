from enum import StrEnum
import re
from tkinter import BooleanVar, Text, ttk, Misc, StringVar, filedialog
from typing import Dict, Iterable, List, Mapping, Union, override
from comps.component import Component
from lib.image_manager import ImageManager
from lib import event_bus as eb
import debug
from stores import email_with_attachments_store
from stores.email_with_attachments_store import (
    ActionEnum,
    EmailState, 
    EmailWithAttachmentsStore, 
    ValidationState
)
from preferences import FontBuilder
from lib.logger import log


class EventNames(StrEnum):
    SEND_BUTTON_CLICK = "email_editor.send_button#click"
    SAVE_BUTTON_CLICK = "email_editor.save_button#click"
    ATTACH_BUTTON_CLICK = "email_editor.attach_button#click"

    BEGIN_EDITING_EMAIL = "email_editor.editing_email#begin"
    END_EDITING_EMAIL = "email_editor.editing_email#end"


class HeaderEntry(ttk.Entry):
    var: StringVar
    
    def __init__(self, parent: Misc, var: StringVar, *args, **kwargs):
        super().__init__(parent, textvariable=var, *args, **kwargs)
        self.var = var


class EmailEditor(Component):
    is_valid_recepient_email: bool
    toolbar_frame: Component
    header_frame: Component
    body_frame: Component
    is_editing_draft: BooleanVar 

    def __init__(self, parent: Misc):
        Component.__init__(self, parent, label=__name__)

        self.is_valid_recepient_email = False
        self.is_editing_draft = BooleanVar(value=False)

        img = ImageManager()

        self.editor_comps: Dict[str, Component] = {}

        self.editing_draft_frame = Component(self, "editing_draft_frame", show_border=True)
        self.toolbar_frame = Component(self, "toolbar_frame", show_border=False)
        self.header_frame = Component(self, "header_frame")
        self.body_frame = Component(self, "body_frame")

        # toolbar_frame
        ttk.Button(
            self.toolbar_frame, 
            text="Send", 
            image=img.get("icon_send"), 
            compound="left", 
            style="LeftAlign.TButton", 
            command=self.on_send_button_click).pack(side="left", padx=(0, 2), pady=0)

        ttk.Button(
            self.toolbar_frame, 
            text="Save", 
            image=img.get("icon_save"), 
            compound="left", 
            style="LeftAlign.TButton", 
            command=self.on_save_button_click).pack(side="left", padx=2, pady=0)

        ttk.Button(
            self.toolbar_frame, 
            text="Attach", 
            image=img.get("icon_attach_file"), 
            compound="left", style="LeftAlign.TButton",
            command=lambda: eb.bus.publish(EventNames.ATTACH_BUTTON_CLICK)).pack(side="right", padx=(2, 0), pady=0)

        # editing_draft_frame
        ttk.Label(
            self.editing_draft_frame,
            text="You are editing a draft.",
            font=FontBuilder().weight("bold").build(),
        ).pack(side="left", padx=2, pady=2)

        def i_dont_want_to_edit_a_draft():
            ewa = EmailWithAttachmentsStore()
            ewa.clear_editing_email_id()

        ttk.Button(
            self.editing_draft_frame,
            text="I don't want to edit a draft.",
            image=img.get("icon_close"),
            compound="left", 
            style="LeftAlign.TButton", 
            command=i_dont_want_to_edit_a_draft
        ).pack(side="right", padx=2, pady=2)

        
        # header_frame
        self.entries: Dict[str, HeaderEntry] = {
            "sender": HeaderEntry(self.header_frame, var=StringVar(value=debug.DEFAULT_LOGGED_IN_EMAIL), state="readonly"),
            "recipients": HeaderEntry(self.header_frame, var=StringVar(value=""), state="enabled"),
            "subject": HeaderEntry(self.header_frame, var=StringVar(value=""), state="enabled"),
        }
        
        # bind the email validation
        self.entries["recipients"].bind("<KeyRelease>", lambda _: self.check_email(self.entries["recipients"].get()))

        self.header_frame.grid_columnconfigure(1, weight=10)
        self.header_frame.grid_columnconfigure(0, weight=1)

        for index, (label, entry) in enumerate(self.entries.items()):
            ttk.Label(self.header_frame, text=label.capitalize(), anchor="w").grid(row=index, column=0, padx=2, pady=2, sticky="ew")
            entry.grid(row=index, column=1, padx=2, pady=2, sticky="ew")
            # entry.var.trace_add("write", lambda name, index, mode, var=entry.var: print(name, mode, var.get()))


        # body_frame 
        self.textarea = Text(self.body_frame, width=48, height=12, highlightthickness=0, borderwidth=1, border=1)

        textarea_scrollbar = ttk.Scrollbar(self.body_frame, orient="vertical", command=self.textarea.yview)
        self.textarea.configure(yscrollcommand=textarea_scrollbar.set)

        self.textarea.pack(side="left", fill="both", expand=True, padx=(2, 0), pady=2)
        textarea_scrollbar.pack(side="right", fill="y", padx=(0, 2), pady=2)


        def toggle_editing_mail_frame():
            if self.is_editing_draft.get():
                log.info("You are editing draft email.")
                self.editing_draft_frame.grid(row=0, column=0, padx=4, pady=4, sticky="nsew")
            else:
                log.info("You are NOT editing draft email.")
                self.editing_draft_frame.grid_remove()


        self.is_editing_draft.trace_add(
            "write", 
            lambda *_: toggle_editing_mail_frame()
        )


        # parent: email_editor
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        self.toolbar_frame.grid(row=1, column=0, padx=4, pady=10, sticky="nsew")

        self.header_frame.grid(row=2, column=0, padx=4, pady=0, sticky="nsew")
        self.body_frame.grid(row=3, column=0, padx=4, pady=(4, 4), sticky="nsew")

        # events
        eb.bus.subscribe(EventNames.ATTACH_BUTTON_CLICK, self.on_attach_button_click)
        eb.bus.subscribe(email_with_attachments_store.EventNames.EDITING_EMAIL_SET, lambda _: self.is_editing_draft_email(True))
        eb.bus.subscribe(email_with_attachments_store.EventNames.EDITING_EMAIL_CLEARED, lambda _: self.is_editing_draft_email(False))


    def on_attach_button_click(self, _: eb.Event):
        attachments = filedialog.askopenfilenames(title="Select Attachments")

        eb.bus.publish("email_editor.attachments#selected", data={
            "attachments": attachments
        })

        return True

    
    def get_content(self):
        data: Dict[str, bool | str | Iterable[str]] = {}
        
        data["sender_email"] = self.entries["sender"].get()
        data["subject"] = self.entries["subject"].get()
        data["body"] = self.textarea.get(1.0, "end")
        data["recipients"] = self.entries["recipients"].get()
        
        return data


    def on_send_button_click(self):
        error_messages: List[str] = []

        data = self.get_content()

        recipients = data["recipients"]
        assert isinstance(recipients, str)

        self.check_email(recipients) 

        if not self.is_valid_recepient_email:
            error_messages.append(f"recipient's email not valid: {data["recipients"]}")

        if not data["subject"]:
            error_messages.append("missing subject")

        assert isinstance(data["body"], Iterable)

        if len([c for c in data["body"] if not c.isspace()]) == 0:
            error_messages.append("missing body")

        valid = len(error_messages) == 0

        ewa = EmailWithAttachmentsStore()
        sender_email = self.entries["sender"].get()
        subject = self.entries["subject"].get()
        body = self.textarea.get(1.0, "end")
        recipient_emails = self.entries["recipients"].get()
        recipient_emails = [re.strip(" ") for re in recipient_emails.split(",")]
        
        ewa.set_action(ActionEnum.SEND)
        ewa.set_email(EmailState(sender_email, subject, body, recipient_emails))
        ewa.set_validation(ValidationState(valid, error_messages))

        eb.bus.publish(EventNames.SEND_BUTTON_CLICK)

        if valid:
            self.clear_entries()
            self.clear_body()
            self.is_editing_draft_email(False)

        return True

    def on_save_button_click(self):
        # notify that the save button has been pressed

        # store the content of the email to the centralized store
        ewa = EmailWithAttachmentsStore()
        sender_email = self.entries["sender"].get()
        subject = self.entries["subject"].get()
        body = self.textarea.get(1.0, "end")
        recipient_emails = self.entries["recipients"].get()
        recipient_emails = [re.strip(" ") for re in recipient_emails.split(",")]

        ewa.set_action(ActionEnum.SAVE)
        ewa.set_email(EmailState(sender_email, subject, body, recipient_emails))

        eb.bus.publish(EventNames.SAVE_BUTTON_CLICK)
        eb.bus.publish(EventNames.END_EDITING_EMAIL)

        self.clear_entries()
        self.clear_body()
        self.is_editing_draft_email(False)

        return True


    def check_email(self, new_emails_value: str):
        emails = new_emails_value.split(",")
        regex = r"^([a-zA-Z0-9][a-zA-Z0-9._%+-]{0,63}[a-zA-Z0-9]@(?:[a-zA-Z0-9-]{1,63}\.){1,125}[a-zA-Z]{2,63}$)"

        self.is_valid_recepient_email = True

        for email in emails:
            self.is_valid_recepient_email = re.match(regex, email.strip(" ")) is not None

        foreground = "red" if not self.is_valid_recepient_email else ""
        self.entries["recipients"].configure(foreground=foreground)

        return self.is_valid_recepient_email


    def clear_entries(self):
        entries: dict[str, str] = {}
        for k, e in self.entries.items():
            if k == "sender":
                continue
            entries[k] = e.var.get()
            e.var.set("")

        return entries


    def clear_body(self):
        current_state = self.textarea.cget("state")
        self.textarea.configure(state="normal")
        body = self.textarea.get(1.0, "end")
        self.textarea.delete(1.0, "end")
        self.textarea.configure(state=current_state)
        return body

    
    def insert_body(self, body: str):
        current_state = self.textarea.cget("state")
        self.textarea.configure(state="normal")
        self.textarea.delete(1.0, "end")
        self.textarea.insert(1.0, body)
        self.textarea.configure(state=current_state)
        

    def insert_entries(self, entries: Mapping[str, Union[str, list[str]]]):
        for k,v in entries.items():
            self.entries[k].var.set(", ".join(v) if isinstance(v, list) else v)
        self.check_email(self.entries["recipients"].get())


    def is_editing_draft_email(self, value: bool | None = None):
        if isinstance(value, bool):
            log.info(f"Setting is_editing_draft to {value}")
            self.is_editing_draft.set(value)

        return self.is_editing_draft.get()


    @override
    def enable(self):
        super().enable()
        self.entries["sender"].configure(state="readonly")

