import evk.gui.Page as p
import tkinter as tk
import tkinter.ttk as ttk

import evk.gui.BfRamTableView

class BfRamWindow():
    def __init__(self, parent, gui_handler, dev, *args, **kwargs):
        self.gui_handler = gui_handler
        self.host = gui_handler.host
        self.dev = dev
        self.parent = parent

        self.bfRamTableViewPage = p.Page(parent)
        self.bfRamTableView = evk.gui.BfRamTableView.BfRamTableView(self.bfRamTableViewPage, gui_handler, dev)

        self.bfRamTableViewPage.pack(expand=True, fill='both')
