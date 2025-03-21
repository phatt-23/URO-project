import tkinter as tk
from os.path import isfile
from tkinter import Misc, ttk

from tkinterdnd2 import DND_FILES 
from tkinterdnd2.TkinterDnD import DnDEvent

from comps import email_editor, email_preview_toolbar
from comps.component import Component
from database import Database
from lib import event_bus as eb
from lib.image_manager import ImageManager
from lib.logger import log
from models import EmailModel, EmailStatus
from stores.email_with_attachments_store import (
    AttachmentsState,
    EmailWithAttachmentsStore,
)


class AttachmentSidebarPopupMenu(tk.Menu):
    def __init__(self, parent: Misc):
        super().__init__(parent)

        self.add_command(label="Open", command=lambda: eb.bus.publish("attachment_sidebar.popup_menu.open_option#click"))
        self.add_command(label="Remove", command=lambda: eb.bus.publish("attachment_sidebar.popup_menu.remove_option#click"))


class AttachmentSidebar(Component):
    popup_menu: AttachmentSidebarPopupMenu

    def __init__(self, parent: Misc):
        Component.__init__(self, parent, label=__name__)

        self.popup_menu = AttachmentSidebarPopupMenu(self)

        self.drop_in = Component(self, label="drop_in")
        self.drop_in.pack(side="top", expand=False)

        self.drag_and_drop_label = ttk.Label(self.drop_in, text="Drag and drop files here")
        self.drag_and_drop_label.pack(padx=10, pady=30, anchor="center")

        self.attach_list = Component(self, label="Attachments", show_label=True)
        self.attach_list.pack(padx=4, pady=4, side="bottom", expand=True)
        
        self.tree = ttk.Treeview(self.attach_list, show="tree")
        self.tree.pack(fill="both", expand=True, padx=1, pady=1)

        # events
        self.tree.bind("<Button-3>", self._on_right_click)

        eb.bus.subscribe("email_editor.attachments#selected", self._on_attach_button_click)
        eb.bus.subscribe("attachment_sidebar.popup_menu.open_option#click", self._on_popup_menu_open_click)
        eb.bus.subscribe("attachment_sidebar.popup_menu.remove_option#click", self._on_popup_menu_remove_click)
        eb.bus.subscribe(email_preview_toolbar.EventNames.EDIT, self._on_email_preview_edit_click)

        eb.bus.subscribe(email_editor.EventNames.SAVE_BUTTON_CLICK, self._on_save_button_click)
        eb.bus.subscribe(email_editor.EventNames.SEND_BUTTON_CLICK, self._on_send_button_click)
        
        # self.drop_in.drop_target_register(DND_FILES)
        # self.drop_in.dnd_bind("<<Drop>>", self._on_file_drop)


    def _on_file_drop(self, e: DnDEvent):
        assert hasattr(e, "data")

        file_paths = [fp for fp in e.data.split(" ")]
        log.info("Drag and dropped file:", file_paths)

        for fp in file_paths:
            if isfile(fp):
                self.add_attachment(fp)
            else:
                raise ValueError("Can add only file attachments for now. (not directories)")


    def _on_save_button_click(self, _: eb.Event):
        ewa = EmailWithAttachmentsStore()
        ewa.set_attachments(AttachmentsState(self.get_attachments()))
        self.clear_attachment_list()
        return False

    def _on_send_button_click(self, _: eb.Event):
        ewa = EmailWithAttachmentsStore()
        ewa.set_attachments(AttachmentsState(self.get_attachments()))
        self.clear_attachment_list()
        return False 


    def _on_email_preview_edit_click(self, e: eb.Event):
        log.info("-------------------------------------------")

        # remove the items in the tree
        # show attachs of the current draft email in the tree
        
        email = e.data["email"]
        assert isinstance(email, EmailModel) and email.status == EmailStatus.DRAFT

        db = Database()
        attchs = db.fetch_attachments_by_email_id(email.email_id)

        log.info(f"Attachments of email {email}:")
        log.info(attchs)

        self.tree.delete(*self.tree.get_children())
        for a in attchs:
            self.tree.insert("", "end", text=a.filepath)
        
        log.info("-------------------------------------------")
        return False

    def _on_popup_menu_open_click(self, e: eb.Event):
        selected_ids = self.tree.selection()
        for id in selected_ids:
            filepath = self.tree.item(id, "text")
            log.info("Open attachment:", filepath)

        return True

    def _on_popup_menu_remove_click(self, e: eb.Event):
        selected_ids = self.tree.selection()
        self.tree.delete(*selected_ids)
        return True

    def _on_right_click(self, e: tk.Event):
        identifier = self.tree.identify_row(e.y)
        if identifier:
            self.tree.selection_add(identifier)
            self.popup_menu.tk_popup(e.x_root + 10, e.y_root + 10)

    def _on_attach_button_click(self, e: eb.Event):
        attachments = e.data["attachments"]
        img = ImageManager()
        for attachment in attachments: 
            self.tree.insert("", "end", text=attachment, image=img.get("icon_attachment"))
        return True


    def get_attachments(self):
        return [self.tree.item(item_id, "text") for item_id in self.tree.get_children()]

    def clear_attachment_list(self):
        attchs: list[str] = []
        for item_id in self.tree.get_children():
            attchs.append(self.tree.item(item_id, "text"))
            self.tree.delete(item_id)
        return attchs
    
    def add_attachment(self, attachment: str):
        img = ImageManager()
        self.tree.insert("", "end", text=attachment, image=img.get("icon_attachment"))

    def add_attachments(self, attachments: list[str]):
        for a in attachments:
            self.tree.insert("", "end", text=a)

        


