from tkinter import Tk, Toplevel, Widget
from typing import Any, Dict


def get_hierarchy_string(w: Tk | Widget | Toplevel, depth=0) -> str:
    if w.winfo_manager() == "labelframe":
        return ""

    indent = "  " * depth

    if w.winfo_name().startswith("!"):
        name = w.winfo_name()[1:]
    else:
        name = w.winfo_name()

    result = indent + "<%s:%s:%s:%s>" % (name, w.winfo_class(), w.winfo_manager(), w.winfo_ismapped()) + "\n"

    for child in w.winfo_children():
        result += get_hierarchy_string(child, depth + 1)

    result += indent + "</%s>" % (name, ) + "\n"

    return result


def pretty_string_dict(d: Dict[Any, Any], indent=0) -> str:
    result = ""
    for key, value in d.items():
        result += "\t" * indent + str(key) + "\n"
        if isinstance(value, dict):
            result += pretty_string_dict(value, indent+1) + "\n"
        else:
            result += "\t" * (indent+1) + str(value) + "\n"
    return result
