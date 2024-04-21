class GeneralActions():

    def __init__(self, host):
        self._host = host

    # Reset
    def reset(self, dev):
        self._host.reset(dev)

    # State
    def state_set(self, dev, state):
        self._host.chip.trx.mode(dev, state)

    # Init
    def init(self, dev, block):
        self._host.chip.init(dev, grps=block, printit=False)

    def pwr_on(self, port):
        self._host.pwr.on(port)
        return self._host.pwr.status(port)

    def pwr_off(self, port):
        self._host.pwr.off(port)
        return self._host.pwr.status(port)

    def pwr_status(self, port=None):
        if port == None:
            return self._host.pwr.status()
        return self._host.pwr.status(port)

    def misc_on(self, port):
        self._host.misc.on(port)
        return self._host.misc.status(port)

    def misc_off(self, port):
        self._host.misc.off(port)
        return self._host.misc.status(port)

    def misc_status(self, port=None):
        if port == None:
            return self._host.misc.status()
        return self._host.misc.status(port)