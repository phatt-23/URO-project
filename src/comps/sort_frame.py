from comps.component import Component
from tkinter import Misc


class SortFrame(Component):

    def __init__(self, parent: Misc):
        Component.__init__(self, parent, label=__name__)
