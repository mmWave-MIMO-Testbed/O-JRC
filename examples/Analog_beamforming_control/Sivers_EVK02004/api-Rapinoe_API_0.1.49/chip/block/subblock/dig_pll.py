import math
import evk_logger
import ref_clk
from common import *

class Dig_pll():

    __instance = None

    def __new__(cls, spi):
        if cls.__instance is None:
            cls.__instance = super(Dig_pll, cls).__new__(cls)
            cls.__instance.__initialized = False
        return cls.__instance

    def __init__(self, spi):
        self.spi        = spi
        self.ref_clk    = ref_clk.Ref_clk(spi)


    def set(self, devs, freq):
        return_one = False
        resp       = []
        if not isinstance(devs, list):
            devs = [devs]
            return_one = True
            
        frefs = self.ref_clk.get(devs)

        if return_one == True:
            return resp[0]
        else:
            return resp

