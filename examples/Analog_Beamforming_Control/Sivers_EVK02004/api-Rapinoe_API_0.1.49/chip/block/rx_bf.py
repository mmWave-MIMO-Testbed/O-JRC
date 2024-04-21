class RxBf():

    __instance = None

    def __new__(cls, connection):
        if cls.__instance is None:
            cls.__instance = super(RxBf, cls).__new__(cls)
            cls.__instance.__initialized = False
        return cls.__instance

    def __init__(self):
        pass
