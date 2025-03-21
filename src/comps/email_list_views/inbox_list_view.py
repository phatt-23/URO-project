from logging import Logger
from tkinter import Misc

from lib import event_bus as eb
from comps.component import Component
from comps.email_card_list import EmailCardList
from database import Database
from debug import DEFAULT_LOGGED_IN_EMAIL
from models import EmailModel, EmailRecipientModel
from comps.email_list_views.email_list_view import EmailListView
from lib.logger import log
import database


class InboxListView(EmailListView):

    def __init__(self, parent: Misc):
        super().__init__(parent, label=__name__)

        eb.bus.subscribe(database.EventNames.EMAIL_WITH_RECIPIENTS_AND_ATTACHMENTS_INSERT, self._on_email_recipient_and_attachments)

        self._populate_list()


    def _on_email_recipient_and_attachments(self, e: eb.Event):
        email = e.data["email"]
        assert isinstance(email, EmailModel)
        
        db = Database()
        user = db.fetch_user_by_email(DEFAULT_LOGGED_IN_EMAIL)
        assert user, "Logged-in not in the database."

        recipients = db.fetch_recipients_by_email_id(email.email_id)
        if any(r.user_id == user.user_id for r in recipients):
            sender = db.fetch_user_by_id(email.sender_id)
            assert sender
            self.add_email(sender, email, index=0)

        return False


    def _populate_list(self):
        db = Database()
        user = db.fetch_user_by_email(DEFAULT_LOGGED_IN_EMAIL)

        if not user:
            raise ValueError(f"ERROR: User with email '{DEFAULT_LOGGED_IN_EMAIL}' isnt in the database!")

        for sender, email in db.fetch_emails_for_user(user.user_id):
            self.add_email(sender, email)


