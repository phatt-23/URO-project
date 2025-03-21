from comps.component import Component
from tkinter import Misc, ttk, StringVar, IntVar


class EmailCardListNavbar(Component):
    def __init__(self, parent: Misc):
        super().__init__(parent, label=__name__, show_label=False, show_border=True)

        self.total_email_count_var = IntVar(value=0)
        self.total_email_count_string_var = StringVar(value="")
        
        self.total_email_count_var.trace_add(
            "write", 
            lambda a, b, c: self.total_email_count_string_var.set(f"Email count of {self.total_email_count_var.get()}")
        )

        self.total_email_count_label = ttk.Label(self, textvariable=self.total_email_count_string_var)

    def render(self):
        self.total_email_count_label.pack()

    def set_email_count(self, count: int):
        self.total_email_count_var.set(count)

        
        
