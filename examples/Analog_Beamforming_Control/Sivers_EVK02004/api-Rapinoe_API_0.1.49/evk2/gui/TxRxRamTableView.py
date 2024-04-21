from traceback import print_tb
import Page as p
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.filedialog as tkFileDialog
import math

from common import fhex
import ScrolledFrame
import tooltip
import smart_entry
import RamFileSelector

NUM_OF_ROWS = 65
STYLE = 'clam'

class TxRxRamTableView():
    def __init__(self, parent, main_view, dev, txrx_ram, *args, **kwargs):
        # Table view format selector
        self.main_view = main_view
        self.dev = dev
        self.txrx_ram = txrx_ram
        self.parent = parent
        selectorRow = p.Page(parent)
        self.selected_table_format = tk.StringVar(value='Field view')
        self.table_format_selector = ttk.Combobox(selectorRow, values=['Field view', 'Compact view', 'Byte view'], state='readonly', width=14, textvariable=self.selected_table_format)
        self.table_format_selector.bind('<<ComboboxSelected>>', self.table_format_selected)

        # Polarization selector
        self.selected_polarization = tk.StringVar(value='Horizontal polarization')
        self.polarization_selector_values = {'Horizontal polarization':'H', 'Vertical polarization':'V'}
        self.polarization_selector = ttk.Combobox(selectorRow, values=list(self.polarization_selector_values.keys()), state='readonly', width=20, textvariable=self.selected_polarization)
        self.polarization_selector.bind('<<ComboboxSelected>>', self.polarization_selected)

        index_selection_frame = tk.LabelFrame(selectorRow, relief=tk.GROOVE, text='Selected gain index', width=10)
        index_label = tk.Label(index_selection_frame, text='Index')
        self.spinbox_selected_index = tk.IntVar()
        if txrx_ram.lower() == 'tx_ram':
            self.spinbox_selected_index.set(self.main_view.gui_data.exec_command("self._host.chip.tx.curr_gain_index(__RAP__, 'H')"))
        else:
            #self.spinbox_selected_index.set(self.gui_handler.host.chip.spi.rd(dev, 'rx_gain_indx_h'))
            self.spinbox_selected_index.set(self.main_view.gui_data.exec_command("self._host.chip.spi.rd(__RAP__, 'rx_gain_indx_h')"))
        self.index_spinbox = tk.Spinbox(index_selection_frame, width=10, from_=0, to=NUM_OF_ROWS-2, textvariable=self.spinbox_selected_index, wrap=True, state='readonly', command=self.index_spinbox_value_changed)
        self.index_spinbox.bind('<Return>', self.set_index)
        self.set_index_button = tk.Button(index_selection_frame, text='Set', command=self.set_index, width=8)
        self.set_index_button.configure(bg='light grey')

        separatorRow = p.Page(parent)
        separator = ttk.Separator(separatorRow, orient='horizontal')

        buttonRow = p.Page(parent)
        self.read_button = tk.Button(buttonRow, text='Read', command=self.read_ram, width=8)
        self.read_button.configure(bg='light grey')
        self.write_button = tk.Button(buttonRow, text='Write', command=self.write_ram, width=8)
        self.write_button.configure(bg='light grey')
        self.ram_file_button = tk.Button(buttonRow, text='Load RAM file', command=self.open_table_selector, width=11)
        self.ram_file_button.configure(bg='light grey')
        self.set_new_index_checkbutton_var = tk.IntVar()
        self.set_new_index_checkbutton_var.set(1)
        self.set_new_index_checkbutton = ttk.Checkbutton(buttonRow, text='Activate lowest gain index on load', variable=self.set_new_index_checkbutton_var)

        separatorRow2 = p.Page(parent)
        separator2 = ttk.Separator(separatorRow2, orient='horizontal')

        self.table_format_selector.pack(side='left', expand=False)
        self.polarization_selector.pack(side='left', expand=False)
        index_label.pack(side='left', expand=False)
        self.index_spinbox.pack(side='left', expand=False, pady=10)
        index_selection_frame.pack(side='left', expand=False, padx=10)
        self.set_index_button.pack(side='left', expand=False, padx=10)
        separator.pack(side='bottom', fill='x', pady=8, expand=True)
        selectorRow.pack(side='top', expand=False, anchor='nw', fill='x')
        separatorRow.pack(side='top', expand=False, anchor='nw', fill='x')

        self.read_button.pack(side='left', expand=False)
        self.write_button.pack(side='left', expand=False)
        self.ram_file_button.pack(side='left', expand=False)
        self.set_new_index_checkbutton.pack(side='left', expand=False, padx=10)
        #self.sync_button.pack(side='left', expand=False)
        buttonRow.pack(side='top', expand=False, anchor='nw', fill='x')
        separator2.pack(side='top', expand=False, anchor='nw', fill='x')
        separatorRow2.pack(side='top', expand=False, anchor='nw', fill='x')

        # Read specified RAM area from device
        self.ram_value = {}
        #self.ram_value['h'] = self.gui_handler.gd[self.dev.get_name()].read_ram_complete(self.txrx_ram.lower()+'_h', 'compact')
        self.ram_value['h'] = self.main_view.gui_data.read_ram_complete(self.txrx_ram.lower()+'_h', 'compact')
        #self.ram_value['v'] = self.gui_handler.gd[self.dev.get_name()].read_ram_complete(self.txrx_ram.lower()+'_v', 'compact')
        self.ram_value['v'] = self.main_view.gui_data.read_ram_complete(self.txrx_ram.lower()+'_v', 'compact')

        self.selected_index = {}
        self.selected_index['h'] = 0
        self.selected_index['v'] = 0

        self.fv = TxRxRamTableFieldView(self, parent, main_view, dev, txrx_ram, self.ram_value, 10, self.value_modified, *args, **kwargs)
        self.bv = TxRxRamTableByteView(self, parent, main_view, dev, txrx_ram, self.ram_value, col_width=8, value_changed_callback=self.value_modified, *args, **kwargs)
        self.cv = TxRxRamTableCompactView(self, parent, main_view, dev, txrx_ram, self.ram_value, value_changed_callback=self.value_modified, *args, **kwargs)

        self.fv.show()

    def index_spinbox_value_changed(self):
        p = self.get_selected_polarization()
        if self.spinbox_selected_index.get() != self.selected_index[p]:
            self.set_index_button.configure(bg='yellow')
        else:
            self.set_index_button.configure(bg='light grey')

    def table_format_selected(self, event):
        table_format = self.selected_table_format.get()
        if table_format == 'Field view':
            self.bv.hide()
            self.cv.hide()
            self.fv.show()
        elif table_format == 'Byte view':
            self.fv.hide()
            self.cv.hide()
            self.bv.show()
        else:
            self.fv.hide()
            self.bv.hide()
            self.cv.show()

    def get_selected_polarization(self):
        p = self.selected_polarization.get()
        if p == 'Horizontal polarization':
            return 'h'
        else:
            return 'v'

    def polarization_selected(self, event):
        self.set_index_button.configure(bg='light grey')
        table_format = self.selected_table_format.get()
        p = self.get_selected_polarization()
        if self.txrx_ram.lower() == 'tx_ram':
            self.spinbox_selected_index.set(self.main_view.gui_data.exec_command("self._host.chip.tx.curr_gain_index(__RAP__, '{}')".format(p.upper())))
        else:
            #self.spinbox_selected_index.set(self.gui_handler.host.chip.spi.rd(self.dev, 'rx_gain_indx_'+p.lower()))
            self.spinbox_selected_index.set(self.main_view.gui_data.exec_command("self._host.chip.spi.rd(__RAP__, 'rx_gain_indx_'+'{}')".format(p.lower())))

        self.fv.polarization_selected(p)
        self.bv.polarization_selected(p)
        self.cv.polarization_selected(p)

    def value_modified(self):
        self.write_button.configure(bg='yellow')
        self.polarization_selector.configure(state='disable')

    def write_ok(self):
        self.write_button.configure(bg='light grey')
        self.polarization_selector.configure(state='readonly')

    def write_failed(self):
        self.write_button.configure(bg='red')

    def read_ram(self):
        self.reload()
        self.fv.reload_ram(self.ram_value)
        self.fv.update_view()
        self.cv.reload_ram(self.ram_value)
        self.cv.update_view()
        self.bv.reload_ram(self.ram_value)
        self.bv.update_view()

    def set_index(self, x=None):
        pol = self.get_selected_polarization()
        index = self.spinbox_selected_index.get()
        self.selected_index[pol] = index
        if self.txrx_ram.lower() == 'tx_ram':
            if pol == 'h':
                pol = 'TH'
            else:
                pol = 'TV'
            #self.gui_handler.host.chip.tx.gain_rf(self.dev, index, pol)
            self.main_view.gui_data.exec_command("self._host.chip.tx.gain_rf(__RAP__, {}, '{}')".format(index, pol))
        else:
            if pol == 'h':
                pol = 'RH'
            else:
                pol = 'RV'
            #self.gui_handler.host.chip.rx.gain(self.dev, index, pol)
            self.main_view.gui_data.exec_command("self._host.chip.rx.gain(__RAP__, {}, '{}')".format(index, pol))

        self.set_index_button.configure(bg='light grey')

    def open_table_selector(self):
        pol = self.get_selected_polarization()
        filename = tkFileDialog.askopenfile(initialdir = "./config/ram",title = "Select RAM file",defaultextension=".xml",filetypes = (("XML files","*.xml"),("all files","*.*")))
        if filename != None:
            if pol == 'h':
                filter = self.txrx_ram + '_H'
            else:
                filter = self.txrx_ram + '_V'
            ram_file_selector = RamFileSelector.RamFileSelector(self.parent, filename.name, filter=filter, select_callback=self.ram_table_selected)

    def ram_table_selected(self, filename, table_id):
        if self.get_selected_polarization() == 'v' and self.txrx_ram == 'RX_RAM':
            # Read active gain indexes and write them back after new RAM content has been written
            tx_v_gain_index = self.main_view.gui_data.exec_command("self._host.chip.tx.curr_gain_index(__RAP__, 'V')")
            tx_h_gain_index = self.main_view.gui_data.exec_command("self._host.chip.tx.curr_gain_index(__RAP__, 'H')")
            #rx_h_gain_index = self.gui_handler.host.chip.spi.rd(self.dev, 'rx_gain_indx_h')
            rx_h_gain_index = self.main_view.gui_data.read_register('rx_gain_indx_h')
        #r = self.gui_handler.host.chip.ram.fill(self.dev, table_id=table_id, filename=filename)
        r = self.main_view.gui_data.ram_fill(table_id, filename)
        if self.get_selected_polarization() == 'v' and self.txrx_ram == 'RX_RAM':
            #self.gui_handler.host.chip.tx.save_gain_index_to_ram(self.dev, tx_v_gain_index, 'V')
            self.main_view.gui_data.exec_command("self._host.chip.tx.save_gain_index_to_ram(__RAP__, {}, 'V')".format(tx_v_gain_index))
            #self.gui_handler.host.chip.tx.save_gain_index_to_ram(self.dev, tx_h_gain_index, 'H')
            self.main_view.gui_data.exec_command("self._host.chip.tx.save_gain_index_to_ram(__RAP__, {}, 'H')".format(tx_h_gain_index))
        self.spinbox_selected_index.set(r[table_id]['last_index'])
        if self.set_new_index_checkbutton_var.get():
            self.set_index()
        else:
            self.set_index_button.configure(bg='yellow')

        self.read_ram()

    def write_ram(self):
        if self.fv.view_active:
            view = self.fv
        elif self.cv.view_active:
            view = self.cv
        elif self.bv.view_active:
            view = self.bv

        saved_rows = self.cv.write_changes()
        if saved_rows != None:
            self.fv.clear_modified_tags(saved_rows)
            self.bv.clear_modified_tags(saved_rows)

        #view.write_changes()
        self.write_ok()
        #view.reload_ram()
        view.update_view()

        self.reload()
        self.fv.reload_ram(self.ram_value)
        self.fv.update_view()
        self.cv.reload_ram(self.ram_value)
        self.cv.update_view()
        self.bv.reload_ram(self.ram_value)
        self.bv.update_view()

    def sync_ram(self):
        if self.fv.view_active:
            view = self.fv
        elif self.cv.view_active:
            view = self.cv
        elif self.bv.view_active:
            view = self.bv
        view.sync_ram()

    def refresh(self):
        pass

    def reload(self):
        #self.ram_value['h'] = self.gui_handler.gd[self.dev.get_name()].read_ram_complete(self.txrx_ram.lower()+'_h', 'compact')
        self.ram_value['h'] = self.main_view.gui_data.read_ram_complete(self.txrx_ram.lower()+'_h', 'compact')
        #self.ram_value['v'] = self.gui_handler.gd[self.dev.get_name()].read_ram_complete(self.txrx_ram.lower()+'_v', 'compact')
        self.ram_value['v'] = self.main_view.gui_data.read_ram_complete(self.txrx_ram.lower()+'_v', 'compact')

    def hide(self):
        self.columnNameRow.pack_forget()
        self.sf.pack_forget()
        self.view_active = False

    def show(self):
        self.columnNameRow.pack(expand=False, anchor='nw')
        self.sf.pack(side='top', expand=True, anchor='nw', fill='y')
        self.view_active = True

    def reload_ram(self, ram_value=None):
        if ram_value == None:
            #self.ram_value['v'] = self.gui_handler.gd[self.dev.get_name()].read_ram_complete(self.txrx_ram.lower()+'_v', 'compact')
            self.ram_value['v'] = self.main_view.gui_data.read_ram_complete(self.txrx_ram.lower()+'_v', 'compact')
            #self.ram_value['h'] = self.gui_handler.gd[self.dev.get_name()].read_ram_complete(self.txrx_ram.lower()+'_h', 'compact')
            self.ram_value['h'] = self.main_view.gui_data.read_ram_complete(self.txrx_ram.lower()+'_h', 'compact')
        else:
            self.ram_value = ram_value

    def update_view(self):
        for i in range(len(self.ram_value[self.polarization])-2):
            self.rows[i+1][1].set_value(fhex(self.ram_value[self.polarization][i], self.number_of_digits), False)

    def sync_ram(self):
        pass

    def table_changed(self, view, iid):
        value = view.get_compact(iid)
        view_type = type(view).__name__
        if view_type == 'TxRxRamTableCompactView':
            self.bv.set_row_value(iid, value)
            self.fv.set_row_value(iid, value)
        elif view_type == 'TxRxRamTableByteView':
            self.cv.set_row_value(iid, value)
            self.fv.set_row_value(iid, value)
        elif view_type == 'TxRxRamTableFieldView':
            self.cv.set_row_value(iid, value)
            self.bv.set_row_value(iid, value)

        self.value_modified()

