class GeneralActions():

    def __init__(self, gui_data):
        self._gui_data = gui_data

    # Reset
    def reset(self):
        self._gui_data.reset()

    # State
    def state_set(self, state):
        command = "self._host.chip.trx.mode(__RAP__, '{}')".format(state)
        self._gui_data.exec_command(command)

    # Init
    def init(self, block):
        command = "self._host.chip.init(__RAP__, grps='{}')".format(block)
        self._gui_data.exec_command(command)

    def pwr_on(self, port):
        command = "self._host.pwr.on('{}')".format(port)
        self._gui_data.exec_command(command)
        command = "self._host.pwr.status('{}')".format(port)
        return self._gui_data.exec_command(command)

    def pwr_off(self, port):
        command = "self._host.pwr.off('{}')".format(port)
        self._gui_data.exec_command(command)
        command = "self._host.pwr.status('{}')".format(port)
        return self._gui_data.exec_command(command)

    def pwr_status(self, port=None):
        if port == None:
            command = "self._host.pwr.status()"
            return self._gui_data.exec_command(command)
        command = "self._host.pwr.status('{}')".format(port)
        return self._gui_data.exec_command(command)

    def misc_on(self, port):
        command = "self._host.misc.on('{}')".format(port)
        self._gui_data.exec_command(command)
        command = "self._host.misc.status('{}')".format(port)
        return self._gui_data.exec_command(command)

    def misc_off(self, port):
        command = "self._host.misc.off('{}')".format(port)
        self._gui_data.exec_command(command)
        command = "self._host.misc.status('{}')".format(port)
        return self._gui_data.exec_command(command)

    def misc_status(self, port=None):
        if port == None:
            command = "self._host.misc.status()"
            return self._gui_data.exec_command(command)
        command = "self._host.misc.status('{}')".format(port)
        return self._gui_data.exec_command(command)