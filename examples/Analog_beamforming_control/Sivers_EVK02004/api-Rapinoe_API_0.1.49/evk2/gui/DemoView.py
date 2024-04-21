import Page as p
import tkinter as tk
import tkinter.ttk as ttk

import DemoTxView
import DemoRxView

DEMO_TX_RAM_INDEX = 0
DEMO_RX_RAM_INDEX = 0

class DemoView():

    def __init__(self, parent, gui_data, dev, *args, **kwargs):
        self.gui_data = gui_data
        self.dev = dev
        self.parent = parent
        self.nb = ttk.Notebook(self.parent)
        self.TxPage = p.Page(self.nb)
        self.RxPage = p.Page(self.nb)

        self.demo_tx_view = DemoTxView.DemoTxView(self.TxPage, self.gui_data, self.dev)
        self.demo_rx_view = DemoRxView.DemoRxView(self.RxPage, self.gui_data, self.dev)

        self.nb.add(self.TxPage, text="TX")
        self.nb.add(self.RxPage, text="RX")
        self.nb.pack(side="top",fill="both", expand=True)
        self.nb.bind('<<NotebookTabChanged>>', self._on_tab_change)

    def _on_tab_change(self, event):
        tab = event.widget.tab('current')['text']
        if tab == 'TX':
            self.demo_tx_view._update()
        elif tab == 'RX':
            self.demo_rx_view._update()

    def _update(self, trx=None):
        if trx == None:
            trx = self.nb.tab(self.nb.select(), 'text')
        if trx == 'TX':
            self.demo_tx_view._update()
        elif trx == 'RX':
            self.demo_rx_view._update()
