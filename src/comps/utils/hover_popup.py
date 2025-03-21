import tkinter as tk 
from tkinter import StringVar


class HoverPopupText:
    text: str | StringVar 

    def __init__(self, parent, text: str | StringVar = "Additional details"):
        self.parent = parent
        self.text = text
        self.popup = None

        # bind hover events to the parent widget
        parent.bind("<Enter>", self.show_popup)
        parent.bind("<Leave>", self.hide_popup)

    def show_popup(self, event):
        """Creates and shows the popup window"""

        # prevent multiple popups
        if self.popup is not None:
            return  

        self.popup = tk.Toplevel(self.parent)
        # remove window decorations (border, title bar)
        self.popup.overrideredirect(True)  
        # position near the cursor
        self.popup.geometry(f"+{event.x_root + 10}+{event.y_root + 10}")  

        if isinstance(self.text, StringVar):
            label = tk.Label(self.popup, textvariable=self.text, bg="black", fg="white", padx=5, pady=3)
        else:
            label = tk.Label(self.popup, text=self.text, bg="black", fg="white", padx=5, pady=3)
        label.pack()

    def hide_popup(self, _):
        """Destroys the popup window when the cursor leaves"""
        if self.popup:
            self.popup.destroy()
            self.popup = None
