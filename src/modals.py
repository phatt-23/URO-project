from tkinter import Misc, Widget, Toplevel, Tk, Wm, ttk, font
import tkinter as tk
from typing import Dict
from lib.utils import get_hierarchy_string
from preferences import FontBuilder


MODAL_DEBUG_STYLE = False


class CustomModal(Toplevel):
    title_frame: ttk.LabelFrame | ttk.Frame
    message_frame: ttk.LabelFrame | ttk.Frame
    action_frame: ttk.LabelFrame | ttk.Frame 

    def __init__(self, parent: Tk | Toplevel, title: str):
        super().__init__(parent, padx=10, pady=10)
        self.transient(parent)
        self.wait_visibility()
        self.grab_set()  
        self.focus()
        self.resizable(False, False)
        self.title(title)

        title_font = FontBuilder().size("huge").weight("bold").buildTk()
        
        if MODAL_DEBUG_STYLE:
            self.title_frame = ttk.LabelFrame(self)
            self.title_frame.configure(labelwidget=ttk.Label(self.title_frame, text="title_frame"))

            self.message_frame = ttk.LabelFrame(self)
            self.message_frame.configure(labelwidget=ttk.Label(self.message_frame, text="message_frame"))

            self.action_frame = ttk.LabelFrame(self)
            self.action_frame.configure(labelwidget=ttk.Label(self.action_frame, text="action_frame"))
        else:
            self.title_frame = ttk.Frame(self)
            self.message_frame = ttk.Frame(self)
            self.action_frame = ttk.Frame(self)

        ttk.Label(self.title_frame, text=title, font=title_font).pack(fill="both", expand=True, anchor="center", padx=10, pady=10)


        self.bind("<Escape>", lambda _: self.close())
        self.update_idletasks()
        self.minsize(self.winfo_reqwidth(), self.winfo_reqheight())


    def close(self):
        self.grab_release()
        self.destroy()

    def finalize(self):
        self.grid_rowconfigure((2), weight=1, uniform="a")
        self.grid_columnconfigure(0, weight=1, uniform="a")

        self.title_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 4))
        ttk.Separator(self).grid(row=1, column=0, sticky="nsew", pady=4)
        self.message_frame.grid(row=2, column=0, sticky="nsew", pady=4)
        ttk.Separator(self).grid(row=3, column=0, sticky="nsew", pady=4)
        self.action_frame.grid(row=4, column=0, sticky="nsew", pady=(4, 0))

        self.update_idletasks()
        self.minsize(self.winfo_reqwidth(), self.winfo_reqheight())


