from tkinter import Misc, Toplevel, ttk
from lib import event_bus as eb
from comps.component import Component
from comps.attachments_sidebar import AttachmentSidebar
from comps.email_editor import EmailEditor
from lib.image_manager import ImageManager 
from comps import email_preview_toolbar
from models import EmailModel
from database import Database
import tkinter as tk


class EventNames:
    OPEN_IN_NEW_WINDOW = "email_editor.open_in_new_window_button#click"


class ComposeView(Component):
    def __init__(self, parent: Misc):
        Component.__init__(self, parent, label=__name__, show_border=False)

        self.paned_window = tk.PanedWindow(self, orient="horizontal")

        self.left_pane = Component(self, show_border=False, show_label=False)
        self.left_pane.columnconfigure(0, weight=1)
        self.left_pane.rowconfigure(0, weight=1)

        self.email_editor = EmailEditor(self.left_pane)
        self.email_editor.grid_configure(row=0, column=0, columnspan=2, sticky="nsew")

        img = ImageManager()

        self.open_in_new_window_button = ttk.Button(
            self.left_pane, 
            text="Open in new window", 
            image=img.get("icon_open_in_new"), 
            compound="left", style="LeftAlign.TButton",
            command=lambda: eb.bus.publish(EventNames.OPEN_IN_NEW_WINDOW)
        )
        self.open_in_new_window_button.grid(row=1, column=1, sticky="e", padx=1, pady=10)

        self.attach_sidebar = AttachmentSidebar(self)

        self.paned_window.add(self.left_pane)
        self.paned_window.add(self.attach_sidebar)
        self.left_weight = 8
        self.right_weight = 4

        self.paned_window.pack(fill="both", expand=True)
        
        # events
        eb.bus.subscribe(EventNames.OPEN_IN_NEW_WINDOW, self._on_open_in_new_window_button_click)
        eb.bus.subscribe(email_preview_toolbar.EventNames.EDIT, self._on_email_preview_toolbar_edit_click)
        self.paned_window.bind("<Configure>", self.on_resize)

    def on_resize(self, e: tk.Event):
        total_width = e.width

        total_weight = self.left_weight + self.right_weight
        left_pane_width = total_width * (self.left_weight / total_weight)
        right_pane_width = total_width * (self.right_weight / total_weight)
        # print(total_width, left_pane_width, right_pane_width)

        self.paned_window.paneconfigure(self.left_pane, width=int(left_pane_width))
        self.paned_window.paneconfigure(self.attach_sidebar, width=int(right_pane_width))

        self.paned_window.update_idletasks()
        self.update_idletasks()

    def render(self):
        pass

    def _on_email_preview_toolbar_edit_click(self, e: eb.Event):
        email = e.data["email"]

        assert isinstance(email, EmailModel)

        db = Database()

        sender = db.fetch_user_by_id(email.sender_id)
        assert sender

        recs = db.fetch_recipients_by_email_id(email.email_id)

        attchs = db.fetch_attachments_by_email_id(email.email_id)

        self.email_editor.insert_entries({
            "sender": sender.email,
            "recipients": [r.email for r in recs],
            "subject": email.subject,
        })

        self.email_editor.insert_body(email.body)

        self.attach_sidebar.add_attachments([a.filepath for a in attchs])
        
        self.email_editor.is_editing_draft_email(True)

        return False


    def _on_open_in_new_window_button_click(self, _: eb.Event):
        """Move the email editor to a new window. Data in the compose view is persistent."""
        
        # prevent multiple opened window
        if hasattr(self, "has_new_window_open") and self.has_new_window_open: 
            return True 

        # disable event subs
        main_window_event_subs = eb.bus.unsubscribe_for(self.email_editor)
        main_window_event_subs += eb.bus.unsubscribe_for(self.attach_sidebar)

        # clear entries and attachments
        main_window_entries = self.email_editor.clear_entries()
        main_window_body = self.email_editor.clear_body()
        main_window_attchs = self.attach_sidebar.clear_attachment_list()

        self.email_editor.disable()
        self.attach_sidebar.disable()

        self.open_in_new_window_button.configure(state="disabled")

        # Create a new window
        new_window = Toplevel(self)
        new_window.title("Email Editor")
        new_window.geometry("800x800")
        self.has_new_window_open = True

        paned_window = ttk.PanedWindow(new_window, orient="horizontal")
        paned_window.pack(fill="both", expand=True)

        editor = EmailEditor(new_window)
        attch_sidebar = AttachmentSidebar(new_window)
        
        # populate the entries and attachments with 
        # the content from main window
        editor.insert_entries(main_window_entries)
        editor.insert_body(main_window_body)
        editor.is_editing_draft_email(self.email_editor.is_editing_draft_email())
        attch_sidebar.add_attachments(main_window_attchs)

        paned_window.add(editor, weight=4)
        paned_window.add(attch_sidebar, weight=1)

        def new_window_destroy():
            eb.bus.unsubscribe_for(editor)
            eb.bus.unsubscribe_for(attch_sidebar)

            self.open_in_new_window_button.configure(state="enabled")
            self.has_new_window_open = False

            # put the new entries and attachments into main window
            self.email_editor.insert_entries(editor.clear_entries())
            self.email_editor.insert_body(editor.clear_body())
            self.attach_sidebar.add_attachments(attch_sidebar.clear_attachment_list())

            # set the events of the main window back
            for sub in main_window_event_subs:
                eb.bus.subscribe(sub.event_name, sub.event_callback)
            
            # reenable the widgets inside them
            self.email_editor.enable()
            self.attach_sidebar.enable()

            new_window.destroy()
            return False

        new_window.protocol("WM_DELETE_WINDOW", new_window_destroy)


        return True

