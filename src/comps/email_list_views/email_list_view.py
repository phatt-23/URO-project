from abc import abstractmethod
from tkinter import Misc

from lib import event_bus as eb
from comps.component import Component
from comps.email_card_list import EmailCardList
from debug import DEFAULT_LOGGED_IN_EMAIL
from models import EmailModel, UserModel
import database
from lib.logger import log
from comps.email_card_list_navbar import EmailCardListNavbar


class EmailListView(Component):
    email_card_list: EmailCardList

    def __init__(self, parent: Misc, label: str):
        super().__init__(parent, label=label, show_label=False, show_border=False)

        self.email_card_list = EmailCardList(self)
        self.email_card_list_navbar = EmailCardListNavbar(self)

        eb.bus.subscribe(database.EventNames.EMAIL_UPDATE, self._on_db_email_update)

    def update_email_count(self):
        self.email_card_list_navbar.set_email_count(len(self.email_card_list.cards))

    def _on_db_email_update(self, e: eb.Event):
        log.warning("EMAIL LIST VIEW updating email")

        email = e.data["email"]
        assert isinstance(email, EmailModel)

        db = database.Database()
        sender = db.fetch_user_by_id(email.sender_id)
        assert sender

        if self.email_card_list.contains_card(email.email_id):
            log.warning("REMOVING AND ADDING")
            self.email_card_list.clear_all()
            self.populate_list()

        return False

    def render(self):
        self.email_card_list.render()
        self.email_card_list.pack(padx=0, pady=0)
        self.email_card_list_navbar.pack(padx=1, pady=1, expand=False)

    def add_email(self, sender: UserModel, email: EmailModel, index=-1):
        self.email_card_list.add_card(sender, email, index)
        self.update_email_count()

    def clear_list(self):
        self.email_card_list.clear_all()
        self.update_email_count()

    @abstractmethod
    def populate_list(self):
        pass

