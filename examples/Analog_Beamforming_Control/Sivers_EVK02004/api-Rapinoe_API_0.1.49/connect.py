
class Connect:
    
    def __init__(self, serial_num, bsp, clock_rate=10000000):

        import mbdrv

        self.serial_num = serial_num
        self.mb         = mbdrv.MbDrv()
        self.board_id  = self.mb.get_board_id(serial_num)

        # Get MB configuration
        self.board_type = self.mb.get_board_type(self.board_id)
        if self.board_type == 'EVK06002':
            import config.platform.mb1
            self.config = config.platform.mb1
        elif self.board_type == 'MB2':
            import config.platform.mb2
            self.config = config.platform.mb2
            attributes = vars(self.config)
            for key, value in attributes.items():
                print(f"{key} = {value}")
                break
            for hw_obj in list(self.config.HW_OBJECTS):
                exec("self.{} = self.config.{}(**{})".format(hw_obj, self.config.HW_OBJECTS[hw_obj]['type'], self.config.HW_OBJECTS[hw_obj]['params']))
        elif self.board_type == 'DBMB':
            import config.platform.dbmb
            self.config = config.platform.dbmb
            for hw_obj in list(self.config.HW_OBJECTS):
                exec("self.{} = self.config.{}(**{})".format(hw_obj, self.config.HW_OBJECTS[hw_obj]['type'], self.config.HW_OBJECTS[hw_obj]['params']))

        # Get module configuration
        if (bsp == 'rapvalbsp') or (bsp == 'rapvalx'):
            import config.bsp.rapvalx
            self._override_signals(config.bsp.rapvalx, self.config)
            for hw_obj in list(config.bsp.rapvalx.HW_OBJECTS):
                exec("self.{} = config.bsp.rapvalx.{}(**{})".format(hw_obj, config.bsp.rapvalx.HW_OBJECTS[hw_obj]['type'], config.bsp.rapvalx.HW_OBJECTS[hw_obj]['params']))
        elif bsp == 'rapvalt':
            import config.bsp.rapvalt
            self._override_signals(config.bsp.rapvalt, self.config)
            for hw_obj in list(config.bsp.rapvalt.HW_OBJECTS):
                exec("self.{} = config.bsp.rapvalt.{}(**{})".format(hw_obj, config.bsp.rapvalt.HW_OBJECTS[hw_obj]['type'], config.bsp.rapvalt.HW_OBJECTS[hw_obj]['params']))
        elif bsp == 'bfm02803':
            import config.bsp.bfm02803
            self._override_signals(config.bsp.bfm02803, self.config)
            for hw_obj in list(config.bsp.bfm02803.HW_OBJECTS):
                exec("self.{} = config.bsp.bfm02803.{}(**{})".format(hw_obj, config.bsp.bfm02803.HW_OBJECTS[hw_obj]['type'], config.bsp.bfm02803.HW_OBJECTS[hw_obj]['params']))
        elif bsp == 'dbm1':
            import config.bsp.dbm1
            self._override_signals(config.bsp.dbm1, self.config)
            for hw_obj in list(config.bsp.dbm1.HW_OBJECTS):
                exec("self.{} = config.bsp.dbm1.{}(**{})".format(hw_obj, config.bsp.dbm1.HW_OBJECTS[hw_obj]['type'], config.bsp.dbm1.HW_OBJECTS[hw_obj]['params']))


        self.mb.gpio_open(self.board_id, 0, self.config.GPIO_STATE_C)
        self.mb.gpio_open(self.board_id, 1, self.config.GPIO_STATE_D)
        print("  SPI speed set to {} MHz".format(clock_rate/1e6))
        self.spi_chan = self.mb.spi_open(self.board_id, mode=0, clock_rate=clock_rate, pin=self.config.GPIO_STATE_A)
        self.i2c_chan = self.mb.i2c_open(self.board_id, pin=self.config.GPIO_STATE_B)

    def _override_signals(self, bsp, conf):
        sig_names = [item for item in dir(conf)]
        for sig_name in sig_names:
            try:
                exec("conf.{} = bsp.{}".format(sig_name,sig_name))
            except:
                pass
