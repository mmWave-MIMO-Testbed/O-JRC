import test_host
import threading
import multiprocessing

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
            print("111111111111111")
            self.config = config.platform.mb2
            attributes = vars(self.config)
            for key, value in attributes.items():
                print(f"{key} = {value}")
                break
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

def initialize_host(serial_num, bsp, fspi):
    try:
        host_instance = Connect(serial_num=serial_num, bsp=bsp, clock_rate=fspi)
        print(f"Host initialized for serial number: {serial_num}")
    except Exception as e:
        print(f"Failed to initialize Host for serial number: {serial_num}, error: {e}")


if __name__ == '__main__':

    # Serial numbers for the devices
    serial_num1 = "T582306548"
    serial_num2 = "T582306549"

    process1 = multiprocessing.Process(target=initialize_host, args=(serial_num1, 'rapvalt', 1000000))
    process2 = multiprocessing.Process(target=initialize_host, args=(serial_num2, 'rapvalt', 1000000))

    # Start and join the processes
    process1.start()
    process1.join()

    process2.start()
    process2.join()

