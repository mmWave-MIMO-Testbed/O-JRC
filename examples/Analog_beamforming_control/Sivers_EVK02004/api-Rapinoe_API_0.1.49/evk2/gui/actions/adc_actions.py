class AdcActions():

    def __init__(self, gui_data):
        self._gui_data = gui_data

    def enable(self):
        command = "self._host.chip.adc.enable(__RAP__)"
        self._gui_data.exec_command(command)
