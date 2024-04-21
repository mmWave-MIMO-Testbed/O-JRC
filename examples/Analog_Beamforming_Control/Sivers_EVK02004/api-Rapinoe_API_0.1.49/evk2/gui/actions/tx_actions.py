class TxActions():

    def __init__(self, gui_data):
        self._gui_data = gui_data

    def setup(self, mode, pol, latitude, ant_en_v, ant_en_h):
        command = "self._host.chip.tx.setup(__RAP__, '{}', '{}', latitude='{}', ant_en_v={}, ant_en_h={})".format(mode, pol, latitude, ant_en_v, ant_en_h)
        self._gui_data.exec_command(command)
        

    def bb_gain(self, bb_v, bb_h):
        command = "self._host.chip.tx.gain_bb(__RAP__, {}, {})".format(bb_v, bb_h)
        self._gui_data.exec_command(command)

    def rf_gain(self, pol, gain_index):
        command = "self._host.chip.tx.gain_rf(__RAP__, {}, pol='{}', sync=1)".format(gain_index, pol)
        self._gui_data.exec_command(command)
        
    def beam(self, pol, beam_index):
        command = "self._host.chip.tx.beam(__RAP__, {}, pol='{}', sync=1)".format(beam_index, pol)
        self._gui_data.exec_command(command)

    def dco_calibrate(self, mode, tx_pol, cross_pol):
        if tx_pol == 'TV':
            tx_pol = 'V'
        else:
            tx_pol = 'H'

        if cross_pol == 'Yes':
            cross_pol = True
        else:
            cross_pol = False
        command = "self._host.chip.tx.dco.calibrate(__RAP__, '{}', '{}', {})".format(mode, tx_pol, cross_pol)
        self._gui_data.exec_command(command)

    def override(self, dev, state):
        if state == 'On':
            command = "self._host.chip.tx.override_mode(__RAP__, True)"
        else:
            command = "self._host.chip.tx.override_mode(__RAP__, False)"
        self._gui_data.exec_command(command)
