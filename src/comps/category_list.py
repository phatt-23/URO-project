from lib.image_manager import ImageManager
from lib import event_bus as eb
from comps.component import Component
from tkinter import Misc, ttk
import tkinter as tk


NOT_SELECTED = "notselected"
SELECTED = "selected"


class CategoryList(Component):
    selected_item_id: int = 0

    def __init__(self, parent: Misc):
        Component.__init__(self, parent, label=__name__)

        self.category_tree = ttk.Treeview(self, selectmode="browse", show="tree")

        tree_items = {
            "inbox"     : (("basic", SELECTED), "icon_inbox"),
            "drafts"    : (("basic", NOT_SELECTED), "icon_drafts"),
            "sent_mail" : (("basic", NOT_SELECTED), "icon_outbox"),
            "all_mail"  : (("basic", NOT_SELECTED), "icon_all_inbox"),
            "spam"      : (("basic", NOT_SELECTED), "icon_block"),
            "bin"       : (("basic", NOT_SELECTED), "icon_delete"),
            "important" : (("folder", NOT_SELECTED), "icon_folder"),
            "starred"   : (("folder", NOT_SELECTED), "icon_folder"),
        }

        self.category_tree.tag_configure(SELECTED, background="gray")
        self.category_tree.tag_configure(NOT_SELECTED)

        for name, (tags, icon) in tree_items.items():
            tags_with_name = (name, *tags)
            self.category_tree.insert("", tk.END, 
                text="  " + " ".join([n.capitalize() for n in name.split("_")]), tags=tags_with_name, 
                image=ImageManager().get(icon))

        self.category_tree.bind("<<TreeviewSelect>>", self.on_category_select)
       
    def on_category_select(self, e: tk.Event):
        """Update selection state and ensure persistent highlighting."""

        for item in self.category_tree.get_children():
            item_name, item_type, _ = self.category_tree.item(item, "tags")
            self.category_tree.item(item, tags=(item_name, item_type, NOT_SELECTED))

        selected_item = self.category_tree.selection()

        if selected_item:
            selected_item = selected_item[0]
            item_name, item_type, _ = self.category_tree.item(selected_item, "tags")
            self.category_tree.item(selected_item, tags=(item_name, item_type, SELECTED))

            self.category_tree.update_idletasks()

            eb.bus.publish("category_list.item#click", data={"item_name": item_name})

        return True

    def render(self):
        self.category_tree.pack(fill="both", expand=True, padx=1, pady=1)
    



