from typing import Optional
from comps.component import Component
from tkinter import Misc
from lib import event_bus as eb
from models import EmailModel, UserModel
from comps.email_preview_content import EmailPreviewContent
from comps.email_preview_toolbar import EmailPreviewToolbar


class EmailPreview(Component):

    def __init__(self, parent: Misc):
        Component.__init__(self, parent, label=__name__)

        self.email_preview_toolbar = EmailPreviewToolbar(self)
        self.email_preview_content = EmailPreviewContent(self)

    def render(self):
        self.email_preview_toolbar.pack(side="top", expand=False, padx=1, pady=1)
        self.email_preview_content.pack(side="bottom", expand=True, padx=1, pady=1)

         
