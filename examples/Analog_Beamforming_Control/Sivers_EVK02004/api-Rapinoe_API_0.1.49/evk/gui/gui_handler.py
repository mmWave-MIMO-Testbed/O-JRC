import tkinter as tk

from evk.gui import viewNotebook
import evk.gui.gui_data
import evk.gui.FuncThread as FT
import evk.gui.ThreadHandler as TH

class GuiHandler(object):

    def __init__(self, host):
        self.host = host
        self.root = tk.Tk()
        self.root.protocol('WM_DELETE_WINDOW', self.close)
        self.root.withdraw()
        self.gd = {}

    def start_gui(self, devs, extended=False):
        if not isinstance(devs, list):
            devs = [devs]
        for dev in devs:
            if not dev.get_name() in self.gd:
                self.gd[dev.get_name()] = evk.gui.gui_data.GuiData(self, dev)
            viewNotebook.start_gui(self, dev, extended)

    def close(self):
        self.TH.stop()
        self.root.destroy()
