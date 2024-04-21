import evk.gui.Page as p
import tkinter as tk
import tkinter.ttk as ttk

import evk.gui.RegFieldView

class TxRxRamRegView():
    def __init__(self, parent, gui_handler, dev, txrx_ram, *args, **kwargs):
        self.txrx_ram = txrx_ram.lower()
        self.gui_handler = gui_handler
        self.host = gui_handler.host
        self.dev = dev
        self.parent = parent
        registerViewPage = p.Page(parent)
        selectorRow = p.Page(registerViewPage)
        regViewRow = p.Page(registerViewPage)
        syncbutton_row = p.Page(registerViewPage)
        idx_label = tk.Label(selectorRow, text='Index ')

        self.current_selected_index = 0
        self.selected_index = tk.StringVar(value=0)
        self.index_selector = ttk.Combobox(selectorRow, values=list(range(64)), state='readonly', width=4, textvariable=self.selected_index)
        self.index_selector.bind('<<ComboboxSelected>>', self.index_selected)

        idx_label.pack(side='left')
        self.index_selector.pack(side='left', expand=False)
        selectorRow.pack(side='top')
        self.regfield_v = evk.gui.RegFieldView.RegFieldView(regViewRow, None, self.host, self.dev, self.txrx_ram+'_v', button_text='Write')
        self.regfield_v.row = 0
        self.regfield_h = evk.gui.RegFieldView.RegFieldView(regViewRow, None, self.host, self.dev, self.txrx_ram+'_h', button_text='Write')
        self.regfield_h.row = 0

        # Three buttons for SyncV, SyncH or SyncVH
        #syncv_button = tk.Button(syncbutton_row, text='Sync. V', command=self._v_ram_sync)
        #syncvh_button = tk.Button(syncbutton_row, text='Sync. V+H', command=self._vh_ram_sync)
        #synch_button = tk.Button(syncbutton_row, text='Sync. H', command=self._h_ram_sync)

        regViewRow.pack()
        #syncv_button.pack(side='left', padx=10, pady=10)
        #syncvh_button.pack(side='left', padx=10, pady=10)
        #synch_button .pack(side='left', padx=10, pady=10)
        syncbutton_row.pack(side='bottom')
        registerViewPage.pack()
        self.index_selected()

    def _v_ram_sync(self):
        self.gui_handler.gd[self.dev.get_name()].sync_ram(self.txrx_ram, 'V')

    def _h_ram_sync(self):
        self.gui_handler.gd[self.dev.get_name()].sync_ram(self.txrx_ram, 'H')

    def _vh_ram_sync(self):
        self.gui_handler.gd[self.dev.get_name()].sync_ram(self.txrx_ram, 'VH')

    def index_selected(self, event=None):
        try:
            new_index = int(self.selected_index.get())
        except ValueError:
            self.selected_index.set(str(self.current_selected_index))
            return
        if new_index >= 0 and new_index <= 63:
            self.current_selected_index = new_index
            self.regfield_h.row = new_index
            self.regfield_v.row = new_index
            self.regfield_h.read_reg_value(self.current_selected_index)
            self.regfield_v.read_reg_value(self.current_selected_index)

    def refresh(self):
        pass
