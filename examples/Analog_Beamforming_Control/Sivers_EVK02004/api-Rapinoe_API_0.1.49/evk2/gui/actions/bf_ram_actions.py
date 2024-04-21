class BfRamActions():

    def __init__(self, gui_data):
        self._gui_data = gui_data

    def get_beam_index(self, path):
        command = "self._host.chip.adc.enable(__RAP__)"
        self._gui_data.exec_command(command)
