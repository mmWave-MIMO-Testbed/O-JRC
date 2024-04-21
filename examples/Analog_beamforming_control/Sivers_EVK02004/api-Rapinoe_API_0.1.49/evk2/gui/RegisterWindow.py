import Page as p
import tkinter as tk
import tkinter.ttk as ttk

import sys
sys.path.insert(0, '..')
sys.path.insert(0, '../')

import ScrolledFrame
import RegFieldView
import tooltip

class RegisterWindow():

    def __init__(self, parent, gui_data, dev, field_frame, *args, **kwargs):
        self.gui_data = gui_data
        self.dev = dev
        self.field_frame = field_frame
        self.SelectedEntry = [None, None, None]
        self.groups = list(self.gui_data.rem_evk.get_reg_groups_keys())
        self.groups.sort()
        self.group_tab = {}
        self.reg_tab_layout = {}
        self.regValueList = {}
        exclude_groups = ['BF_RAM', 'RX_RAM', 'TX_RAM']
        for exclude_group in exclude_groups:
            if exclude_group in self.groups:
                self.groups.remove(exclude_group)

        self.nb = ttk.Notebook(parent)
        for group in self.groups:
            self.group_tab[group] = ScrolledFrame.ScrolledFrame(self.nb)
            self.reg_tab_layout[group] = RegisterTabLayout(self.group_tab[group].interior, dev, group, self, self.field_frame, gui_data)
            self.nb.add(self.group_tab[group], text=group)
             
        self.nb.pack(side="right", fill="both", expand=True)

    def poll(self):
        try:
            for reg in self.reg_tab_layout[self.group].reg_frame:
                self.regValueList[reg] = self.gui_data.read_register(reg)
        except:
            pass

    def updateView(self):
        try:
            self.group = self.nb.tab(self.nb.select(), "text")
            for reg in self.reg_tab_layout[self.group].reg_frame:
                self.reg_tab_layout[self.group].reg_frame[reg].register_value.set(hex(self.regValueList[reg]))
        except KeyError as err:
            #print("KeyError: {0}".format(err))
            pass
        except:
            #print("Something else went wrong")
            pass

    def close(self):
        self.nb.destroy()

class RegisterTabLayout(p.Page):
    def __init__(self, parent, dev, group, regwin, field_frame, gui_data, *args, **kwargs):
        p.Page.__init__(self, parent, *args, **kwargs)
        self.reg_frame = {}
        self.dev = dev
        i = 0
        regs = gui_data.rem_evk.get_reg_groups()[group]
        for reg in regs:
            self.reg_frame[reg] = RegFrame(parent, dev, reg, regwin, field_frame, gui_data)
            self.reg_frame[reg].grid(row=i, column=0, sticky="nsew")
            i = i + 1


class RegFrame(p.Page):
    def __init__(self, parent, dev, register_name, regwin, field_frame, gui_data, *args, **kwargs):
        p.Page.__init__(self, parent, *args, **kwargs)
        self.gui_data = gui_data
        self.dev = dev
        self.name = register_name
        self.regwin = regwin
        self.field_frame = field_frame
        self.register_value = tk.StringVar()
        self.reg_name_label = tk.Label(self, text=register_name, anchor="w", width=20)
        self.reg_name_label.bind('<Button-1>', self.enterKeyPressedEditMode)
        self.value_label = tk.Label(self, textvariable=self.register_value, anchor="e", width=12)
        self.value_label.bind('<Button-1>', self.enterKeyPressedEditMode)
        self.hex_entry_value = tk.StringVar()
        self.entry = tk.Entry(self, textvariable=self.hex_entry_value, width=14)
        self.entry.bind('<Return>', self.enterKeyPressed)
        self.entry.bind("<Enter>", self.entry_select_callback)
        self.entry.bind('<Button-1>', self.enterKeyPressed)
        self.reg_name_label.pack(side="left",  fill="both")
        self.value_label.pack(side="right")
        self.register_value.set(hex(gui_data.read_register(register_name)))
        # Create tooltip
        register_desc = gui_data.rem_evk.get_register_attribs(register_name)['desc']
        self.toolTip = tooltip.ToolTip(self.reg_name_label, register_desc)
        self.reg_name_label.bind('<Enter>', self.enter)
        self.reg_name_label.bind('<Leave>', self.leave)

    def enter(self, event):
        self.toolTip.showtip()

    def leave(self, event):
        self.toolTip.hidetip()

    def enterKeyPressedEditMode(self, event):
        if (self.regwin.SelectedEntry[0] != None) and (self.regwin.SelectedEntry[0] != self.entry):
            self.regwin.SelectedEntry[0].pack_forget()
            self.regwin.SelectedEntry[1].pack(side="right")
        try:
            self.regwin.SelectedEntry[2].close()
        except:
            pass
        self.regwin.SelectedEntry = [self.entry, self.value_label]
        self.value_label.pack_forget()
        self.entry.pack(side="right")
        self.hex_entry_value.set(self.register_value.get())
        self.regfield = RegFieldView.RegFieldView(self.field_frame, self.value_changed_externally, self.gui_data, self.dev, self.name)
        self.value_changed = False
        self.regwin.SelectedEntry = [self.entry, self.value_label, self.regfield]

    def value_changed_externally(self):
        self.value_changed = True

    def enterKeyPressed(self, event):
        if not self.value_changed:
            self.updateValue()
        self.entry.pack_forget()
        self.regfield.close()
        self.value_label.pack(side="right")

    def updateValue(self):
        value_str = self.hex_entry_value.get()
        if ('0x' in value_str) or ('0X' in value_str):
            # Hex
            try:
                value = int(value_str, 16)
            except:
                return
        else:
            # Dec
            try:
                value = int(value_str, 10)
            except:
                return

        self.gui_data.write_register(self.name, value)
        self.regwin.regValueList[self.name] = value
        self.register_value.set(hex(value))

    def entry_select_callback(self, event):
        self.entry.icursor(tk.END)
        self.entry.focus()
