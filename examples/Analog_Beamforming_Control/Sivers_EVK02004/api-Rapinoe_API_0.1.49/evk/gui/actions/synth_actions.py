class SynthActions():

    def __init__(self, host):
        self._host = host

    def setup_set(self, dev, freq_rff, frac_mode, sd_order):
        vcxo_freq = self.ref_clk_setup(dev)
        self._host.chip.synth.setup(dev, sd_cfg={'sd_order':sd_order})
        self._host.chip.synth.set(dev, freq_rff, frac_mode=frac_mode, sd_order=sd_order)
        return vcxo_freq

    def ref_clk_setup(self, dev):
        try:
            vcxo_freq = self._host.pll.setup()['vcxo_freq']
            self._host.chip.ref_clk.set(dev, vcxo_freq)
        except:
            vcxo_freq = 245760000
        return vcxo_freq

    def get_rf_freq(self, dev):
        return self._host.chip.synth.status(dev)['freq']