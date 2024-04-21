class GainActions():

    def __init__(self, gui_data):
        self._gui_data = gui_data

    def rx_gain(self, index, pol):
        command = "self._host.chip.rx.gain(__RAP__, {}, 'R{}')".format(index, pol.upper())
        self._gui_data.exec_command(command)

    def tx_gain(self, index, pol):
        command = "self._host.chip.tx.gain_rf(__RAP__, {}, 'T{}')".format(index, pol.upper())
        self._gui_data.exec_command(command)
