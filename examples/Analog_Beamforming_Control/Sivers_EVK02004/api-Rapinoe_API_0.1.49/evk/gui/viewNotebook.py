'''
A GUI for controlling registers
'''
__author__= "Pontus Brink"

import sys
import os

import tkinter as tk
import tkinter.ttk as ttk
from tkinter.filedialog import asksaveasfilename
from tkinter.filedialog import askopenfilename

import evk_logger
import version
from shutil import copyfile
import time
import evk.gui.Variables as var
import evk.gui.Page as p
import evk.gui.RegisterWindow
import evk.gui.graphplot
import evk.gui.AdcWindow
import evk.gui.TxRamWindow
import evk.gui.RxRamWindow
import evk.gui.BfRamWindow
import evk.gui.TxRxWindow
import evk.gui.GainView
import evk.gui.DemoView
import evk.gui.FuncThread as FT
import evk.gui.ThreadHandler as TH

INITIAL_POLL_DELAY  = 800
LONG_POLL_DELAY     = 1100 #1600
SHORT_POLL_DELAY    = 3000 #1000
GUI_UPDATE_INTERVALL = 1

# This class controls the entire program.
class MainView(tk.Frame):
    def __init__(self, gui_handler, dev, extended=False, *args, **kwargs):
        tk.Frame.__init__(self,*args,**kwargs)
        self.parent = gui_handler.root
        self.gui_handler = gui_handler
        self.dev = dev
        self.top = tk.Toplevel(self.parent)
        w = 1280 # width for the Tk root
        h = 1000 # height for the Tk root

        # get screen width and height
        ws = self.top.winfo_screenwidth() # width of the screen
        hs = self.top.winfo_screenheight() # height of the screen

        # calculate x and y coordinates for the Tk root window
        x = (ws/2) - (w/2)
        y = (hs/2) - (h/2)

        # set the dimensions of the screen
        # and where it is placed
        self.top.geometry('%dx%d+%d+%d' % (w, hs*0.7, x, y))
        # Set main window minimum size
        self.top.minsize(w, h)

        self.top.withdraw()
        self.top.protocol('WM_DELETE_WINDOW', self.close)
        try:
            self.top.iconbitmap('evk/gui/images/sivers.ico')
        except:
            iconphoto = tk.PhotoImage(file = "evk/gui/images/sivers.png")
            self.top.iconphoto(False, iconphoto)

        ################################################
        self.TH = TH.ThreadHandler()
        self.queueThread = FT.FuncThread(lambda:self.TH.start()) # DOESNT STOP???
        self.queueThread.daemon = True
        self.queueThread.start()
        gui_handler.TH = self.TH
        ################################################

        self.quit_mainview = False
        self.version    = version.Version().get_version()

        # Siversima logo
        self.logoPage = p.Page(self.top, background=var._BACKGROUND)
        verLabel = tk.Label(self.logoPage, fg='white', text="v" + self.version, background=var._BACKGROUND)
        verLabel.pack(side="right", anchor="ne")
        logo = PictureShower(self.logoPage,"evk/gui/images/SiversLogo.gif")

        self.top.title(var._EVKNAME + ' ' + self.dev.get_name())

        self.menuBarSetup()

        tab_frame = p.Page(self.top)
        self.temp_frame = p.Page(self.top)

        self.nb = ttk.Notebook(tab_frame)

        # Demo tab
        if extended:
            self.demoTabSetup()

        # TX / RX tab content
        self.txrxTabSetup()

        self.rxGainTabSetup()
        self.txGainTabSetup()

        RegsPage = p.Page(self.nb)
        self.nb.add(RegsPage, text="Registers")
        RegsListPage = p.Page(RegsPage)
        RegFieldPage = p.Page(RegsPage)
        RegsListPage.pack(side="left", anchor="nw", fill="y")
        RegFieldPage.pack(side="left")

        AdcPage = p.Page(self.nb)
        self.nb.add(AdcPage, text="ADC")

        if False:
            AmuxSrcPage = p.Page(self.nb)
            self.nb.add(AmuxSrcPage, text="Amux src readings")

            RxPage = p.Page(self.nb)
            self.nb.add(RxPage, text="RX")

            TxPage = p.Page(self.nb)
            self.nb.add(TxPage, text="TX")

        self.adcwin = evk.gui.AdcWindow.AdcWindow(AdcPage, gui_handler, dev)

        # Register tab content
        self.regwin = evk.gui.RegisterWindow.RegisterWindow(RegsListPage, gui_handler, dev, RegFieldPage)

        # Temperature tab content
        self.temp_sources = list(self.gui_handler.host.chip.temp.src)
        self.tempTabSetup()
        self.mainTempSetup()
        if extended:
            self.txRamTabSetup()
            self.rxRamTabSetup()
        self.bfRamTabSetup()

        # Pack it up.
        self.logoPage.pack(side="top", fill="x", anchor="n")
        self.temp_src_menu.pack(side="left", anchor="nw", fill="none",expand=False)
        self.main_temp_selector_check.pack(side="left", anchor="nw", fill="none",expand=False)
        self.nb.pack(side="top",fill="both", expand=True)

        tab_frame.pack(side="top", fill='both', anchor="nw", expand=True)
        self.temp_frame.pack(side="bottom", fill='x', anchor="nw")

        self.nb.bind('<<NotebookTabChanged>>', self._on_tab_change)
        self.grapher.startPlotThread()
        self.top.after(INITIAL_POLL_DELAY, self.PollStarter)
        self.top.deiconify()
        self.nb.select(2)
        self.busy = False

    def set_busy(self, busy):
        self.busy = busy

    def _on_tab_change(self, event):
        tab = event.widget.tab('current')['text']
        if tab == 'TX_RAM':
            self.txRamWindow.refresh()
        elif tab == 'Demo':
            self.demoWindow._update()
        elif tab == 'TX RAM':
            self.txRamWindow.txRamTableView.read_ram()

    def save_register_settings(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        dir_path = dir_path + '\\..\\..\\config\\saved'
        try:
            os.makedirs(dir_path)
        except FileExistsError:
            pass
        files = [('CSV files', '*.csv'), ('All Files', '*.*')]
        file_name = asksaveasfilename(filetypes = files, defaultextension = files, initialdir=dir_path)
        if file_name != '':
            self.gui_handler.host.spi.reg_state(self.dev, save_csv=True, csv_file_name=file_name)

    def load_register_settings(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        dir_path = dir_path + '\\..\\..\\config\\saved'
        try:
            os.makedirs(dir_path)
        except FileExistsError:
            pass
        files = [('CSV files', '*.csv'), ('All Files', '*.*')]
        file_name = askopenfilename(filetypes = files, defaultextension = files, initialdir=dir_path)
        if file_name != '':
            self.gui_handler.host.spi.reg_state_wr(self.dev, csv_file_name=file_name)

    def menuBarSetup(self):
        self.menubar = tk.Menu(self.top, font="TkMenuFont")
        self.top.configure(menu = self.menubar)
        self.sub_menu = tk.Menu(self.top,
                activebackground="beige",
                activeborderwidth=1,
                activeforeground="#000000",
                background="#d9d9d9",
                borderwidth=1,
                disabledforeground="#a3a3a3",
                foreground="#000000",
                tearoff=0)
        self.menubar.add_cascade(menu=self.sub_menu,
                compound="left",
                label="Register save/load")
        self.sub_menu.add_command(
                command=self.save_register_settings,
                compound="left",
                label="Save to CSV")
        self.sub_menu.add_command(
                command=self.load_register_settings,
                compound="left",
                label="Load from CSV")

    def txRamTabSetup(self):
        txRamPage = p.Page(self.nb)
        self.txRamWindow = evk.gui.TxRamWindow.TxRamWindow(txRamPage, self.gui_handler, self.dev)
        self.nb.add(txRamPage, text="TX RAM")

    def rxRamTabSetup(self):
        rxRamPage = p.Page(self.nb)
        self.rxRamWindow = evk.gui.RxRamWindow.RxRamWindow(rxRamPage, self.gui_handler, self.dev)
        self.nb.add(rxRamPage, text="RX RAM")

    def bfRamTabSetup(self):
        bfRamPage = p.Page(self.nb)
        self.bfRamWindow = evk.gui.BfRamWindow.BfRamWindow(bfRamPage, self.gui_handler, self.dev)
        self.nb.add(bfRamPage, text="BF RAM")

    def demoTabSetup(self):
        demoPage = p.Page(self.nb)
        self.demoWindow = evk.gui.DemoView.DemoView(demoPage, self.gui_handler, self.dev)
        self.nb.add(demoPage, text="Demo")

    def txrxTabSetup(self):
        txrxPage = p.Page(self.nb)
        self.txrxWindow = evk.gui.TxRxWindow.TxRxWindow(txrxPage, self.gui_handler, self.dev, self)
        self.nb.add(txrxPage, text="Main")

    def rxGainTabSetup(self):
        rxGainPage = p.Page(self.nb)
        self.rxGainWindow = evk.gui.GainView.GainView(rxGainPage, self.gui_handler, self.dev, 'RX')
        self.nb.add(rxGainPage, text="RX Gain")

    def txGainTabSetup(self):
        txGainPage = p.Page(self.nb)
        self.txGainWindow = evk.gui.GainView.GainView(txGainPage, self.gui_handler, self.dev, 'TX')
        self.nb.add(txGainPage, text="TX Gain")


    def mainTempSetup(self):
        main_temp_ctrl_frame = p.Page(self.temp_frame)
        main_temp_plot_frame = p.Page(self.temp_frame)

        # Graph plotter.
        self.grapher = evk.gui.graphplot.PlotFrame(main_temp_plot_frame, self.gui_handler, self.dev)

        # Temperatue source menu
        def temp_src_selected(*args):
            self.grapher.set_temperature_src(args[0])

        self.selected_temp_src = tk.StringVar()
        self.temp_src_menu = tk.OptionMenu(main_temp_ctrl_frame, self.selected_temp_src, *self.temp_sources, command=temp_src_selected)
        if list(self.gui_handler.host.chip.temp.src)[-1] == 'BG':
            self.selected_temp_src.set(self.temp_sources[-1])
            temp_src_selected((self.temp_sources[-1]))
        else:
            self.selected_temp_src.set(self.temp_sources[0])
            temp_src_selected((self.temp_sources[0]))
        self.main_temp_check = tk.IntVar()
        self.main_temp_check.set(0)
        self.main_temp_selector_check = tk.Checkbutton(main_temp_ctrl_frame, text='Poll temperature', variable=self.main_temp_check, command=self.temp_src_selector_changed)

        self.temp_src_menu.pack(side="left", anchor="nw", fill="none",expand=False)
        self.main_temp_selector_check.pack(side="left", anchor="nw", fill="none",expand=False)
        self.grapher.pack(side="bottom", fill="x", expand=True)
        main_temp_ctrl_frame.pack(side='top', fill='x')
        main_temp_plot_frame.pack(side='bottom', fill='x')

    def temp_src_selector_changed(self, *args):
        if len(args) == 1:
            self.temp_grapher[args[0]].enable_graph(self.temp_selector_check[args[0]].get())
        else:
            self.grapher.enable_graph(self.main_temp_check.get())

    def adc_enable_selector_changed(self, *args):
        pass


    def tempTabSetup(self):
        TempPage = p.Page(self.nb)
        self.nb.add(TempPage, text="Temperature")
        NUMBER_OF_TEMP_PLOTS = 8

        TempSelectorRow = p.Page(TempPage)
        self.temp_selector = [None]*NUMBER_OF_TEMP_PLOTS
        self.temp_selector_check = [None]*NUMBER_OF_TEMP_PLOTS
        for i in range(NUMBER_OF_TEMP_PLOTS):
            self.temp_selector_check[i] = tk.IntVar()
            self.temp_selector_check[i].set(0)
            self.temp_selector[i] = tk.Checkbutton(TempSelectorRow, text=list(self.gui_handler.host.chip.temp.src)[i], variable=self.temp_selector_check[i])
            self.temp_selector[i].pack(side="left", anchor="nw", fill="both", expand=True)

        self.temp_selector[0].configure(command=lambda: self.temp_src_selector_changed(0))
        self.temp_selector[1].configure(command=lambda: self.temp_src_selector_changed(1))
        self.temp_selector[2].configure(command=lambda: self.temp_src_selector_changed(2))
        self.temp_selector[3].configure(command=lambda: self.temp_src_selector_changed(3))
        self.temp_selector[4].configure(command=lambda: self.temp_src_selector_changed(4))
        self.temp_selector[5].configure(command=lambda: self.temp_src_selector_changed(5))
        self.temp_selector[6].configure(command=lambda: self.temp_src_selector_changed(6))
        self.temp_selector[7].configure(command=lambda: self.temp_src_selector_changed(7))

        TempRow0 = p.Page(TempPage)
        TempRow1 = p.Page(TempPage)
        TempRow2 = p.Page(TempPage)
        TempRow3 = p.Page(TempPage)

        self.temp_grapher = [None]*NUMBER_OF_TEMP_PLOTS
        for temp_plot_num in range(NUMBER_OF_TEMP_PLOTS):
            if temp_plot_num <= 1:
                temp_row = TempRow0
            elif temp_plot_num <= 3:
                temp_row = TempRow1
            elif temp_plot_num <= 5:
                temp_row = TempRow2
            else:
                temp_row = TempRow3
            self.temp_grapher[temp_plot_num] = evk.gui.graphplot.PlotFrame(temp_row, self.gui_handler, self.dev)
            self.temp_grapher[temp_plot_num].set_temperature_src((self.temp_sources[temp_plot_num]))
            self.temp_grapher[temp_plot_num].pack(side="left", anchor="nw", fill="both", expand=True)

        TempSelectorRow.pack(side="top", anchor="nw", fill="both", expand=True)
        TempRow0.pack(side="top", anchor="nw", fill="both", expand=True)
        TempRow1.pack(side="top", anchor="nw", fill="both", expand=True)
        TempRow2.pack(side="top", anchor="nw", fill="both", expand=True)
        TempRow3.pack(side="top", anchor="nw", fill="both", expand=True)
        for temp_plot_num in range(NUMBER_OF_TEMP_PLOTS):
            self.temp_grapher[temp_plot_num].startPlotThread()

    def __del__(self):
            self.after_cancel(self.pollstarter_id)

    def _update_gui(self):
        _update_gui(self)
        if self.quit_mainview:
            return
        self.parent.after(GUI_UPDATE_INTERVALL, self._update_gui)

    def PollStarter(self):
        _update(self)
        if self.quit_mainview:
            return
        try:
            self.group = self.nb.tab(self.nb.select(), "text")
        except:
            print('*****!!!!!*****')
            self.pollstarter_id = self.parent.after(SHORT_POLL_DELAY, self.PollStarter)
            return

        self.pollstarter_id = self.parent.after(SHORT_POLL_DELAY, self.PollStarter)

    def close(self):
        if self.pollstarter_id is not None:
            self.parent.after_cancel(self.pollstarter_id)
            self.pollstarter_id = None

        self.top.withdraw()

        self.grapher.close()
        self.temp_grapher[0].close()
        self.temp_grapher[1].close()
        self.temp_grapher[2].close()
        self.temp_grapher[3].close()
        self.temp_grapher[4].close()
        self.temp_grapher[5].close()

        try:
            self.nb.destroy()
        except:
            pass

        try:
            self.TH.stop()
        except:
            pass

        self.regwin.close()

        try:
            self.adcwin.close()
        except:
            pass

        ##print "Thread joined!!!", self.TH
        ##self.grapher.ani.event_source.stop()
        self.quit_mainview = True
        ##print "All things stopped", self.queueThread
        ##time.sleep(1000)
        #
        ## Destroy each nb in the notebook.

        #
        try:
            self.menubar.destroy()
        except:
            pass

        #self.root.quit()
        #self.master.destroy()
        self.top.quit()
        self.top.destroy()

class PictureShower(p.Page):
    def __init__(self, parent, photoLocation, *args, **kwargs):
        p.Page.__init__(self,parent,*args,**kwargs)
        # Picture
        photo = tk.PhotoImage(file=photoLocation)
        self.label = tk.Label(parent, bd=0, image=photo, *args, **kwargs)
        self.label.photo=photo
        self.label.pack(side='left')

def _update(app):
    _update_gui(app)
    #evk_logger.evk_logger.set_max_call_log_level(-1)
    #app.gui_handler.gd[app.dev.get_name()]._read_all_groups()
    try:
        app.gui_handler.gd[app.dev.get_name()]._update_register_group_data(app.regwin.group)
    except:
        pass
    app.regwin.poll()
    try:
        app.adcwin.poll()
    except:
        pass
    evk_logger.evk_logger.set_max_call_log_level(0)
    app.regwin.updateView()

def _update_gui(app):
    app.update_idletasks()
    app.update()

def startApp(gui_handler, dev, extended=False):
    app=MainView(gui_handler, dev, extended)
    app.pack(side="top", fill="both", expand=True)
    app.update()
    app.nb.select(0)
    #app.mainloop()


def start_gui(gui_handler, dev, extended=False):
    root = gui_handler.root

    w = 1100 # width for the Tk root
    h = 500 # height for the Tk root

    # get screen width and height
    ws = root.winfo_screenwidth() # width of the screen
    hs = root.winfo_screenheight() # height of the screen

    # calculate x and y coordinates for the Tk root window
    x = (ws/2) - (w/2)
    y = (hs/2) - (h/2)

    # set the dimensions of the screen
    # and where it is placed
    #root.geometry('%dx%d+%d+%d' % (w, h, x, y))
    root.geometry('%dx%d+%d+%d' % (w, hs*0.5, x, y))
    # Set main window minimum size
    #root.update()
    root.minsize(root.winfo_width(), root.winfo_height())
    
    startApp(gui_handler, dev, extended)



