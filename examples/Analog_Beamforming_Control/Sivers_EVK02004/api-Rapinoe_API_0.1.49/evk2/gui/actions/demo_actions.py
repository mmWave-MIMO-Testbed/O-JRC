class DemoActions():

    def __init__(self, gui_data):
        self._gui_data = gui_data

    def get_num_devs(self):
        command = "self._host.chip._chip_info.get_num_devs()"
        return self._gui_data.exec_command(command)

    def get_rap(self, n):
        command = "self._host.rap{:}".format(n)
        return self._gui_data.exec_command(command)

    def run_script(self, script_file):
        command = "self._host.run_script('{}')".format(script_file)
        self._gui_data.exec_command(command)
