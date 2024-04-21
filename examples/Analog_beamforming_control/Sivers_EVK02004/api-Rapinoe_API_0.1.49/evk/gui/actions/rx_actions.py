class RxActions():

    def __init__(self, host):
        self._host = host

    def setup(self, dev, mode, pol, latitude, ant_en_v, ant_en_h):
        self._host.chip.rx.setup(dev, mode, pol, latitude=latitude, ant_en_v=ant_en_v, ant_en_h=ant_en_h)

    def rf_gain(self, dev, pol, gain_index):
        self._host.chip.rx.gain(dev, gain_index, pol=pol, sync=1)

    def beam(self, dev, pol, beam_index):
        self._host.chip.rx.beam(dev, beam_index, pol=pol, sync=1)

    def dco_calibrate(self, dev, pol, gain_index):
        self._host.chip.rx.dco.calibrate(dev, pol, gain_index)
    def override(self, dev, state):
        if state == 'On':
            self._host.chip.rx.override_mode(dev, True)
        else:
            self._host.chip.rx.override_mode(dev, False)