class TxRxRamTableCompactView():
    def __init__(self, owner, parent, main_view, dev, txrx_ram, ram_value, col_width=15, value_changed_callback=None, *args, **kwargs):
        self.owner = owner
        self.parent = parent
        self.main_view = main_view
        self.dev = dev
        self.txrx_ram = txrx_ram.lower()
        self.polarization = 'h'
        self.rows = []
        r = []
        self.view_active = False
        self.entryPopup = None
        self.pointed_column = None

        #self.number_of_bytes = self.gui_handler.host.spi.register_map.regs[self.txrx_ram.lower()+'_h']['length']
        self.number_of_bytes = self.main_view.gui_data.get_register_map_regs()[self.txrx_ram.lower()+'_h']['length']
        self.number_of_digits = self.number_of_bytes * 2
        self.ram_value = ram_value

        self.field_names = ['Value']
        column_names = ['Index'] + self.field_names

        column_names_int = list(range(len(self.field_names)))
        column_names_int.reverse()
        column_names = [str(n) for n in column_names_int]
        column_names = ['Index'] + column_names

        #################################################
        def fixed_map(option):
            # Fix for setting text colour for Tkinter 8.6.9
            # From: https://core.tcl.tk/tk/info/509cafafae
            #
            # Returns the style map for 'option' with any styles starting with
            # ('!disabled', '!selected', ...) filtered out.

            # style.map() returns an empty list for missing options, so this
            # should be future-safe.
            return [elm for elm in style.map('Treeview', query_opt=option) if elm[:2] != ('!disabled', '!selected')]

        style = ttk.Style()
        style.theme_use(STYLE)
        style.map('Treeview', foreground=fixed_map('foreground'), background=fixed_map('background'))
        #################################################
        #style.configure('Treeview.Heading', background="blue")

        #self.sf = ScrolledFrame.ScrolledFrame(parent)
        #self.main_table = ttk.Treeview(self.sf.interior)
        self.main_table = ScrolledTreeView(parent)
        self.main_table.rows_modified = []
        self.main_table.bind('<Double-Button-1>', self.on_double_click)
        self.main_table.bind('<Button-1>', self.on_click)
        #self.main_table.bind('<Motion>', self.enter)
        #self.main_table.bind('<Leave>', self.leave)

        columns = ''
        for j in range(len(self.field_names)):
            columns = columns + ' ' + str(self.field_names[j])
        self.main_table.configure(columns=columns)
        # build_treeview_support starting.
        self.main_table.heading("#0",text='Index')
        self.main_table.heading("#0",anchor='center')
        self.main_table.column("#0",width='50')
        self.main_table.column("#0",minwidth='50')
        self.main_table.column("#0",stretch=0)
        self.main_table.column("#0",anchor='center')
        for j in range(len(self.field_names)):
            column_name = 'Col'+str(j+1)
            self.main_table.heading(self.field_names[j], text=self.field_names[j])
            self.main_table.heading(self.field_names[j], anchor='center')
            self.main_table.column(self.field_names[j], width="50")
            self.main_table.column(self.field_names[j], minwidth="50")
            self.main_table.column(self.field_names[j], stretch=1)
            self.main_table.column(self.field_names[j], anchor='center')

        for i in range(NUM_OF_ROWS-1):
            row_values = []
            for j in range(len(self.field_names)):
                row_values.append(fhex(self.ram_value[self.polarization][i][j], self.number_of_digits))
            if (i % 2) == 0:
                tag='WHITE'
            else:
                tag='WHITESMOKE'
            self.main_table.insert('', 'end', text=str(i), values=row_values, iid=i, tags=(tag,))
            self.main_table.tag_configure('WHITESMOKE', background='whitesmoke')
            #self.main_table.tag_configure('EVEN_ROW', background='purple')


    def on_click(self, event):
        if self.entryPopup != None:
            self.entryPopup.destroy()
            self.entryPopup = None

    def on_double_click(self, event):
        ''' Executed, when a row is double-clicked. Opens 
        read-only EntryPopup above the item's column, so it is possible
        to select text '''

        if self.entryPopup != None:
            self.entryPopup.destroy()
            self.entryPopup = None

        # what row and column was clicked on
        rowid = self.main_table.identify_row(event.y)
        column = self.main_table.identify_column(event.x)

        rowid_int = int(rowid)
        column_int = int(column.replace('#',''))

        # get column position info
        # This doesn't work
        x,y,width,height = self.main_table.bbox(rowid_int, column_int)

        pady = 2

        # place Entry popup properly
        values = self.main_table.item(rowid, 'values')
        self.entryPopup = EntryPopup(self, rowid, values, column_int, [self.number_of_digits*4])
        self.entryPopup.place( x=event.x, y=event.y, anchor='w', relwidth=0.12)

    def get_compact(self, iid):
        value = 0
        values = self.main_table.item(iid, 'values')
        try:
            value = self.get_int_value(values[0])
        except:
            value = None
        return value

    def set_row_value(self, iid, compact_value):
        self.main_table.item(iid, values=[fhex(compact_value, self.number_of_digits)])
        self.main_table.item(iid, tags=('MODIFIED',))
        self.main_table.tag_configure('MODIFIED', background='yellow')
        if self.main_table.rows_modified.count(iid) == 0:
            self.main_table.rows_modified.append(iid)

    def hide(self):
        self.main_table.pack_forget()
        self.view_active = False

    def show(self):
        self.main_table.pack(expand=True, fill='both')
        self.view_active = True

    def polarization_selected(self, polarization):
        # Reload RAM
        self.polarization = polarization
        self.update_view()

    def reload_ram(self, ram_value=None):
        if ram_value == None:
            #self.ram_value['v'] = self.gui_handler.gd[self.dev.get_name()].read_ram_complete(self.txrx_ram.lower()+'_v', 'compact')
            self.ram_value['v'] = self.main_view.gui_data.read_ram_complete(self.txrx_ram.lower()+'_v', 'compact')
            #self.ram_value['h'] = self.gui_handler.gd[self.dev.get_name()].read_ram_complete(self.txrx_ram.lower()+'_h', 'compact')
            self.ram_value['h'] = self.main_view.gui_data.read_ram_complete(self.txrx_ram.lower()+'_h', 'compact')
        else:
            self.ram_value = ram_value

    def update_view(self):
        for i in range(NUM_OF_ROWS-1):
            row_values = []
            for j in range(len(self.field_names)):
                row_values.append(fhex(self.ram_value[self.polarization][i][j],self.number_of_digits))
            if (i % 2) == 0:
                tag='WHITE'
            else:
                tag='WHITESMOKE'
            self.main_table.item(str(i), values=row_values)
            self.main_table.tag_configure('WHITESMOKE', background='whitesmoke')


    def get_int_value(self, v):
        int_val = None
        try:
            v = v.lower()
            if v.startswith('0x'):
                int_val = int(v, 16)
            elif v.startswith('0b'):
                int_val = int(v, 2)
            else:
                int_val = int(v)
        except:
            pass
        return int_val

    def write_changes(self):
        any_rows_modified = (self.main_table.rows_modified != [])
        if any_rows_modified:
            modified_rows = list(self.main_table.rows_modified)
            for rowid in modified_rows:
                values = self.main_table.item(rowid, 'values')
                value = 0
                try:
                    value = self.get_int_value(values[0])
                except:
                    value = None

                if value != None:
                    #self.gui_handler.gd[self.dev.get_name()].write_ram(self.txrx_ram.lower()+'_'+self.polarization, int(rowid), value)
                    self.main_view.gui_data.write_ram(self.txrx_ram.lower()+'_'+self.polarization, int(rowid), value)
                    self.main_table.rows_modified.remove(rowid)
                    if (int(rowid) % 2) == 0:
                        tag='WHITE'
                    else:
                        tag='WHITESMOKE'
                    self.main_table.item(rowid, tags=(tag,))
            return modified_rows

    def _separate_values(self, ram_value, mask):
        v = {}
        for i in range(64):
            v[i] = [0]*len(mask)
            value = ram_value[i][0]
            for j in range(len(v[i])):
                xmask = 2**mask[j]-1
                v[i][len(v[i])-j-1] = value & xmask
                value = value >> mask[j]

        return v

    def table_changed(self, iid):
        self.owner.table_changed(self, iid)

    # def sync_ram(self):
    #     pass


