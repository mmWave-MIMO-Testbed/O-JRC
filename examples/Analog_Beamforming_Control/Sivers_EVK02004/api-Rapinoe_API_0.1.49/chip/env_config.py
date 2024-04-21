import os

class EnvConfig(object):

    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super(EnvConfig, cls).__new__(cls)
            cls.__instance.__initialized = False
        return cls.__instance

    def __init__(self):
        self.abs_dirname = os.path.dirname(os.path.abspath(__file__))

    def main_path(self):
        return self.abs_dirname

    def register_map_path(self):
        return self.abs_dirname

    def beambook_path(self):
        return self.abs_dirname + '/lut/beambook'

    def alc_path(self):
        return self.abs_dirname + '/lut/vco'

    def config_path(self):
        return self.abs_dirname + '/config'

    def ram_path(self):
        return self.abs_dirname + '/../config/ram'

    def eeprom_path(self):
        return self.abs_dirname + '/../config/eeprom'

env_config = EnvConfig()