import Page as p
import tkinter as tk
import tkinter.ttk as ttk

import BfRamTableView

class BfRamWindow():
    def __init__(self, parent, main_view, dev, *args, **kwargs):
        self.main_view = main_view
        self.dev = dev
        self.parent = parent

        self.bfRamTableViewPage = p.Page(parent)
        self.bfRamTableView = BfRamTableView.BfRamTableView(self.bfRamTableViewPage, main_view, dev)

        self.bfRamTableViewPage.pack(expand=True, fill='both')
