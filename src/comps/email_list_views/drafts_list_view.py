from tkinter import Misc
from comps.email_list_views.email_list_view import EmailListView
import database as db
from lib import event_bus as eb
from comps import email_editor
from models import EmailModel, EmailStatus
from debug import DEFAULT_LOGGED_IN_EMAIL
from stores import email_with_attachments_store
from lib.logger import log


class DraftsListView(EmailListView):
    def __init__(self, parent: Misc):
        super().__init__(parent, label=__name__)

        eb.bus.subscribe(
            db.EventNames.EMAIL_WITH_RECIPIENTS_AND_ATTACHMENTS_INSERT, 
            self._on_email_recipient_and_attachments_insert)

        eb.bus.subscribe(
            email_with_attachments_store.EventNames.EMAIL_AND_ATTACHMENTS_READY, 
            self._on_email_with_attchs_ready)

        self.populate_list()

  
    def _on_email_with_attchs_ready(self, e: eb.Event):
        if e.data["is_editing_email"]:
            log.warning(f"Update the email with id: {e.data["editing_email_id"]}")
            log.warning("with new content")
            
        return False
        


    def _on_email_recipient_and_attachments_insert(self, e: eb.Event):
        email = e.data["email"]
        assert isinstance(email, EmailModel)

        if email.status == EmailStatus.DRAFT:
            sender = db.db.fetch_user_by_id(email.sender_id)
            assert sender

            self.add_email(sender, email, index=0)

        return False


    def populate_list(self):
        user = db.db.fetch_user_by_email(DEFAULT_LOGGED_IN_EMAIL)
        assert user
        emails = db.db.fetch_emails_from_user(user.user_id)
        for e in emails:
            if e.status == EmailStatus.DRAFT:
                self.add_email(user, e, index=0)
            

