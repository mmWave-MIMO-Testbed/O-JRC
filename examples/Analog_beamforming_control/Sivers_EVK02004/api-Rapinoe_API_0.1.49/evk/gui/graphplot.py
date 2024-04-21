from sre_compile import isstring
import tkinter as tk
from matplotlib import pyplot as plt
from matplotlib import animation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib import rcParams
rcParams.update({'figure.autolayout': True})
from matplotlib import style
import evk.gui.Variables as var
from threading import Lock


class PlotFrame(tk.Frame):
    def __init__(self, parent, gui_handler, dev, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.gui_handler = gui_handler
        self.dev = dev
        self.TH = gui_handler.TH
        self.dev_temp_data = [0]*var._LIST_LENGTH
        plot_color = "blue"
        self.xdata = list(range(var._LIST_LENGTH))
        #print (style.available)
        try:
            style.use('bmh')
        except:
            style.use('ggplot')

        self.dev_temperature = 0
        self.lock = Lock()

        # Chip Temp
        self.chipFig = plt.figure()
        self.chipFig.set_size_inches(4, 1.5)
        self.chipTempAx = self.chipFig.add_subplot(1,1,1)
        self.chipTempAx.set_title('Temperature (°C)', fontsize=var._FONTSIZE)
        self.chipTempAx.yaxis.set_label_coords(0,1.00)
        self.chipTempAx.set_xticklabels([])
        self.temp_line, = self.chipTempAx.plot(self.xdata, self.dev_temp_data, color=plot_color, linewidth=2.0)
        #plt.legend(loc=2, fontsize=var._FONTSIZE)

        for label in self.chipTempAx.get_yticklabels():
            label.set_fontsize(var._FONTSIZE)

        self.canvas = FigureCanvasTkAgg(self.chipFig, master=self)
        self.canvas.get_tk_widget().pack(side="left",fill="x", expand=True)

        #plt.legend(loc=2, fontsize=var._FONTSIZE)

        self.ybottom = -1
        self.ytop = 30
        self.ymargin = 10
        self.paused = True

        #self.bind("<Configure>", self._resize)

    def _resize(self, event):
        #print (self, 'RESIZE', event.height)
        size = self.chipFig.get_size_inches()
        self.chipFig.set_size_inches(size[0], 1)

    def enable_graph(self, enable):
        if not enable:
            self.anim.event_source.stop()
        else:
            self.anim.event_source.start()
            self.paused = False

    def set_temperature_src(self, src):
        self.temperature_src = src
        self.dev_temp_data = [0]*var._LIST_LENGTH

    def _readForPlotChip(self, src):
        #if isstring(src):
            #src = src.split()
            #src = src[len(src)-1]
        self.dev_temperature = self.gui_handler.gd[self.dev.get_name()].read_temperature(src)
        return self.dev_temperature

    def _shift_dev_temp_data(self):
        self.dev_temp_data = self.dev_temp_data[-var._LIST_LENGTH+1:]

    def startPlotThread(self):
        self.anim = animation.FuncAnimation(self.chipFig, self.animate_dev_temp, cache_frame_data=False, interval=var._GRAPHUPDATEDELAY)

    def animate_dev_temp(self, i=0):
        if self.paused:
            return
        try:
            self._shift_dev_temp_data()
            read_temp = self.dev_temperature
            self.dev_temp_data.append(read_temp)
            self.temp_line.set_ydata(self.dev_temp_data)

            if read_temp > var._REDTEMPERATURE:
                self.font_color = 'red'
                self.temp_line.set_color('red')
            else:
                self.font_color = 'black'
                self.temp_line.set_color('blue')

            self.ytop = max(self.dev_temp_data) + self.ymargin
            self.ybottom = min(self.dev_temp_data) - self.ymargin

            self.chipTempAx.set_ylim(self.ybottom, self.ytop)
            self.chipTempAx.set_title(str(self.temperature_src) + ' ( {} °C )'.format(round(read_temp)), loc='center', color=self.font_color, fontsize=var._FONTSIZE)
        except:
            #print ('*')
            pass

        self.TH.put(lambda : self._readForPlotChip(self.temperature_src))

    def close(self):
        try:
            self.anim.event_source.stop()
        except:
            pass
        plt.close()
