import evk.gui.Page as p
import tkinter as tk
import tkinter.ttk as ttk

import evk.gui.TxRxRamTableView

class TxRamWindow():
    def __init__(self, parent, gui_handler, dev, *args, **kwargs):
        self.gui_handler = gui_handler
        self.host = gui_handler.host
        self.dev = dev
        self.parent = parent

        self.txRamTableViewPage = p.Page(parent)
        self.txRamTableView = evk.gui.TxRxRamTableView.TxRxRamTableView(self.txRamTableViewPage, gui_handler, dev, 'TX_RAM')

        self.txRamTableViewPage.pack(expand=True, fill='both')
