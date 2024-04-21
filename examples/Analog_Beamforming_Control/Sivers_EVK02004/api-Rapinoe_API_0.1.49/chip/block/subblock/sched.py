class Sched():

    __instance = None

    def __new__(cls, spi):
        if cls.__instance is None:
            cls.__instance = super(Sched, cls).__new__(cls)
            cls.__instance.__initialized = False
        return cls.__instance

    def __init__(self, spi):
        self.evk_logger   = evk_logger.EvkLogger()
        self.spi          = spi
        self.amux         = amux.Amux(spi)
