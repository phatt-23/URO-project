from tkinter import ttk, Misc
from comps.component import Component
from database import Database
from lib import event_bus as eb
import database as db

class AddressBookView(Component):
    def __init__(self, parent: Misc):
        Component.__init__(self, parent, label=__name__)

        self.frame = Component(self, show_border=True, show_label=False)

        columns = ("email", "first_name", "last_name")
        self.treeview = ttk.Treeview(self.frame, columns=columns, show="headings", selectmode="browse")
        for column in columns:
            text = " ".join([c.capitalize() for c in column.replace("_", " ").split(" ")])
            self.treeview.heading(column=column, text=text)

        treeview_scroll = ttk.Scrollbar(self.frame, orient="vertical", command=self.treeview.yview)
        self.treeview.configure(yscrollcommand=treeview_scroll.set)

        treeview_scroll.pack(side="right", fill="y", padx=(0, 10), pady=10)
        self.treeview.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=10)

        self.frame.pack(fill="both", expand=True, padx=10)

        eb.bus.subscribe(db.EventNames.USER_INSERT, lambda _: self.repopulate())

        self.populate()

    def repopulate(self):
        print("REPOPULATE")
        self.clear()
        self.populate()
        self.update_idletasks()

        return False

    def clear(self):
        self.treeview.delete(*self.treeview.get_children())

    def populate(self):
        db = Database()

        users = db.fetch_all_users()
        for user in users:
            self.treeview.insert("", "end", values=(user.email, user.first_name, user.last_name))
