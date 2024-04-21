class RxLvlDet():

    __instance = None
    __initialized = False

    WAIT_SLEEP   = (1<<7)
    WAIT_SX      = (1<<6)
    WAIT_TX      = (1<<5)
    WAIT_RX      = (1<<4)
    DETECT_SLEEP = (1<<3)
    DETECT_SX    = (1<<2)
    DETECT_TX    = (1<<1)
    DETECT_RX    = 1


    def __new__(cls, spi):
        if cls.__instance is None:
            cls.__instance = super(RxLvlDet, cls).__new__(cls)
            cls.__instance.__initialized = False
        return cls.__instance

    def __init__(self, spi):
        if not RxLvlDet.__initialized:
            self._spi = spi
            RxLvlDet.__initialized = True

    def set_wait_time(self, devs, wait_time=0x7f):
        self._spi.wr(devs, 'rx_lvl_det_wait_time', wait_time)

    def det_setup(self, devs, pol, cnt_th, cfg=WAIT_SLEEP|WAIT_SX|WAIT_TX|WAIT_RX|DETECT_SLEEP|DETECT_SX|DETECT_TX|DETECT_RX):
        self.set_wait_time()
        pol = pol.upper()
        if (pol == 'RVRH') or (pol == 'RV') or (pol == 'V') or (pol == 'RHRV'):
            self._spi.wr(devs, 'rx_lvl_det_cnt_th_v', cnt_th)
            self._spi.wr(devs, 'rx_lvl_det_cfg_v', cfg)

        if (pol == 'RVRH') or (pol == 'RH') or (pol == 'H') or (pol == 'RHRV'):
            self._spi.wr(devs, 'rx_lvl_det_cnt_th_h', cnt_th)
            self._spi.wr(devs, 'rx_lvl_det_cfg_h', cfg)

    def det_enable(self, devs, pol):
        pol = pol.upper()
        if (pol == 'RVRH') or (pol == 'RV') or (pol == 'V') or (pol == 'RHRV'):
            self._spi.set(devs, 'rx_lvl_det_en', 0x10)
        if (pol == 'RVRH') or (pol == 'RH') or (pol == 'H') or (pol == 'RHRV'):
            self._spi.set(devs, 'rx_lvl_det_en', 0x01)

    def det_disable(self, devs, pol):
        pol = pol.upper()
        if (pol == 'RVRH') or (pol == 'RV') or (pol == 'V') or (pol == 'RHRV'):
            self._spi.clr(devs, 'rx_lvl_det_en', 0x10)
        if (pol == 'RVRH') or (pol == 'RH') or (pol == 'H') or (pol == 'RHRV'):
            self._spi.clr(devs, 'rx_lvl_det_en', 0x01)

    def com_setup(self, devs, pol, dac_cal, lvl_ctrl, lvl_lo):
        pol = pol.upper()
        if (pol == 'RVRH') or (pol == 'RV') or (pol == 'V') or (pol == 'RHRV'):
            self._spi.wr(devs, 'com_rx_det_config_v', (lvl_lo&0xff)|((lvl_ctrl&0xff)<<8)|((dac_cal&0x1f)<<16))
        if (pol == 'RVRH') or (pol == 'RH') or (pol == 'H') or (pol == 'RHRV'):
            self._spi.wr(devs, 'com_rx_det_config_h', (lvl_lo&0xff)|((lvl_ctrl&0xff)<<8)|((dac_cal&0x1f)<<16))

    def com_enable(self, devs, pol):
        pol = pol.upper()
        if (pol == 'RVRH') or (pol == 'RV') or (pol == 'V') or (pol == 'RHRV'):
            self._spi.set(devs, 'com_rx_det_ctrl', 0x10)
        if (pol == 'RVRH') or (pol == 'RH') or (pol == 'H') or (pol == 'RHRV'):
            self._spi.set(devs, 'com_rx_det_ctrl', 0x01)

    def com_disable(self, devs, pol):
        pol = pol.upper()
        if (pol == 'RVRH') or (pol == 'RV') or (pol == 'V') or (pol == 'RHRV'):
            self._spi.clr(devs, 'com_rx_det_ctrl', 0x10)
        if (pol == 'RVRH') or (pol == 'RH') or (pol == 'H') or (pol == 'RHRV'):
            self._spi.clr(devs, 'com_rx_det_ctrl', 0x01)

    def com_status(self, devs):
        return self._spi.rd(devs, 'com_rx_det_status')