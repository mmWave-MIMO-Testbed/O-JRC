import Page as p
import tkinter as tk
import tkinter.ttk as ttk

import TxRxRamTableView

class TxRamWindow():
    def __init__(self, parent, main_view, dev, *args, **kwargs):
        self.main_view = main_view
        self.dev = dev
        self.parent = parent

        self.txRamTableViewPage = p.Page(parent)
        self.txRamTableView = TxRxRamTableView.TxRxRamTableView(self.txRamTableViewPage, main_view, dev, 'TX_RAM')

        self.txRamTableViewPage.pack(expand=True, fill='both')