class TxRxRamTableByteView():
    def __init__(self, owner, parent, main_view, dev, txrx_ram, ram_value, col_width=15, value_changed_callback=None, *args, **kwargs):
        self.owner = owner
        self.parent = parent
        self.main_view = main_view
        self.dev = dev
        self.txrx_ram = txrx_ram.lower()
        self.polarization = 'h'
        self.rows = []
        r = []
        self.view_active = False
        self.entryPopup = None
        self.pointed_column = None
        self.toolTip = None

        #self.number_of_bytes = self.gui_handler.host.spi.register_map.regs[self.txrx_ram.lower()+'_h']['length']
        self.number_of_bytes = self.main_view.gui_data.get_register_map_regs()[self.txrx_ram.lower()+'_h']['length']
        self.ram_value = {}
        self.ram_value['v'] = self._separate_values(ram_value['v'], [8]*self.number_of_bytes)
        self.ram_value['h'] = self._separate_values(ram_value['h'], [8]*self.number_of_bytes)

        self.field_names = list(range(self.number_of_bytes))
        self.field_names.reverse()
        column_names = ['Index'] + self.field_names

        column_names_int = list(range(len(self.field_names)))
        column_names_int.reverse()
        column_names = [str(n) for n in column_names_int]
        column_names = ['Index'] + column_names

        #################################################
        def fixed_map(option):
            # Fix for setting text colour for Tkinter 8.6.9
            # From: https://core.tcl.tk/tk/info/509cafafae
            #
            # Returns the style map for 'option' with any styles starting with
            # ('!disabled', '!selected', ...) filtered out.

            # style.map() returns an empty list for missing options, so this
            # should be future-safe.
            return [elm for elm in style.map('Treeview', query_opt=option) if elm[:2] != ('!disabled', '!selected')]

        style = ttk.Style()
        style.theme_use(STYLE)
        style.map('Treeview', foreground=fixed_map('foreground'), background=fixed_map('background'))
        #################################################
        #style.configure('Treeview.Heading', background="blue")

        #self.sf = ScrolledFrame.ScrolledFrame(parent)
        #self.main_table = ttk.Treeview(self.sf.interior)
        self.main_table = ScrolledTreeView(parent)
        self.main_table.rows_modified = []
        self.main_table.bind('<Double-Button-1>', self.on_double_click)
        self.main_table.bind('<Button-1>', self.on_click)
        #self.main_table.bind('<Motion>', self.enter)
        #self.main_table.bind('<Leave>', self.leave)

        columns = ''
        for j in range(len(self.field_names)):
            columns = columns + ' ' + str(self.field_names[j])
        self.main_table.configure(columns=columns)
        # build_treeview_support starting.
        self.main_table.heading("#0",text='Index')
        self.main_table.heading("#0",anchor='center')
        self.main_table.column("#0",width='50')
        self.main_table.column("#0",minwidth='50')
        self.main_table.column("#0",stretch=0)
        self.main_table.column("#0",anchor='center')
        for j in range(len(self.field_names)):
            column_name = 'Col'+str(j+1)
            self.main_table.heading(self.field_names[j], text=str(len(self.field_names)-j-1))
            self.main_table.heading(self.field_names[j], anchor='center')
            self.main_table.column(self.field_names[j], width="50")
            self.main_table.column(self.field_names[j], minwidth="50")
            self.main_table.column(self.field_names[j], stretch=1)
            self.main_table.column(self.field_names[j], anchor='center')

        for i in range(NUM_OF_ROWS-1):
            row_values = []
            for j in range(len(self.field_names)):
                row_values.append(fhex(self.ram_value[self.polarization][i][j],2))
            if (i % 2) == 0:
                tag='WHITE'
            else:
                tag='WHITESMOKE'
            self.main_table.insert('', 'end', text=str(i), values=row_values, iid=i, tags=(tag,))
            self.main_table.tag_configure('WHITESMOKE', background='whitesmoke')
            #self.main_table.tag_configure('EVEN_ROW', background='purple')


    def on_click(self, event):
        if self.entryPopup != None:
            self.entryPopup.destroy()
            self.entryPopup = None

    def on_double_click(self, event):
        ''' Executed, when a row is double-clicked. Opens 
        read-only EntryPopup above the item's column, so it is possible
        to select text '''

        if self.entryPopup != None:
            self.entryPopup.destroy()
            self.entryPopup = None

        # what row and column was clicked on
        rowid = self.main_table.identify_row(event.y)
        column = self.main_table.identify_column(event.x)

        rowid_int = int(rowid)
        column_int = int(column.replace('#',''))
        if column_int == 0:
            return

        # get column position info
        # This doesn't work
        x,y,width,height = self.main_table.bbox(rowid_int, column_int)

        pady = 2

        # place Entry popup properly
        values = self.main_table.item(rowid, 'values')
        self.entryPopup = EntryPopup(self, rowid, values, column_int, [8]*self.number_of_bytes)
        self.entryPopup.place( x=event.x, y=event.y, anchor='w', relwidth=0.05)


    def hide(self):
        self.main_table.pack_forget()
        self.view_active = False

    def show(self):
        self.main_table.pack(expand=True, fill='both')
        self.view_active = True

    def polarization_selected(self, polarization):
        # Reload RAM
        self.polarization = polarization
        self.update_view()

    def reload_ram(self, ram_value=None):
        if ram_value == None:
            #self.ram_value['h'] = self.gui_handler.gd[self.dev.get_name()].read_ram_complete(self.txrx_ram.lower()+'_h', 'compact')
            self.ram_value['h'] = self.main_view.gui_data.read_ram_complete(self.txrx_ram.lower()+'_h', 'compact')
            self.ram_value['h'] = self._separate_values(self.ram_value['h'], [8]*self.number_of_bytes)
            #self.ram_value['v'] = self.gui_handler.gd[self.dev.get_name()].read_ram_complete(self.txrx_ram.lower()+'_v', 'compact')
            self.ram_value['v'] = self.main_view.gui_data.read_ram_complete(self.txrx_ram.lower()+'_v', 'compact')
            self.ram_value['v'] = self._separate_values(self.ram_value['v'], [8]*self.number_of_bytes)
        else:
            self.ram_value['h'] = self._separate_values(ram_value['h'], [8]*self.number_of_bytes)
            self.ram_value['v'] = self._separate_values(ram_value['v'], [8]*self.number_of_bytes)

    def update_view(self):
        for i in range(NUM_OF_ROWS-1):
            row_values = []
            for j in range(len(self.field_names)):
                row_values.append(fhex(self.ram_value[self.polarization][i][j],2))
            if (i % 2) == 0:
                tag='WHITE'
            else:
                tag='WHITESMOKE'
            self.main_table.item(str(i), values=row_values)
            self.main_table.tag_configure('WHITESMOKE', background='whitesmoke')

    def get_compact(self, iid):
        values = self.main_table.item(iid, 'values')
        v = [0]*self.number_of_bytes
        value = 0
        for n in range(self.number_of_bytes):
            try:
                v[n] = self.get_int_value(values[n])
                value += ((v[n]&0xff)<<((self.number_of_bytes-1-n)*8))
            except:
                v[n] = None

        if None in v:
            value = None
        return value

    def set_row_value(self, iid, compact_value):
        formatted_value = self._separate_value(compact_value, [8]*self.number_of_bytes)
        self.main_table.item(iid, values=formatted_value)
        self.main_table.item(iid, tags=('MODIFIED',))
        self.main_table.tag_configure('MODIFIED', background='yellow')
        if self.main_table.rows_modified.count(iid) == 0:
            self.main_table.rows_modified.append(iid)

    def clear_modified_tags(self, saved_rows):
        for iid in saved_rows:
            if (int(iid) % 2) == 0:
                tag='WHITE'
            else:
                tag='WHITESMOKE'
            self.main_table.item(iid, tags=(tag,))
            if self.main_table.rows_modified.count(iid) != 0:
                self.main_table.rows_modified.remove(iid)

    def get_int_value(self, v):
        int_val = None
        try:
            v = v.lower()
            if v.startswith('0x'):
                int_val = int(v, 16)
            elif v.startswith('0b'):
                int_val = int(v, 2)
            else:
                int_val = int(v)
        except:
            pass
        return int_val

    def write_changes(self):
        any_rows_modified = (self.main_table.rows_modified != [])
        if any_rows_modified:
            modified_rows = list(self.main_table.rows_modified)
            for rowid in modified_rows:
                values = self.main_table.item(rowid, 'values')
                v = [0]*self.number_of_bytes
                value = 0
                for n in range(self.number_of_bytes):
                    try:
                        v[n] = self.get_int_value(values[n])
                        value += ((v[n]&0xff)<<((self.number_of_bytes-1-n)*8))
                    except:
                        v[n] = None

                if None in v:
                    value = None
                if value != None:
                    #self.gui_handler.gd[self.dev.get_name()].write_ram(self.txrx_ram.lower()+'_'+self.polarization, int(rowid), value)
                    self.main_view.gui_data.write_ram(self.txrx_ram.lower()+'_'+self.polarization, int(rowid), value)
                    self.main_table.rows_modified.remove(rowid)
                    if (int(rowid) % 2) == 0:
                        tag='WHITE'
                    else:
                        tag='WHITESMOKE'
                    self.main_table.item(rowid, tags=(tag,))
            return modified_rows

    def _separate_value(self, value, mask):
        v = [0]*len(mask)
        for j in range(len(v)):
            xmask = 2**mask[j]-1
            v[len(v)-j-1] = fhex(value & xmask, 2)
            value = value >> mask[j]
        return v

    def _separate_values(self, ram_value, mask):
        v = {}
        for i in range(64):
            v[i] = [0]*len(mask)
            value = ram_value[i][0]
            for j in range(len(v[i])):
                xmask = 2**mask[j]-1
                v[i][len(v[i])-j-1] = value & xmask
                value = value >> mask[j]

        return v

    def table_changed(self, iid):
        self.owner.table_changed(self, iid)


    # def sync_ram(self):
    #     pass



