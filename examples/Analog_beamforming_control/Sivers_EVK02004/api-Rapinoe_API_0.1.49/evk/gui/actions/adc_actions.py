class AdcActions():

    def __init__(self, host):
        self._host = host

    def enable(self, dev):
        self._host.chip.adc.enable(dev)
