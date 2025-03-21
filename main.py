import tkinter as tk


class HoverPopup:
    def __init__(self, parent, text="Additional details"):
        self.parent = parent
        self.text = text
        self.popup = None

        # bind hover events to the parent widget
        parent.bind("<Enter>", self.show_popup)
        parent.bind("<Leave>", self.hide_popup)

    def show_popup(self, event):
        """Creates and shows the popup window."""
        if self.popup is not None:
            return  # prevent multiple popups

        self.popup = tk.Toplevel(self.parent)
        self.popup.overrideredirect(True)  # remove window decorations (border, title bar)
        self.popup.geometry(f"+{event.x_root + 10}+{event.y_root + 10}")  # Position near the cursor

        label = tk.Label(self.popup, text=self.text, bg="black", fg="white", padx=5, pady=3)
        label.pack()

    def hide_popup(self, _):
        """Destroys the popup window when the cursor leaves."""
        if self.popup:
            self.popup.destroy()
            self.popup = None


