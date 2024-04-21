import Page as p
import tkinter as tk
import tkinter.ttk as ttk

import TxRxRamTableView

class RxRamWindow():
    def __init__(self, parent, main_view, dev, *args, **kwargs):
        self.main_view = main_view
        self.dev = dev
        self.parent = parent

        self.rxRamTableViewPage = p.Page(parent)
        self.rxRamTableView = TxRxRamTableView.TxRxRamTableView(self.rxRamTableViewPage, main_view, dev, 'RX_RAM')

        self.rxRamTableViewPage.pack(expand=True, fill='both')
