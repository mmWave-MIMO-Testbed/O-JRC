import chip_info
import evk_logger

class Sd():

    __instance = None
    sd_length = 2**24
    freq_ref = 122.88e6

    def __new__(cls, spi):
        if cls.__instance is None:
            cls.__instance = super(Sd, cls).__new__(cls)
            cls.__instance.__initialized = False
        return cls.__instance

    def __init__(self, spi):
        self.spi       = spi
        self.chip_info = chip_info.Chip_info(spi)


    @evk_logger.log_call
    def calc_N_k(self, dev, freq, fref):
        if self.chip_info.get(dev,False)['band'] == 28:
            div = 3.0
        elif self.chip_info.get(dev,False)['band'] == 39:
            div = 6.0
        freq_rel = freq/div/fref
        N    = int(freq_rel)
        frac = round((freq_rel-N)*self.sd_length)
        return N, frac

    @evk_logger.log_call
    def calc_rf_freq(self, dev, N, k, fref):
        if self.chip_info.get(dev,False)['band'] == 28:
            div = 3.0
        elif self.chip_info.get(dev,False)['band'] == 39:
            div = 6.0
        return round((N+k/self.sd_length)*div*fref)
        

    @evk_logger.log_call
    def cfg_rd(self, devs):
        cfg = self.spi.rd(devs, 'sd_config')
        resp={}
        resp['sd_prbs_en'] = (cfg >> 7) & 1
        resp['sd_dither_en'] = (cfg >> 4) & 7
        resp['sd_order'] = (cfg >> 2) & 3
        resp['sd_not_rst_at_en'] = (cfg >> 1) & 1
        resp['sd_rst_n'] = (cfg >> 0) & 1
        cfg = self.spi.rd(devs, 'sm_sd_fsm_config')
        resp['sd_wait_on_sm'] = cfg
        cfg = self.spi.rd(devs, 'sm_sd_fsm_delay')
        resp['sd_delay'] = cfg
        return resp


    @evk_logger.log_call
    def cfg_wr(self, devs, cfg = {'sd_prbs_en':None, 'sd_dither_en':None, 'sd_order':None, 'sd_not_rst_at_en':None, 'sd_rst_n':None, 'sd_wait_on_sm':None, 'sd_delay':None}):
        sd_wait_on_sm = cfg.pop('sd_wait_on_sm', None)
        sd_delay      = cfg.pop('sd_delay', None)
        for key,val in cfg.items():
            if val is None:
                cfg.pop(key)
        self.spi.wr(devs, 'sd_config', cfg)

        if sd_wait_on_sm != None:
            self.spi.wr(devs, 'sm_sd_fsm_config', sd_wait_on_sm)

        if sd_delay != None:
            self.spi.wr(devs, 'sm_sd_fsm_delay', sd_delay)

        return self.cfg_rd(devs)