class TxRxRamTableFieldView():
    def __init__(self, owner, parent, main_view, dev, txrx_ram, ram_value, col_width=15, value_changed_callback=None, *args, **kwargs):
        self.owner = owner
        self.parent = parent
        self.main_view = main_view
        self.dev = dev
        self.txrx_ram = txrx_ram.lower()
        self.polarization = 'h'
        self.rows = []
        r = []
        self.view_active = False
        self.entryPopup = None
        self.pointed_column = None
        self.toolTip = None

        #fields = list(self.gui_handler.host.spi.register_map.reg_map[self.txrx_ram+'_v'])
        fields = list(self.main_view.gui_data.get_register_fields(self.txrx_ram+'_v'))
        self.field_details = [None]*len(fields)
        n = 0
        for field in fields:
            reg_field = self.main_view.gui_data.get_register_field(self.txrx_ram+'_v', field)
            lsb = reg_field['Lsb']
            msb = reg_field['Msb']
            #lsb = self.gui_handler.host.spi.register_map.reg_map[self.txrx_ram+'_v'][field]['Lsb']
            #msb = self.gui_handler.host.spi.register_map.reg_map[self.txrx_ram+'_v'][field]['Msb']
            self.field_details[n] = {'field':field, 'lsb':lsb, 'msb':msb, 'size':msb-lsb+1}
            n = n + 1

        self.field_sizes = [n['size'] for n in self.field_details]

        self.ram_value = {}
        self.ram_value['v'] = self._separate_values(ram_value['v'], self.field_sizes)
        self.ram_value['h'] = self._separate_values(ram_value['h'], self.field_sizes)

        column_names_int = list(range(len(fields)))
        column_names_int.reverse()
        column_names = [str(n) for n in column_names_int]
        self.field_names = fields
        column_names = ['Index'] + column_names

        #################################################
        def fixed_map(option):
            # Fix for setting text colour for Tkinter 8.6.9
            # From: https://core.tcl.tk/tk/info/509cafafae
            #
            # Returns the style map for 'option' with any styles starting with
            # ('!disabled', '!selected', ...) filtered out.

            # style.map() returns an empty list for missing options, so this
            # should be future-safe.
            return [elm for elm in style.map('Treeview', query_opt=option) if elm[:2] != ('!disabled', '!selected')]

        style = ttk.Style()
        style.theme_use(STYLE)
        style.map('Treeview', foreground=fixed_map('foreground'), background=fixed_map('background'))
        #################################################
        #style.configure('Treeview.Heading', background="blue")

        #self.sf = ScrolledFrame.ScrolledFrame(parent)
        #self.main_table = ttk.Treeview(self.sf.interior)
        self.main_table = ScrolledTreeView(parent)
        self.main_table.rows_modified = []
        self.main_table.bind('<Double-Button-1>', self.on_double_click)
        self.main_table.bind('<Button-1>', self.on_click)
        self.main_table.bind('<Motion>', self.enter)
        self.main_table.bind('<Leave>', self.leave)

        columns = ''
        for j in range(len(self.field_names)):
            columns = columns + ' ' + self.field_names[j]
        self.main_table.configure(columns=columns)
        # build_treeview_support starting.
        self.main_table.heading("#0",text='Index')
        self.main_table.heading("#0",anchor='center')
        self.main_table.column("#0",width='50')
        self.main_table.column("#0",minwidth='50')
        self.main_table.column("#0",stretch=0)
        self.main_table.column("#0",anchor='center')
        for j in range(len(self.field_names)):
            column_name = 'Col'+str(j+1)
            self.main_table.heading(self.field_names[j], text=str(len(self.field_names)-j-1))
            self.main_table.heading(self.field_names[j], anchor='center')
            self.main_table.column(self.field_names[j], width="50")
            self.main_table.column(self.field_names[j], minwidth="50")
            self.main_table.column(self.field_names[j], stretch=1)
            self.main_table.column(self.field_names[j], anchor='center')

        for i in range(NUM_OF_ROWS-1):
            row_values = []
            for j in range(len(self.field_names)):
                row_values.append(fhex(self.ram_value[self.polarization][i][j],2))
            if (i % 2) == 0:
                tag='WHITE'
            else:
                tag='WHITESMOKE'
            self.main_table.insert('', 'end', text=str(i), values=row_values, iid=i, tags=(tag,))
            self.main_table.tag_configure('WHITESMOKE', background='whitesmoke')
            #self.main_table.tag_configure('EVEN_ROW', background='purple')

        self.main_table.pack(expand=True, fill='both')

    def enter(self, event):
        column = self.main_table.identify_column(event.x)
        if column == '#0':
            return
        if column == '':
            return
        if self.pointed_column != column:
            self.pointed_column = column
            if self.toolTip != None:
                self.toolTip.hidetip()
            text = self.field_names[int(column.replace('#',''))-1]
            if text.endswith('_v'):
                if self.polarization == 'v':
                    pass
                else:
                    text = text[0:-1] + 'h'
            self.toolTip = tooltip.ToolTip(self.main_table, text=text+'['+str(self.field_sizes[int(column.replace('#',''))-1])+' bits]')
            self.toolTip.showtip(self.main_table.winfo_pointerx()+40, self.main_table.winfo_pointery()-40)

    def leave(self, event):
        self.pointed_column = None
        if self.toolTip != None:
            self.toolTip.hidetip()

    def on_click(self, event):
        if self.entryPopup != None:
            self.entryPopup.destroy()
            self.entryPopup = None

    def on_double_click(self, event):
        ''' Executed, when a row is double-clicked. Opens 
        read-only EntryPopup above the item's column, so it is possible
        to select text '''

        if self.entryPopup != None:
            self.entryPopup.destroy()
            self.entryPopup = None

        # what row and column was clicked on
        rowid = self.main_table.identify_row(event.y)
        column = self.main_table.identify_column(event.x)

        rowid_int = int(rowid)
        column_int = int(column.replace('#',''))
        if column_int == 0:
            return

        # get column position info
        # This doesn't work
        x,y,width,height = self.main_table.bbox(rowid_int, column_int)

        pady = 2

        # place Entry popup properly
        values = self.main_table.item(rowid, 'values')
        self.entryPopup = EntryPopup(self, rowid, values, column_int, self.field_sizes)
        self.entryPopup.place( x=event.x, y=event.y, anchor='w', relwidth=0.05)


    def hide(self):
        self.main_table.pack_forget()
        self.view_active = False

    def show(self):
        self.main_table.pack(expand=True, fill='both')
        self.view_active = True

    def polarization_selected(self, polarization):
        # Reload RAM
        self.polarization = polarization
        self.update_view()

    def reload_ram(self, ram_value=None):
        if ram_value == None:
            #self.ram_value['h'] = self.gui_handler.gd[self.dev.get_name()].read_ram_complete(self.txrx_ram.lower()+'_h', 'compact')
            self.ram_value['h'] = self.main_view.gui_data.read_ram_complete(self.txrx_ram.lower()+'_h', 'compact')
            self.ram_value['h'] = self._separate_values(self.ram_value['h'], self.field_sizes)
            #self.ram_value['v'] = self.gui_handler.gd[self.dev.get_name()].read_ram_complete(self.txrx_ram.lower()+'_v', 'compact')
            self.ram_value['v'] = self.main_view.gui_data.read_ram_complete(self.txrx_ram.lower()+'_v', 'compact')
            self.ram_value['v'] = self._separate_values(self.ram_value['v'], self.field_sizes)
        else:
            self.ram_value['h'] = self._separate_values(ram_value['h'], self.field_sizes)
            self.ram_value['v'] = self._separate_values(ram_value['v'], self.field_sizes)

    def update_view(self):
        for i in range(NUM_OF_ROWS-1):
            row_values = []
            for j in range(len(self.field_names)):
                row_values.append(fhex(self.ram_value[self.polarization][i][j],2))
            if (i % 2) == 0:
                tag='WHITE'
            else:
                tag='WHITESMOKE'
            self.main_table.item(str(i), values=row_values)
            self.main_table.tag_configure('WHITESMOKE', background='whitesmoke')

    def get_compact(self, iid):
        values = self.main_table.item(iid, 'values')
        v = [0]*len(self.field_sizes)
        value = 0
        for n in range(len(self.field_sizes)):
            try:
                v[n] = self.get_int_value(values[n])
                value += ((v[n]&(2**self.field_details[n]['size']-1))<<self.field_details[n]['lsb'])
            except:
                v[n] = None

        if None in v:
            value = None
        return value

    def set_row_value(self, iid, compact_value):
        formatted_value = self._separate_value(compact_value, self.field_sizes)
        self.main_table.item(iid, values=formatted_value)
        self.main_table.item(iid, tags=('MODIFIED',))
        self.main_table.tag_configure('MODIFIED', background='yellow')
        if self.main_table.rows_modified.count(iid) == 0:
            self.main_table.rows_modified.append(iid)

    def clear_modified_tags(self, saved_rows):
        for iid in saved_rows:
            if (int(iid) % 2) == 0:
                tag='WHITE'
            else:
                tag='WHITESMOKE'
            self.main_table.item(iid, tags=(tag,))
            if self.main_table.rows_modified.count(iid) != 0:
                self.main_table.rows_modified.remove(iid)


    def get_int_value(self, v):
        int_val = None
        try:
            v = v.lower()
            if v.startswith('0x'):
                int_val = int(v, 16)
            elif v.startswith('0b'):
                int_val = int(v, 2)
            else:
                int_val = int(v)
        except:
            pass
        return int_val

    def write_changes(self):
        any_rows_modified = (self.main_table.rows_modified != [])
        if any_rows_modified:
            modified_rows = list(self.main_table.rows_modified)
            for rowid in modified_rows:
                values = self.main_table.item(rowid, 'values')
                v = [0]*len(self.field_sizes)
                value = 0
                for n in range(len(self.field_sizes)):
                    try:
                        v[n] = self.get_int_value(values[n])
                        value += ((v[n]&(2**self.field_details[n]['size']-1))<<self.field_details[n]['lsb'])
                    except:
                        v[n] = None

                if None in v:
                    value = None
                if value != None:
                    #self.gui_handler.gd[self.dev.get_name()].write_ram(self.txrx_ram.lower()+'_'+self.polarization, int(rowid), value)
                    self.main_view.gui_data.write_ram(self.txrx_ram.lower()+'_'+self.polarization, int(rowid), value)
                    self.main_table.rows_modified.remove(rowid)
                    if (int(rowid) % 2) == 0:
                        tag='WHITE'
                    else:
                        tag='WHITESMOKE'
                    self.main_table.item(rowid, tags=(tag,))
            return modified_rows

    def _separate_value(self, value, mask):
        v = [0]*len(mask)
        for j in range(len(v)):
            xmask = 2**mask[len(v)-j-1]-1
            v[len(v)-j-1] = fhex(value & xmask, 2)
            value = value >> mask[len(v)-j-1]
        return v

    def _separate_values(self, ram_value, mask):
        v = {}
        for i in range(64):
            v[i] = [0]*len(mask)
            value = ram_value[i][0]
            for j in range(len(v[i])):
                xmask = 2**mask[len(v[i])-j-1]-1
                v[i][len(v[i])-j-1] = value & xmask
                value = value >> mask[len(v[i])-j-1]

        return v

    def table_changed(self, iid):
        self.owner.table_changed(self, iid)


    # def sync_ram(self):
    #     pass

