# Just some things I want all page subclasses to have.
import tkinter as tk

class Page(tk.Frame):
    def __init__(self, *args, **kwargs):
        # for name, value in kwargs.items():.
        #    print( '{0} = {1}'.format(name, value)).
        tk.Frame.__init__(self, *args, **kwargs)

    def show(self):
        # print('RAISE').
        self.tkraise()
