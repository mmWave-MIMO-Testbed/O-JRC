class Rcu():

    __instance    = None

    def __new__(cls, spi):
        if cls.__instance is None:
            cls.__instance = super(Rcu, cls).__new__(cls)
            cls.__instance.__initialized = False
        return cls.__instance

    def __init__(self, spi):
        self.spi = spi

    def freq_meas_reset(self, devs):
        self.spi.wr(devs,'fgu_freq_ctrl',0x00)
        self.spi.set(devs,'rgu_misc_rst',0x02)
        self.spi.clr(devs,'rgu_misc_rst',0x02)


    def freq_meas(self, devs):
        self.spi.wr(devs,'fgu_freq_ctrl',0x00)
        self.spi.wr(devs,'fgu_freq_ctrl',0x01)
        while (self.spi.rd(devs,'fgu_freq_ctrl') != 0x11):
            pass
        return self.freq_meas_status(devs)


    def freq_meas_status(self, devs):
        sys_clk_cnt  = self.spi.rd(devs,'cgu_freq_ref')
        meas_clk_cnt = self.spi.rd(devs,'cgu_freq_meas')
        return (meas_clk_cnt, sys_clk_cnt)
