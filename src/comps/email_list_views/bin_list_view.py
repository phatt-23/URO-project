from tkinter import Misc
from comps.email_list_views.email_list_view import EmailListView
import database as db
from lib import event_bus as eb


class BinListView(EmailListView):
    def __init__(self, parent: Misc):
        super().__init__(parent, label=__name__)

        eb.bus.subscribe(db.EventNames.EMAIL_WITH_RECIPIENTS_AND_ATTACHMENTS_INSERT, self._on_email_recipient_and_attachments)

        self.populate_list()
    
    def _on_email_recipient_and_attachments(self, e: eb.Event):
        return False

    def populate_list(self):
        pass
