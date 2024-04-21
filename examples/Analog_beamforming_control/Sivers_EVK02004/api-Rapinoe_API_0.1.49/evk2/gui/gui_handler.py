import tkinter as tk

import viewNotebook
import gui_data
import FuncThread as FT
import ThreadHandler as TH

class GuiHandler(object):

    def __init__(self, host):
        self.host = host
        self.root = tk.Tk()
        self.root.protocol('WM_DELETE_WINDOW', self.close)
        self.root.withdraw()
        self.gd = {}

    def start_gui(self, dev, extended=False):
        viewNotebook.start_gui(dev, extended)

    def close(self):
        self.TH.stop()
        self.root.destroy()