class LabelFrame(p.Page):
    def __init__(self, parent, name, width=None, tooltip_name=None, *args, **kwargs):
        p.Page.__init__(self, parent, *args, **kwargs)
        if tooltip_name == None:
            self.tooltip_name = name
        else:
            self.tooltip_name = tooltip_name
        if width == None:
            width = 8
        l = tk.Label(self, relief=tk.GROOVE, width=width, text=name)
        # Create tooltip
        self.toolTip = tooltip.ToolTip(l, text=self.tooltip_name)
        l.bind('<Enter>', self.enter)
        l.bind('<Leave>', self.leave)
        l.pack()

    def enter(self, event):
        self.toolTip.showtip()

    def leave(self, event):
        self.toolTip.hidetip()


##########################################################

# The following code is added to facilitate the Scrolled widgets you specified.
class AutoScroll(object):
    '''Configure the scrollbars for a widget.'''
    def __init__(self, master):
        #  Rozen. Added the try-except clauses so that this class
        #  could be used for scrolled entry widget for which vertical
        #  scrolling is not supported. 5/7/14.
        try:
            vsb = ttk.Scrollbar(master, orient='vertical', command=self.yview)
        except:
            pass
        hsb = ttk.Scrollbar(master, orient='horizontal', command=self.xview)
        try:
            self.configure(yscrollcommand=self._autoscroll(vsb))
        except:
            pass
        self.configure(xscrollcommand=self._autoscroll(hsb))
        self.grid(column=0, row=0, sticky='nsew')
        try:
            vsb.grid(column=1, row=0, sticky='ns')
        except:
            pass
        hsb.grid(column=0, row=1, sticky='ew')
        master.grid_columnconfigure(0, weight=1)
        master.grid_rowconfigure(0, weight=1)
        # Copy geometry methods of master  (taken from ScrolledText.py)
        methods = tk.Pack.__dict__.keys() | tk.Grid.__dict__.keys() \
                  | tk.Place.__dict__.keys()
        for meth in methods:
            if meth[0] != '_' and meth not in ('config', 'configure'):
                setattr(self, meth, getattr(master, meth))

    @staticmethod
    def _autoscroll(sbar):
        '''Hide and show scrollbar as needed.'''
        def wrapped(first, last):
            first, last = float(first), float(last)
            if first <= 0 and last >= 1:
                sbar.grid_remove()
            else:
                sbar.grid()
            sbar.set(first, last)
        return wrapped

    def __str__(self):
        return str(self.master)

