class RxActions():

    def __init__(self, gui_data):
        self._gui_data = gui_data

    def setup(self, mode, pol, latitude, ant_en_v, ant_en_h):
        command = "self._host.chip.rx.setup(__RAP__, '{}', '{}', latitude='{}', ant_en_v={}, ant_en_h={})".format(mode, pol, latitude, ant_en_v, ant_en_h)
        self._gui_data.exec_command(command)

    def rf_gain(self, pol, gain_index):
        command = "self._host.chip.rx.gain(__RAP__, {}, pol='{}', sync=1)".format(gain_index, pol)
        self._gui_data.exec_command(command)

    def beam(self, pol, beam_index):
        command = "self._host.chip.rx.beam(__RAP__, {}, pol='{}', sync=1)".format(beam_index, pol)
        self._gui_data.exec_command(command)

    def dco_calibrate(self, pol, gain_index):
        command = "self._host.chip.rx.dco.calibrate(__RAP__, '{}', {})".format(pol, gain_index)
        self._gui_data.exec_command(command)

    def override(self, dev, state):
        if state == 'On':
            command = "self._host.chip.rx.override_mode(__RAP__, True)"
        else:
            command = "self._host.chip.rx.override_mode(__RAP__, False)"
        self._gui_data.exec_command(command)
