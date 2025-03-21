# Email Client (URO Project)

## Dependencies

### Python Packages

Tkinter
PIL (Python Image Library)
PIL-Tkinter (PIL Tkinter interface)
json
sqlite3
tkinterdnd2 (Tkinter Drag and Drop)

Install on Linux with `dnf` package manager:
```sh
pip install pillow                  # PIL
sudo dnf install python3-tkinter    # tk interface
sudo dnf install python3-pillow-tk  # PIL-tk interface
pip install tkinterdnd2
```

### Vendor Packages

The theme used is: [https://github.com/rdbende/Sun-Valley-ttk-theme/tree/main]

## Naming In Source Code

I've chosen to call _mail_ as _message_ It should be considered interchangable.
**TODO:** Rename to **email**

## Hierarchy

Described in Python, it should look like this.

```python
class Application:
    def __init__(self, window: tk.Tk):
        self.window = window

        self.main_frame = tk.Frame(self.window)
        
        # sidebar
        layout_menu_bar = LayoutMenuBarC(main_frame)
        # main view port
        layout_view = LayoutViewC(main_frame)

        # swich between views by the layout menu bar
        # mail view for listing through mail
        MailViewC(layout_view)
        # compose view for writing mail
        ComposeViewC(layout_view)
        
        # mail view has folders, list and preview
        # category/folder list to organize mail
        CategoryListC(mail_view)
        # mail list to scroll and view titles and the 'from' address
        MessageListC(mail_view)
        # mail preview
        MessagePreviewC(mail_view)
        
        # compose view has the message editor and sidebar for attachments
        MessageEditor(compose_view)
        AttachmentSidebarC(compose_view)
```

# Event Naming

Components chain with optional ID if there is more of the each of them.
Then at the end, after `#`, there is the action that occured which itself 
can be in some category (optional).
Everything is **lowercase**.

`component-id.subcomponent-id. ... .subcomponent#category. ... .subcategory.action`

Examples:
- `layout_view.compose_view.message_editor.send_button#click`
- `layout_view.mail_view.category_list.folder_item-0#click`
- `layout_view.mail_view.category_list.folder_item-0#hover`
- `layout_menu.compose_button#click`


## Described As a Language:

```text
number = \d+
identifier = [a-z]+[a-z0-9_]+

component = identifier(-number)? ++ (. ++ component)?

category = identifier ++ (. ++ category)?
type = identifier
action = category ++ . ++ type

event = component ++ # ++ action
```

## Event Can Be Searched With Regex.

Regex that matches should match all the events: `([a-zA-Z]+[a-zA-Z_]*(-\d+)?)+#\w+(.\w+)?`






