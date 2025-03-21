from tkinter import Misc

from lib import event_bus as eb
from comps.component import Component
from comps.email_card_list import EmailCardList
from database import Database
from debug import DEFAULT_LOGGED_IN_EMAIL
from models import EmailModel, EmailStatus
from comps.email_list_views.email_list_view import EmailListView
import database
from lib.logger import log


class SentMailListView(EmailListView):

    def __init__(self, parent: Misc):
        super().__init__(parent, label=__name__)

        eb.bus.subscribe(database.EventNames.EMAIL_INSERT, self._on_db_email_change)
        eb.bus.subscribe(database.EventNames.EMAIL_DELETE, self._on_db_email_change)
        eb.bus.subscribe(database.EventNames.EMAIL_WITH_RECIPIENTS_AND_ATTACHMENTS_INSERT, self._on_db_email_change)

        self._populate_list()

    def _on_db_email_change(self, e: eb.Event):
        email = e.data["email"]
        assert isinstance(email, EmailModel)

        if not email.status == EmailStatus.SENT:
            log.warning(f"NOT ADDING EMAIL TO SENT MAIL. Status: {email.status}")
            return False

        sender = Database().fetch_user_by_id(email.sender_id)
        if not sender:
            return False

        # self.add_email(sender, email, index=0)
        self.clear_list()
        self._populate_list()
        return False

    def _populate_list(self):
        db = Database()
        user = db.fetch_user_by_email(DEFAULT_LOGGED_IN_EMAIL)

        if not user:
            raise ValueError(f"ERROR: User with email '{DEFAULT_LOGGED_IN_EMAIL}' isnt in the database!")

        for email in db.fetch_emails_from_user(user.user_id):
            if email.status == EmailStatus.SENT:
                self.add_email(user, email)


