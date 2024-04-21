import evk.gui.Page as p
import tkinter as tk
import tkinter.ttk as ttk

import evk.gui.Variables as var
from common import fhex

class RegFieldView():

    def __init__(self, parent, update_callback, host, dev, reg, wr_button_text='Write changes', rd_button_text=None, *args, **kwargs):
        self.host = host
        self.dev = dev
        self.reg = reg
        self.update_callback = update_callback
        self.field_view = []


        self.fieldbox = p.Page(parent, borderwidth=2, relief=tk.RIDGE, pady=10)
        reg_name_label = tk.Label(self.fieldbox, text=reg+'\n', font=("Ariel", 15))
        reg_name_label.pack(side="top")
        for field in self.host.spi.register_map.reg_map[reg].keys():
            self.field_view.append(FieldView(self.fieldbox, self.update_callback, host, dev, reg, field, owner=self))

        separator = ttk.Separator(self.fieldbox, orient='horizontal')
        # Read button
        if rd_button_text != None:
            self.read_button = tk.Button(self.fieldbox, text=rd_button_text, command=self.read_reg_value)

        self.fieldbox.pack(side="left", anchor="nw", fill="x", expand=True)
        separator.pack(fill='x', pady=8)
        if rd_button_text != None:
            self.read_button.pack()
        # Write button
        if wr_button_text != None:
            self.write_button = tk.Button(self.fieldbox, text=wr_button_text, command=self.write_reg_value)

        self.fieldbox.pack(side="left", anchor="nw", fill="x", expand=True)
        separator.pack(fill='x', pady=8)
        if wr_button_text != None:
            self.write_button.pack()

    def field_value_changed(self):
        try:
            self.write_button.configure(fg='red')
        except:
            pass

    def write_reg_value(self):
        for i in range(len(self.field_view)):
            self.field_view[i].write_new_value(None)
        try:
            self.write_button.configure(fg='green')
        except:
            pass

    def read_reg_value(self):
        for i in range(len(self.field_view)):
            self.field_view[i].read_reg_value()
        try:
            self.write_button.configure(fg='black')
        except:
            pass

    def hide(self):
        self.fieldbox.pack_forget()

    def show(self):
        self.fieldbox.pack()

    def close(self):
        self.fieldbox.destroy()

class FieldView():

    def __init__(self, parent, update_callback, host, dev, reg, field, *args, **kwargs):
        self.host = host
        self.dev = dev
        self.reg = reg
        self.field = field
        self.owner = kwargs['owner']
        self.update_callback = update_callback
        field_row = p.Page(parent)
        field_label = tk.Label(field_row, text=field)

        field_bit_label_text = str(self.host.spi.register_map.reg_map[reg][field])
        field_bit_label = tk.Label(field_row, text=field_bit_label_text)

        self.mask = 0
        for bit in range(self.host.spi.register_map.reg_map[reg][field]['Lsb'], self.host.spi.register_map.reg_map[reg][field]['Msb']+1):
            self.mask = self.mask + (1 << bit)

        self.current_value = (self.host.gui_handler.gd[self.dev.get_name()].read_register(self.reg) & self.mask) >> self.host.spi.register_map.reg_map[reg][field]['Lsb']

        self.field_value = tk.StringVar()

        def on_filed_value_changed(field_value):
            self.owner.field_value_changed()
        self.field_value.trace('w', lambda *_, field_value=self.field_value: on_filed_value_changed(field_value))


        self.num_of_bits = self.host.spi.register_map.reg_map[reg][field]['Msb'] - self.host.spi.register_map.reg_map[reg][field]['Lsb'] + 1
        self.num_of_digits = self.num_of_bits // 4
        self.field_value.set(fhex(self.current_value, self.num_of_digits))
        self.filed_value_entry = tk.Entry(field_row, textvariable=self.field_value, justify=tk.RIGHT)
        field_label.pack(side="left")
        self.filed_value_entry.pack(side="right", padx=4)
        field_bit_label.pack(side="right")
        field_row.pack(side="top", fill="x")
        self.filed_value_entry.bind('<Return>', self.write_new_value)
        self.filed_value_entry.bind('<Up>', self.up_arrow_pressed)
        self.filed_value_entry.bind('<Down>', self.down_arrow_pressed)

    def up_arrow_pressed(self, event):
        value = self.get_entry_value()
        value = value + 1
        self.field_value.set(fhex(value, self.num_of_digits))

    def down_arrow_pressed(self, event):
        value = self.get_entry_value()
        if value > 0:
            value = value - 1
        self.field_value.set(fhex(value, self.num_of_digits))

    def get_entry_value(self):
        entry_val = self.field_value.get().lower()
        if (entry_val.startswith('0x')):
            # Hex value
            entry_val = entry_val.replace('x', '')
            try:
                dec_entry_val = int(entry_val, 16)
            except ValueError:
                return None
        elif (entry_val.startswith('0b')):
            # Binary value
            entry_val = entry_val.replace('b', '')
            try:
                dec_entry_val = int(entry_val, 2)
            except ValueError:
                return None
        else:
            # Decimal
            try:
                dec_entry_val = int(entry_val, 10)
            except ValueError:
                return None

        return dec_entry_val

    def validate_new_value(self, value):
        if value > (2 ** self.num_of_bits) -1 :
            return False
        return True

    def write_new_value(self, event):
        entry_value = self.get_entry_value()
        if entry_value == None or not self.validate_new_value(entry_value):
            self.filed_value_entry.configure(bg='red')
            return
        else:
            self.filed_value_entry.configure(bg='white')
        if entry_value != self.current_value:
            #if not self.update_callback == None:
            #    self.update_callback()
            # Register value should be updated
            self.current_value = entry_value
            value = {self.field: entry_value}
            if 'ram' in self.reg:
                if isinstance(value, dict):
                    row_data = self.host.gui_handler.gd[self.dev.get_name()].read_ram(self.reg, self.owner.row)
                    data_pos = self.host.spi.register_map.reg_map[self.reg][list(value)[0]]['Lsb']
                    data_size = self.host.spi.register_map.reg_map[self.reg][list(value)[0]]['Msb'] - data_pos + 1
                    val = value[list(value)[0]] << data_pos
                    val_mask = ~((2**data_size-1) << data_pos)
                    value = (row_data & val_mask) | val

                self.host.gui_handler.gd[self.dev.get_name()].write_ram(self.reg, self.owner.row, value)
            else:
                self.host.gui_handler.gd[self.dev.get_name()].write_register(self.reg, value)
            if not self.update_callback == None:
                self.update_callback()

    def read_reg_value(self):
        if 'ram' in self.reg:
            self.current_value = (self.host.gui_handler.gd[self.dev.get_name()].read_ram(self.reg, self.owner.row) & self.mask) >> self.host.spi.register_map.reg_map[self.reg][self.field]['Lsb']
        else:
            self.current_value = (self.host.gui_handler.gd[self.dev.get_name()].read_register(self.reg) & self.mask) >> self.host.spi.register_map.reg_map[self.reg][self.field]['Lsb']
        self.field_value.set(fhex(self.current_value, self.num_of_digits))
