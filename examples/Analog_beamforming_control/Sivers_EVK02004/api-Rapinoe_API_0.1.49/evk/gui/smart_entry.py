import tkinter as tk

class SmartEntry(tk.Entry):
    def __init__(self, *args, **kwargs):
        self.modified = False
        self.change_color = True
        self.value_changed_callback = None
        self.str_val = tk.StringVar()
        tk.Entry.__init__(self, *args, **kwargs, textvariable=self.str_val)

    def change_bg_color(self, color):
        self.configure(bg=color)

    def set_value_changed_callback(self, value_changed_callback):
        self.value_changed_callback = value_changed_callback

    def set_value(self, value, change_color=True):
        self.change_color = change_color
        self.str_val.set(value)
        self.change_color = True

    def get_value_int(self):
        int_val = None
        try:
            v = self.str_val.get().lower()
            if v.startswith('0x'):
                int_val = int(self.str_val.get(), 16)
            elif v.startswith('0b'):
                int_val = int(self.str_val.get(), 2)
            else:
                int_val = int(self.str_val.get())
        except:
            pass
        return int_val

    def reset_value_changed(self):
        self.change_bg_color('white')
        self.modified = False

    def mark_error(self):
        self.change_bg_color('red')

    def value_changed(self):
        if self.change_color:
            self.change_bg_color('yellow')
            self.modified = True
        if self.value_changed_callback != None:
            if self.change_color:
                self.value_changed_callback()

    def enable_value_trace(self):
        def callback(var, index, mode):
            self.value_changed()

        self.str_val.trace_add("write", callback)


