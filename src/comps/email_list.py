import tkinter as tk
from tkinter import ttk, Misc, Canvas
from comps.component import Component
from database import Database
from models import EmailModel, UserModel
from comps.email_card_list import EmailCardList
from lib import event_bus as eb
from comps.email_list_views.email_list_view import EmailListView
from comps.email_list_views.inbox_list_view import InboxListView
from comps.email_list_views.sent_mail_list_view import SentMailListView
from comps.email_list_views.drafts_list_view import DraftsListView
from comps.email_list_views.all_mail_list_view import AllMailListView 
from comps.email_list_views.spam_list_view import SpamListView 
from comps.email_list_views.bin_list_view import BinListView 
from comps.search_bar import SearchBar
from comps.filter_frame import FilterFrame
from comps.sort_frame import SortFrame
from comps import search_bar


class EmailList(Component):
    list_views: dict[str, EmailListView] 
    current_list_view: EmailListView 

    def __init__(self, parent: Misc):
        Component.__init__(self, parent, label=__name__)

        self.search_bar = SearchBar(self)
        self.filter_frame = FilterFrame(self)
        self.sort_frame = SortFrame(self)

        self.list_views = {
            "inbox": InboxListView(self),
            "drafts": DraftsListView(self),
            "sent_mail": SentMailListView(self),
            "all_mail": AllMailListView(self),
            "spam": SpamListView(self),
            "bin": BinListView(self),
        }

        # default to inbox
        self.current_list_view = self.list_views["inbox"]
        
        # events
        eb.bus.subscribe("category_list.item#click", self._on_view_item_click)
        # eb.bus.subscribe(search_bar.EventNames.FILTER, self._on_view_filter)
        # eb.bus.subscribe(search_bar.EventNames.SORT, self._on_sort_filter)

    def _on_view_filter(self, _):
        self.sort_frame.grid_remove()
        self.filter_frame.grid()
        return False


    def _on_sort_filter(self, _):
        self.filter_frame.grid_remove()
        self.sort_frame.grid()
        return False

    def _on_view_item_click(self, e: eb.Event):
        view_name = e.data["item_name"]
        self.current_list_view.grid_remove()
        self.current_list_view = self.list_views[view_name]
        self.current_list_view.grid(row=2, column=0, padx=0, pady=0, sticky="nsew")

        return True
        
    def render(self):
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.search_bar.grid(row=0, column=0, padx=1, pady=1, sticky="ew")

        self.filter_frame.grid(row=1, column=0, pady=1, sticky="ew")
        self.filter_frame.grid_remove()

        self.sort_frame.grid(row=1, column=0, pady=1, sticky="ew")
        self.sort_frame.grid_remove()

        self.current_list_view.grid(row=2, column=0, padx=0, pady=0, sticky="nsew")


