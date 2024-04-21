import evk.gui.Page as p
import tkinter as tk
import tkinter.ttk as ttk

import evk.gui.TxRxRamTableView

class RxRamWindow():
    def __init__(self, parent, gui_handler, dev, *args, **kwargs):
        self.gui_handler = gui_handler
        self.host = gui_handler.host
        self.dev = dev
        self.parent = parent

        self.rxRamTableViewPage = p.Page(parent)
        self.rxRamTableView = evk.gui.TxRxRamTableView.TxRxRamTableView(self.rxRamTableViewPage, gui_handler, dev, 'RX_RAM')

        self.rxRamTableViewPage.pack(expand=True, fill='both')
