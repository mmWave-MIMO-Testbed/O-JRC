import chip_info
import rcu
import evk_logger

class Ref_clk():

    __instance = None
    fref       = {}           # XO reference frequency
    is_diff    = True         # XO reference is differential
    diff       = 0x01

    def __new__(cls, spi, fref):
        if cls.__instance is None:
            cls.__instance = super(Ref_clk, cls).__new__(cls)
            cls.__instance.__initialized = False
        return cls.__instance

    def __init__(self, spi, fref=None):
        if self.__initialized != True:
            self.spi       = spi
            self.chip_info = chip_info.Chip_info(spi)
            self.rcu       = rcu.Rcu(spi)
            for dev_num in range(0,self.chip_info.get_num_devs()):
                dev      = self.chip_info.get_dev(dev_num)
                dev_info = self.chip_info.get(dev,printit=None)
                if fref is not None:
                    self.set(dev,fref)                
                elif dev_info['type'] is not None:
                    self.set(dev,dev_info['fref_def'])
            self.__initialized = True

    def set(self, devs, freq):
        devs_l = devs
        if not isinstance(devs_l, list):
            devs_l = [devs_l]
            return_one = True
        if not isinstance(freq, list):
            freq = [freq]*len(devs_l)

        for i,dev in enumerate(devs_l):
            try:
                dev.chip_num
            except:
                evk_logger.evk_logger.log_error("  ref_clk.set: Device identifier {:} does not contain the required attribute chip_num.".format(dev))
                next
            try:
                self.fref[dev.chip_num] = float(freq[i])
            except:
                evk_logger.evk_logger.log_error("  ref_clk.set: Reference frequency {:} for Device {:} could not be set.".format(fref[i],dev.chip_num))
        return self.get(devs)

    def get(self, devs):
        return_one = False
        resp = []
        if not isinstance(devs, list):
            devs = [devs]
            return_one = True

        for i,dev in enumerate(devs):
            try:
                dev.chip_num
            except:
                evk_logger.evk_logger.log_error("  ref_clk.get: Device identifier {:} does not contain the required attribute chip_num.".format(dev))
                resp.append(0)
            try:
                resp.append(self.fref[dev.chip_num])
            except:
                evk_logger.evk_logger.log_error("   ref_clk.get: Device {:} does not have any reference frequency (fref) set yet.".format(dev.chip_num))
                resp.append(0)
            
        if return_one == True:
            return resp[0]
        else:
            return resp