def _create_container(func):
    '''Creates a ttk Frame with a given master, and use this new frame to
    place the scrollbars and the widget.'''
    def wrapped(cls, master, **kw):
        container = ttk.Frame(master)
        container.bind('<Enter>', lambda e: _bound_to_mousewheel(e, container))
        container.bind('<Leave>', lambda e: _unbound_to_mousewheel(e, container))
        return func(cls, container, **kw)
    return wrapped

class ScrolledTreeView(AutoScroll, ttk.Treeview):
    '''A standard ttk Treeview widget with scrollbars that will
    automatically show/hide as needed.'''
    @_create_container
    def __init__(self, master, **kw):
        ttk.Treeview.__init__(self, master, **kw)
        AutoScroll.__init__(self, master)

import platform
def _bound_to_mousewheel(event, widget):
    child = widget.winfo_children()[0]
    if platform.system() == 'Windows' or platform.system() == 'Darwin':
        child.bind_all('<MouseWheel>', lambda e: _on_mousewheel(e, child))
        child.bind_all('<Shift-MouseWheel>', lambda e: _on_shiftmouse(e, child))
    else:
        child.bind_all('<Button-4>', lambda e: _on_mousewheel(e, child))
        child.bind_all('<Button-5>', lambda e: _on_mousewheel(e, child))
        child.bind_all('<Shift-Button-4>', lambda e: _on_shiftmouse(e, child))
        child.bind_all('<Shift-Button-5>', lambda e: _on_shiftmouse(e, child))

