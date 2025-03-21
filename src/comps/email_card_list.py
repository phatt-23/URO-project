from enum import StrEnum
import tkinter as tk
from tkinter import Misc, ttk
from typing import Literal
from comps.component import Component
from database import Database
from models import UserModel, EmailModel
from lib import event_bus as eb
from comps.email_card import EmailCard


CANVAS_BORDER_SIZE = 0


class EmailCardList(Component):
    cards: dict[int, EmailCard]  # key: email.email_id 

    def __init__(self, parent: Misc):
        Component.__init__(self, parent, label=__name__, show_label=False, show_border=False)

        # member variables
        self.cards = {}

        # create a frame to hold the cards
        self.list_frame = Component(self, label="list_frame", show_border=True, show_label=False)

        # canvas that holds the frame with cards
        self.list_canvas = tk.Canvas(
            self.list_frame, 
            scrollregion=(0, 0, self.list_frame.winfo_width(), self.list_frame.winfo_height()),
            highlightthickness=0,
            width=10
        )

        # display frame inside canvas holding the cards (need not to be packed)
        self.cards_frame = Component(self.list_canvas, label="cards_frame", show_border=False)
        self.cards_frame_window_id = self.list_canvas.create_window((0,0), window=self.cards_frame, anchor="nw")
    
        # scrollbar
        self.canvas_scrollbar = ttk.Scrollbar(self.list_frame, orient="vertical", command=self.list_canvas.yview)
        self.list_canvas.configure(yscrollcommand=self.canvas_scrollbar.set)
        
        # events
        self.list_canvas.bind("<Configure>", lambda _: self._resize_frame())
        self.list_canvas.bind("<Enter>", lambda _: self._enable_scrolling())
        self.list_canvas.bind("<Leave>", lambda _: self._disable_scrolling())

    def render(self):
        self.list_frame.pack(fill="both", expand=True, padx=1, pady=1)
        self.list_frame.grid_columnconfigure(0, weight=0)
        self.list_frame.grid_rowconfigure(0, weight=1)
        self.list_canvas.pack(side="left", fill="both", expand=True, padx=(2,4), pady=0)

    def add_card(self, sender: UserModel, email: EmailModel, index: int):
        """Add an email card to the list. Optional index (including negative)"""
        if email.email_id in self.cards:
            # raise ValueError("Email already in the email card list!")
            return

        new_card = EmailCard(self.cards_frame, sender, email)

        card_list = [ (key, value) for key, value in self.cards.items() ]
        card_list.insert(index, (email.email_id, new_card))
        
        self.cards = { key:value for key, value in card_list } 

        self._rerender()
        self._resize_frame()

    def remove_card(self, email_id: int):
        if email_id not in self.cards:
            return

        self.cards.pop(email_id)
        self._rerender()
        self._resize_frame()

    def contains_card(self, email_id: int):
        return email_id in self.cards
    
    def _rerender(self):
        for _, card in self.cards.items():
            card.pack_forget()
            card.pack(fill="x", padx=2, pady=2, side="top", expand=False)


    def clear_all(self):
        for _, c in self.cards.items():
            c.pack_forget()
        self.cards = {}
        self._resize_frame()


    def _enable_scrolling(self):
        """Enable scrolling when the mouse enters the component"""
        self.list_canvas.bind_all("<MouseWheel>", lambda e: self._on_mousewheel(e, -1))  # Window and macOS
        self.list_canvas.bind_all("<Button-4>", lambda e: self._on_mousewheel(e, -1))    # Linux (scoll-up)
        self.list_canvas.bind_all("<Button-5>", lambda e: self._on_mousewheel(e, 1))  # Linux (scrol-down)


    def _disable_scrolling(self):
        """Disable scrolling when the mouse leaves the component"""
        self.list_canvas.bind_all("<MouseWheel>", lambda e: self._on_mousewheel(e, -1))  # Window and macOS
        self.list_canvas.unbind_all("<MouseWheel>")
        self.list_canvas.unbind_all("<Button-4>")
        self.list_canvas.unbind_all("<Button-5>")


    def _update_scrollbar_visibility(self, enable: bool):
        if enable:
            self.canvas_scrollbar.pack(side="right", fill="y", padx=(0, 0), pady=0)
        else:
            self.canvas_scrollbar.pack_forget()


    def _resize_frame(self):
        """Adjust canvas size and scroll region"""
        list_height = self.cards_frame.winfo_reqheight()
        canvas_height = self.list_canvas.winfo_height()
        height = max(list_height, canvas_height)

        self._update_scrollbar_visibility(list_height >= canvas_height)

        # update the size of the window holding the cards frame in canvas
        self.list_canvas.itemconfig(
            self.cards_frame_window_id, 
            width=self.list_canvas.winfo_width(),
            height=height, 
        )
        
        # update the canvas scroll region
        self.list_canvas.configure(scrollregion=self.list_canvas.bbox("all"))

    def _on_mousewheel(self, _: tk.Event, amount: int): 
        """Handle mouse wheel scrolling on the the canvas"""
        self.list_canvas.yview_scroll(amount, "units")
    