class ModalShowWidgetInfo(CustomModal):
    def __init__(self, parent: Tk | Toplevel, w: Widget):
        super().__init__(parent, "Widget Information")

        font_bold = FontBuilder().mono().buildTk()
        font_normal = FontBuilder().mono().weight("bold").buildTk()

        labels = [
            ("Name:", w.winfo_name()),
            ("Class:", w.winfo_class()),
            ("Manager:", f"{bool(w.winfo_ismapped())} => '{w.winfo_manager()}'")
        ]

        for row, (label, value) in enumerate(labels):
            ttk.Label(self.message_frame, text=label, font=font_bold).grid(row=row, column=0, sticky="w", padx=10, pady=2)
            ttk.Label(self.message_frame, text=value, font=font_normal).grid(row=row, column=1, sticky="w", padx=10, pady=2)

        manager = w.winfo_manager()
        match manager:
            case "pack":
                settings = w.pack_info()
            case "grid":
                settings = w.grid_info()
            case "":
                settings = {"Error": "Widget is not managed by pack or grid."}
            case _:
                settings = {"Error": "Unknown geometry manager."}

        ttk.Separator(self.message_frame, orient="horizontal").grid(row=len(labels), column=0, columnspan=2, sticky="ew", padx=10, pady=2)

        settings_frame = tk.Frame(self.message_frame)
        settings_frame.grid(row=len(labels)+2, column=0, columnspan=2, sticky="ew", padx=10, pady=2)
        ttk.Label(settings_frame, text="Settings:", font=font_bold).pack(fill="x")

        def settings_labels(parent_frame: tk.Frame, settings_dict: Dict):
            local_frame = tk.Frame(parent_frame, padx=10, pady=10)
            local_frame.pack()
            for index, (key, value) in enumerate(settings_dict.items()):
                if isinstance(value, Dict):
                    settings_labels(local_frame, value)
                else:
                    key_label = ttk.Label(local_frame, text=key, font=font_bold)
                    key_label.grid(row=index, column=0, sticky="w", padx=10, pady=2)

                    value_label = ttk.Label(local_frame, text=str(value), font=font_normal)
                    value_label.grid(row=index, column=1, sticky="w", padx=10, pady=2)

        settings_labels(settings_frame, settings)

        ttk.Separator(self.message_frame, orient="horizontal").grid(row=len(labels)+3, column=0, columnspan=2, sticky="ew", padx=10, pady=2)

        geometry_frame = ttk.Frame(self.message_frame)
        geometry_frame.grid(row=len(labels)+4, column=0, columnspan=2, sticky="nsew", padx=10, pady=2)
        ttk.Label(geometry_frame, text="Geometry:", font=font_bold).pack(fill="x")

        geometry_label_frame = ttk.Frame(geometry_frame)
        geometry_label_frame.pack(fill="both", expand=True, padx=10, pady=10)

        labels = [("width", w.winfo_width()), ("height", w.winfo_height()), ("x", w.winfo_x()), ("y", w.winfo_y())]
        for index, label in enumerate(labels):
            ttk.Label(geometry_label_frame, text=label[0], font=font_bold).grid(row=index, column=0, sticky="w", padx=10, pady=2)
            ttk.Label(geometry_label_frame, text=label[1], font=font_normal).grid(row=index, column=1, sticky="w", padx=10, pady=2)


        ttk.Button(self.action_frame, text="OK", command=self.close).pack(padx=10, pady=10, fill="x", expand=True)

        self.finalize()


class ModalShowHierarchy(CustomModal):
    def __init__(self, parent: Tk | Toplevel):
        super().__init__(parent, "Hierarchy")
        self.resizable(True, True)

        font_mono = FontBuilder().mono().size("normal").weight("normal").build()

        # canvas
        canvas = tk.Canvas(self.message_frame)

        # bind scrollbar to canvas
        canvas_horizontal_scroll = ttk.Scrollbar(self.message_frame, orient="horizontal", command=canvas.xview)
        canvas_vertical_scroll = ttk.Scrollbar(self.message_frame, orient="vertical", command=canvas.yview)
        canvas.configure(xscrollcommand=canvas_horizontal_scroll.set)
        canvas.configure(yscrollcommand=canvas_vertical_scroll.set)
        canvas_horizontal_scroll.pack(side="bottom", fill="x", padx=8, pady=(0, 1))
        canvas_vertical_scroll.pack(side="right", fill="y", padx=1, pady=1)

        # new frame inside canvas (same as the an image)
        scrollable_frame = ttk.Frame(canvas)
        scrollable_frame.pack(fill="both", expand=True)
        canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

        # content of the new frame
        scrollable_frame_content = ttk.Label(scrollable_frame, text=get_hierarchy_string(parent), font=font_mono)
        scrollable_frame_content.pack(fill="both", expand=True, anchor="center", padx=10, pady=10)

        # canvas resizes when scrollable frame does
        def resize_canvas_window(e):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.itemconfig(canvas_window, width=e.width)
            scrollable_frame.update_idletasks()

        scrollable_frame.bind("<Configure>", lambda e: resize_canvas_window(e))
        canvas.pack(side="left", fill="both", expand=True, padx=1, pady=1)

        ttk.Button(self.action_frame, text="OK", command=self.close).pack(padx=10, pady=10, fill="x", expand=True)

        self.finalize()



class ModalSendNonValidEmail(CustomModal):
    def __init__(self, parent: Tk | Toplevel, errors: list[str]):
        super().__init__(parent, "Email failed to send!")
    
        for e in errors:
            ttk.Label(self.message_frame, text="> " + e.capitalize(), anchor="w").pack(padx=20, pady=2, fill="x")

        ttk.Button(self.action_frame, text="I understand", command=self.close).pack(padx=10, pady=10)
        self.finalize()


    
