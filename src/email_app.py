#!/usr/bin/env python3

from dataclasses import dataclass
from typing import Dict, Iterable, Tuple
from tkinter import messagebox, ttk
import lib.event_bus as eb
import tkinter as tk
from pathlib import Path
from preferences import FontBuilder, ThemeConfig
from models import EmailStatus
from comps import email_editor
from vendor import sv_ttk

from modals import ModalSendNonValidEmail, ModalShowHierarchy, ModalShowWidgetInfo
from lib.utils import get_hierarchy_string
from lib.application import Application
from lib.image_manager import ImageManager
from lib.logger import log
from database import Database
from comps.layout_sidebar import LayoutSidebar
from comps.layout_view import LayoutView
from comps.menubar import MenuBar
from comps.statusbar import StatusBar
from stores import email_with_attachments_store


class EmailClientApp(Application):
    def __init__(self):
        super().__init__()

        ThemeConfig(self.tk_instance)
        Database().__init__()
        ImageManager().__init__()
        self.load_assets()

        self.tk_instance.geometry("1200x600")

        self.menubar = MenuBar(self.tk_instance)
        self.layout_sidebar = LayoutSidebar(self.main_frame)
        self.layout_view = LayoutView(self.main_frame)
        self.statusbar = StatusBar(self.tk_instance)

        eb.bus.subscribe_pattern("[a-zA-Z0-9._#]*", self.on_event)

    def on_event(self, e: eb.Event) -> bool:
        log.info(f"Event: {e}")

        match e.name:
            case "menu_bar.file_menu.quit_button#click":
                if messagebox.askyesno(title="Quit program", message="Do you really want to quit?"):
                    self.tk_instance.destroy()

            case "menu_bar.debug_menu.show_hierarchy_button#click":
                ModalShowHierarchy(self.tk_instance)

            case "menu_bar.debug_menu.print_hierarchy_button#click":
                log.info("\n" + get_hierarchy_string(self.tk_instance))

            case "menu_bar.debug_menu.print_comp_detail_button#click":
                self.start_capture()

            case "app_widget_capture#caught":
                w = e.data.get("captured_widget")
                assert isinstance(w, tk.Widget), "Failed to captured a widget!"
                ModalShowWidgetInfo(self.tk_instance, w)

            case email_with_attachments_store.EventNames.EMAIL_AND_ATTACHMENTS_READY:

                store_content = email_with_attachments_store.EmailWithAttachmentsStore().get_content()

                action = store_content["action"]
                is_editing_email = store_content["is_editing_email"]
                editing_email_id = store_content["editing_email_id"]
                email = store_content["email"]
                attachments = store_content["attachments"]
                validation = store_content["validation"]
                
                assert isinstance(email, email_with_attachments_store.EmailState)
                assert isinstance(attachments, email_with_attachments_store.AttachmentsState)
                assert isinstance(validation, email_with_attachments_store.ValidationState)
                assert isinstance(action, email_with_attachments_store.ActionEnum)

                db = Database()

                assert email.sender_email, "Should always be set."

                # when sending email, validation must be checked
                if action == email_with_attachments_store.ActionEnum.SEND:
                    if not validation.is_valid:
                        ModalSendNonValidEmail(self.tk_instance, validation.error_messages)
                        return True 

                    # if the email is valid then these are non-emptry
                    assert email.recipients and email.subject and email.body


                    # if the sent email is email that been sitting in the draft
                    if is_editing_email:
                        # update the draft to be sent_draft
                        # draft that has been sent
                        # now it shouldnt be visible in drafts view
                        db.update_email_by_id(
                            editing_email_id,
                            email.subject or "", 
                            email.body or "", 
                            status=EmailStatus.SENT_DRAFT
                        )

                        db.delete_recipients_of_email(editing_email_id)
                        db.delete_attachments_of_email(editing_email_id)

                        db.insert_email_with_recipients_and_attachments(
                            email.sender_email, 
                            email.subject, 
                            email.body, 
                            email.recipients, 
                            attachments.attachments
                        )
                    # if the email is not a draft
                    else:
                        db.insert_email_with_recipients_and_attachments(
                            email.sender_email, 
                            email.subject,
                            email.body,
                            email.recipients, 
                            attachments.attachments,
                            status=EmailStatus.SENT
                        )
                elif action == email_with_attachments_store.ActionEnum.SAVE:
                    # if this email is already a draft itself
                    # update it instead of creating a new one
                    if is_editing_email:
                        db.update_email_by_id(
                            editing_email_id,
                            email.subject or "", 
                            email.body or "", 
                            status=EmailStatus.DRAFT,
                        )

                        db.delete_recipients_of_email(editing_email_id)

                        for rec_email in email.recipients:
                            rec = db.fetch_user_by_email(rec_email)
                            if not rec:
                                rec = db.insert_user(rec_email)
                            db.insert_email_recipient(editing_email_id, rec.user_id)

                        db.delete_attachments_of_email(editing_email_id)

                        for attch_path in attachments.attachments:
                            with open(attch_path, "r") as f:
                                blob = f.read()
                                attch = db.insert_attachment(attch_path, attch_path, blob)
                                db.insert_email_attachment(editing_email_id, attch.attachment_id)

                    # if its a new email we want to save, then create a new email
                    else:
                        db.insert_email_with_recipients_and_attachments(
                            email.sender_email, 
                            email.subject or "", 
                            email.body or "", 
                            email.recipients, 
                            attachments.attachments,
                            status=EmailStatus.DRAFT
                        )

                # clear store so no duplication and weird stuff happens
                email_with_attachments_store.EmailWithAttachmentsStore().clear_store()
                return True

        return False

                
    def render(self):
        self.layout_sidebar.pack(side="left", expand=False)
        self.layout_view.pack(side="right")

    def load_assets(self):
        @dataclass
        class ImageWithSize:
            filepath: str
            size: Tuple[int, int]

        images: Dict[str, ImageWithSize] = {}
        
        # Icons
        image_icon_size = (16, 16)
        image_icons_directory = Path("assets/icons")
        for path in image_icons_directory.glob("[a-zA-Z0-9_]*.png"):
            if not path.is_file():
                continue

            filepath = str(path)
            extension = ".png"
            undesired = "_24dp_E3E3E3"
            undesired_sub_pos = filepath.find(undesired)
            extension_pos = filepath.find(extension)

            if undesired_sub_pos >= 0:
                key = filepath[:undesired_sub_pos]
            else:
                key = filepath[:extension_pos]

            key = "icon_" + key[key.rfind("/")+1:]

            images[key] = ImageWithSize(filepath, image_icon_size)
        
        # Load into the cetral manager
        for key, image in images.items():
            ImageManager().load(str(image.filepath), key, image.size)

