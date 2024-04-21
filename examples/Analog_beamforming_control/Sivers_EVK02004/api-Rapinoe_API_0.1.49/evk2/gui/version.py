# DO NOT CHANGE VERSION.
# VERSION IS UPDATED BY INSTALLER BUILDER
RAPINOE_API_VER = "0.1.28"

class Version():
    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super(Version, cls).__new__(cls)
            cls.__instance.__initialized = False
        return cls.__instance

    def __init__(self):
        self._api_version = RAPINOE_API_VER

    def get_version(self):
        return self._api_version
