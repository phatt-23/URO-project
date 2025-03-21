import tkinter as tk 
from tkinter import font
from tkinter import scrolledtext
import logging

class TextLogHandler(logging.Handler):
    """Custom logging handler that sends logs to a Tkinter Text widget"""
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget
        self.setFormatter(logging.Formatter("[%(asctime)s] [%(levelname)s] - %(message)s", "%H:%M:%S"))

    def emit(self, record):
        """Write log message to the text widget"""
        self.text_widget.config(state="normal")
        self.text_widget.insert("end", self.format(record) + "\n")
        self.text_widget.config(state="disabled")
        self.text_widget.yview("end")  # Auto-scroll


class LogViewer(tk.Toplevel):
    log_handler: TextLogHandler

    def __init__(self, parent, log_source):
        super().__init__(parent)
        self.title("Log Viewer")
        self.geometry("600x400")

        small_font = font.Font(size=8)

        self.log_display = scrolledtext.ScrolledText(self, wrap="word", state="disabled", font=small_font)
        self.log_display.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.log_handler = TextLogHandler(self.log_display)
        log_source.addHandler(self.log_handler)

        self.protocol("WM_DELETE_WINDOW", self.destroy)

    def destroy(self):
        """Remove log handler when closing the window"""
        logging.getLogger().removeHandler(self.log_handler)
        self.log_display.destroy()
        super().destroy()

