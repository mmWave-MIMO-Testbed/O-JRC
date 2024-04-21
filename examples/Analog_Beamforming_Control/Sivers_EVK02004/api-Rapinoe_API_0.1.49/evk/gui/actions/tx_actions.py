class TxActions():

    def __init__(self, host):
        self._host = host

    def setup(self, dev, mode, pol, latitude, ant_en_v, ant_en_h):
        self._host.chip.tx.setup(dev, mode, pol, latitude=latitude, ant_en_v=ant_en_v, ant_en_h=ant_en_h)

    def bb_gain(self, dev, bb_v, bb_h):
        self._host.chip.tx.gain_bb(dev, bb_v, bb_h)

    def rf_gain(self, dev, pol, gain_index):
        self._host.chip.tx.gain_rf(dev, gain_index, pol=pol, sync=1)

    def beam(self, dev, pol, beam_index):
        self._host.chip.tx.beam(dev, beam_index, pol=pol, sync=1)

    def dco_calibrate(self, dev, mode, tx_pol, cross_pol):
        if tx_pol == 'TV':
            tx_pol = 'V'
        else:
            tx_pol = 'H'

        if cross_pol == 'Yes':
            cross_pol = True
        else:
            cross_pol = False
        self._host.chip.tx.dco.calibrate(dev, mode, tx_pol, cross_pol)

    def pdet_dco_calibrate(self, dev, mode, tx_pol):
        if tx_pol == 'TV':
            tx_pol = 'V'
        else:
            tx_pol = 'H'
        self._host.chip.tx.dco_det.calibrate(dev, mode, tx_pol)

    def override(self, dev, state):
        if state == 'On':
            self._host.chip.tx.override_mode(dev, True)
        else:
            self._host.chip.tx.override_mode(dev, False)
