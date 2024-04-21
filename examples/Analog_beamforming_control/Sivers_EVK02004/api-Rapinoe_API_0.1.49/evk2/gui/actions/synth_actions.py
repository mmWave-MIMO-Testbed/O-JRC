class SynthActions():

    def __init__(self, gui_data):
        self._gui_data = gui_data

    def setup_set(self, freq_rff, frac_mode, sd_order):
        vcxo_freq = self.ref_clk_setup()
        command = "self._host.chip.synth.setup(__RAP__)"
        self._gui_data.exec_command(command)
        command = "self._host.chip.synth.set(__RAP__, {}, frac_mode={}, sd_order={})".format(freq_rff, frac_mode, sd_order)
        self._gui_data.exec_command(command)
        return vcxo_freq

    def ref_clk_setup(self):
        try:
            command = "self._host.pll.setup()['vcxo_freq']"
            vcxo_freq = self._gui_data.exec_command(command)
            command = "self._host.chip.ref_clk.set(__RAP__, {})".format(vcxo_freq)
            self._gui_data.exec_command(command)
        except:
            vcxo_freq = 245760000
        return vcxo_freq

    def get_rf_freq(self):
        command = "self._host.chip.synth.status(__RAP__)['freq']"
        return self._gui_data.exec_command(command)