def _unbound_to_mousewheel(event, widget):
    if platform.system() == 'Windows' or platform.system() == 'Darwin':
        widget.unbind_all('<MouseWheel>')
        widget.unbind_all('<Shift-MouseWheel>')
    else:
        widget.unbind_all('<Button-4>')
        widget.unbind_all('<Button-5>')
        widget.unbind_all('<Shift-Button-4>')
        widget.unbind_all('<Shift-Button-5>')

def _on_mousewheel(event, widget):
    if platform.system() == 'Windows':
        widget.yview_scroll(-1*int(event.delta/120),'units')
    elif platform.system() == 'Darwin':
        widget.yview_scroll(-1*int(event.delta),'units')
    else:
        if event.num == 4:
            widget.yview_scroll(-1, 'units')
        elif event.num == 5:
            widget.yview_scroll(1, 'units')

def _on_shiftmouse(event, widget):
    if platform.system() == 'Windows':
        widget.xview_scroll(-1*int(event.delta/120), 'units')
    elif platform.system() == 'Darwin':
        widget.xview_scroll(-1*int(event.delta), 'units')
    else:
        if event.num == 4:
            widget.xview_scroll(-1, 'units')
        elif event.num == 5:
            widget.xview_scroll(1, 'units')



class EntryPopup(tk.Entry):

    def __init__(self, parent, iid, text, column_id, field_sizes, **kw):
        ''' If relwidth is set, then width is ignored '''
        super().__init__(parent.main_table, borderwidth=4, background='yellow', **kw)
        self.parent_view = parent
        self.tv = parent.main_table
        self.iid = iid
        self.column_id = column_id
        self.values = text
        self.field_sizes = field_sizes

        self.insert(0, text[column_id-1]) 
        # self['state'] = 'readonly'
        # self['readonlybackground'] = 'white'
        # self['selectbackground'] = '#1BA1E2'
        self['exportselection'] = False

        self.focus_force()
        self.bind("<Return>", self.on_return)
        self.bind("<Control-a>", self.select_all)
        self.bind("<Escape>", lambda *ignore: self.destroy())

    def validate_value(self, v):
        int_val = None
        try:
            v = v.lower()
            if v.startswith('0x'):
                int_val = int(v, 16)
            elif v.startswith('0b'):
                int_val = int(v, 2)
            else:
                int_val = int(v)
        except:
            pass
        return int_val

    def mark_as_error(self):
        self.configure(background='red')

    def on_return(self, event):
        int_value = self.validate_value(self.get())
        if int_value == None:
            self.mark_as_error()
            return
        if self.tv.rows_modified.count(self.iid) == 0:
            self.tv.rows_modified.append(self.iid)
            self.tv.item(self.iid, tags=('MODIFIED',))
            self.tv.tag_configure('MODIFIED', background='yellow')

        values_list = list(self.values)
        int_value = int_value & ((2**self.field_sizes[self.column_id-1])-1)
        int_value_str_hex = fhex(int_value, math.ceil(self.field_sizes[self.column_id-1] / 4))
        values_list[self.column_id-1] = int_value_str_hex
        self.tv.item(self.iid, values=values_list)
        self.parent_view.table_changed(self.iid)
        self.destroy()

    def select_all(self, *ignore):
        ''' Set selection on the whole text '''
        self.selection_range(0, 'end')

        # returns 'break' to interrupt default key-bindings
        return 'break'
