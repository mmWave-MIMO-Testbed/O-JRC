import sys
import os
import ctypes
from threading import Lock

class MbDrv():

    class FT_DEVICE_LIST_INFO_NODE(ctypes.Structure):
            _fields_=[ ("Flags", ctypes.c_uint32),
                        ("Type", ctypes.c_uint32),
                        ("ID", ctypes.c_uint32),
                        ("LocId", ctypes.c_uint32),
                        ("SerialNumber",ctypes.c_char * 16),
                        ("Description",ctypes.c_char * 64),
                        ("ftHandle", ctypes.c_void_p)]

    def __init__(self, dll_path='lib'):
        abspath = os.path.abspath(__file__)
        dll_path = os.path.dirname(abspath) + '/' + dll_path + '/'
        if sys.platform == 'linux':
            self.MbDrv_dll = ctypes.CDLL(dll_path+'linux/x86_64/'+'libmbdrv.so', ctypes.RTLD_GLOBAL)
        else:
            self.MbDrv_dll = ctypes.WinDLL (dll_path+'win\\'+'MBDRV.dll')

        self.MbDrv_dll.get_mbdrv_version.argtypes = ()
        self.MbDrv_dll.get_mbdrv_version.restype = ctypes.c_char_p
        self.MbDrv_dll.list_devs.argtypes = (ctypes.POINTER(self.FT_DEVICE_LIST_INFO_NODE),)
        self.MbDrv_dll.get_num_of_channels.argtypes = ()
        self.MbDrv_dll.print_dev_info.argtypes = (ctypes.c_uint8,)
        self.MbDrv_dll.spi_chaninfo_init()
        self.MbDrv_dll.get_device_id.argtypes = (ctypes.c_char_p,)
        self.MbDrv_dll.get_serial_number.argtypes = (ctypes.c_uint8,)
        self.MbDrv_dll.get_serial_number.restype = ctypes.c_char_p
        self.MbDrv_dll.get_description.argtypes = (ctypes.c_uint8,)
        self.MbDrv_dll.get_description.restype = ctypes.c_char_p
        self.MbDrv_dll.get_board_type.argtypes = (ctypes.c_uint8,)
        self.MbDrv_dll.spi_chaninfo_get_chan.argtypes = (ctypes.c_char_p,)
        self.MbDrv_dll.spi_init.argtypes = (ctypes.c_uint8, ctypes.c_uint8, ctypes.c_uint32, ctypes.c_uint8, ctypes.c_uint8, ctypes.c_uint32, ctypes.c_uint8)
        self.MbDrv_dll.spi_reconfig.argtypes = (ctypes.c_uint8, ctypes.c_uint8, ctypes.c_uint32, ctypes.c_uint8, ctypes.c_uint8, ctypes.c_uint32, ctypes.c_uint8)
        self.MbDrv_dll.spi_change_cs.argtypes = (ctypes.c_uint8, ctypes.c_uint8, ctypes.c_uint8, ctypes.c_uint8)
        self.MbDrv_dll.spi_read.argtypes = (ctypes.c_uint8, ctypes.POINTER(ctypes.c_uint8), ctypes.c_uint32, ctypes.POINTER(ctypes.c_uint8), ctypes.c_uint32)
        self.MbDrv_dll.spi_write.argtypes = (ctypes.c_uint8, ctypes.POINTER(ctypes.c_uint8), ctypes.c_uint32)
        self.MbDrv_dll.spi_read_write.argtypes = (ctypes.c_uint8, ctypes.POINTER(ctypes.c_uint8), ctypes.c_uint32, ctypes.POINTER(ctypes.c_uint8))
        self.MbDrv_dll.spi_gpio.argtypes = (ctypes.c_uint8, ctypes.c_uint8, ctypes.c_uint8, ctypes.c_uint8)
        self.MbDrv_dll.spi_gpio_grp_set_dir.argtypes = (ctypes.c_uint8, ctypes.c_uint8, ctypes.c_uint8)
        self.MbDrv_dll.spi_grp_gpio.argtypes = (ctypes.c_uint8, ctypes.c_uint8, ctypes.c_uint8, ctypes.c_uint8)
        self.MbDrv_dll.spi_gpio_get.argtypes = (ctypes.c_uint8, ctypes.c_uint8, ctypes.POINTER(ctypes.c_uint8), ctypes.c_uint8)
        self.MbDrv_dll.spi_gpio_dir.argtypes = (ctypes.c_uint8, ctypes.c_uint8, ctypes.c_uint8)
        self.MbDrv_dll.spi_close.argtypes = (ctypes.c_uint8,)
        self.MbDrv_dll.cleanup_libmpsse.argtypes = ()
        self.MbDrv_dll.get_signal.argtypes = (ctypes.c_uint8, ctypes.c_uint16, ctypes.POINTER(ctypes.c_uint8), ctypes.c_uint8)
        self.MbDrv_dll.set_signal.argtypes = (ctypes.c_uint8, ctypes.c_uint16, ctypes.c_bool, ctypes.c_uint8, ctypes.c_bool, ctypes.c_uint16)
        self.MbDrv_dll.set_grp_signal.argtypes = (ctypes.c_uint8, ctypes.c_uint8, ctypes.c_uint8, ctypes.c_uint8, ctypes.c_uint8)
        self.MbDrv_dll.get_grp_signal.argtypes = (ctypes.c_uint8, ctypes.c_uint8, ctypes.c_uint8, ctypes.c_uint8, ctypes.POINTER(ctypes.c_uint8))
        self.MbDrv_dll.set_signal_direction.argtypes = (ctypes.c_uint8, ctypes.c_uint16, ctypes.c_bool)
        self.MbDrv_dll.get_signal_direction.argtypes = (ctypes.c_uint8, ctypes.c_uint16)
        self.MbDrv_dll.get_signal_grp_direction.argtypes = (ctypes.c_uint8, ctypes.c_uint8)
        self.MbDrv_dll.set_signal_grp_direction.argtypes = (ctypes.c_uint8, ctypes.c_uint8, ctypes.c_uint8, ctypes.c_uint8)
        self.MbDrv_dll.i2c_chaninfo_init.argtypes = ()
        self.MbDrv_dll.i2c_chaninfo_get_chan.argtypes = (ctypes.c_char_p,)
        self.MbDrv_dll.i2c_init.argtypes = (ctypes.c_uint8, ctypes.c_uint32)
        self.MbDrv_dll.i2c_gpio.argtypes = (ctypes.c_uint8, ctypes.c_uint8, ctypes.c_uint8, ctypes.c_uint8)
        self.MbDrv_dll.i2c_gpio_get.argtypes = (ctypes.c_uint8, ctypes.c_uint8, ctypes.POINTER(ctypes.c_uint8), ctypes.c_uint8)
        self.MbDrv_dll.i2c_gpio_dir.argtypes = (ctypes.c_uint8, ctypes.c_uint8, ctypes.c_uint8)
        self.MbDrv_dll.i2c_close.argtypes = (ctypes.c_uint8,)
        self.MbDrv_dll.i2c_read.argtypes = (ctypes.c_uint8, ctypes.c_uint32, ctypes.POINTER(ctypes.c_uint8), ctypes.c_uint32, ctypes.c_bool, ctypes.c_bool, ctypes.c_bool, ctypes.c_bool, ctypes.c_bool, ctypes.c_bool)
        self.MbDrv_dll.i2c_write.argtypes = (ctypes.c_uint8, ctypes.c_uint32, ctypes.POINTER(ctypes.c_uint8), ctypes.c_uint32, ctypes.c_bool, ctypes.c_bool, ctypes.c_bool, ctypes.c_bool, ctypes.c_bool, ctypes.c_bool)
        self.MbDrv_dll.gpio_init.argtypes = (ctypes.c_uint8, ctypes.c_uint8, ctypes.c_uint32)
        self.MbDrv_dll.gpio_pin_set.argtypes = (ctypes.c_uint8, ctypes.c_uint8, ctypes.c_uint8, ctypes.c_uint8, ctypes.c_uint8)
        self.MbDrv_dll.gpio_grp_set.argtypes = (ctypes.c_uint8, ctypes.c_uint8, ctypes.c_uint8, ctypes.c_uint8)
        self.MbDrv_dll.gpio_grp_set_direction.argtypes = (ctypes.c_uint8, ctypes.c_uint8, ctypes.c_uint8, ctypes.c_uint8)
        self.MbDrv_dll.gpio_pin_set_direction.argtypes = (ctypes.c_uint8, ctypes.c_uint8, ctypes.c_uint8, ctypes.c_uint8)
        self.MbDrv_dll.gpio_pin_get.argtypes = (ctypes.c_uint8, ctypes.c_uint8, ctypes.c_uint8, ctypes.POINTER(ctypes.c_uint8), ctypes.c_uint8)
        self.MbDrv_dll.gpio_grp_get.argtypes = (ctypes.c_uint8, ctypes.c_uint8, ctypes.POINTER(ctypes.c_uint8), ctypes.c_uint8, ctypes.c_uint8)
        self.MbDrv_dll.gpio_close.argtypes = (ctypes.c_uint8, ctypes.c_uint8)
        self.MbDrv_dll.set_vcm.argtypes = (ctypes.c_uint8, ctypes.c_uint16)
        self.MbDrv_dll.set_vchp.argtypes = (ctypes.c_uint8, ctypes.c_uint16)
        self.MbDrv_dll.get_chpc.argtypes = (ctypes.c_uint8, ctypes.POINTER(ctypes.c_uint8))

        self.lock = Lock()
        self._set_default_spi_setting()

        n = self.num_of_channels()
        if n > 0:
            dev_info = self._list_devs()
        self._i2c_chaninfo_init()
        self._spi_chaninfo_init()

    def _list_devs(self):
        self.lock.acquire()
        dev_info = (self.FT_DEVICE_LIST_INFO_NODE * 40)()
        dev_info_array = ctypes.cast(dev_info, ctypes.POINTER(self.FT_DEVICE_LIST_INFO_NODE))
        res = self.MbDrv_dll.list_devs(dev_info_array)
        self.lock.release()
        return dev_info_array[0:res]

    def _print_dev_info(self, index):
        self.lock.acquire()
        self.MbDrv_dll.print_dev_info(ctypes.c_uint8(index))
        self.lock.release()

    def _spi_chaninfo_init(self):
        self.lock.acquire()
        res = self.MbDrv_dll.spi_chaninfo_init()
        self.lock.release()
        return res

    def _get_device_id(self, serial_num):
        self.lock.acquire()
        res = self.MbDrv_dll.get_device_id(serial_num.encode())
        self.lock.release()
        return res

    def _get_serial_number(self, index):
        self.lock.acquire()
        res = self.MbDrv_dll.get_serial_number(ctypes.c_uint8(index))
        self.lock.release()
        return res

    def _get_description(self, index):
        self.lock.acquire()
        res = self.MbDrv_dll.get_description(ctypes.c_uint8(index))
        self.lock.release()
        return res

    def _get_board_type(self, index):
        self.lock.acquire()
        res = self.MbDrv_dll.get_description(ctypes.c_uint8(index))
        self.lock.release()
        return res.decode()

    def _spi_chaninfo_get_chan(self, serial_num):
        self.lock.acquire()
        res = self.MbDrv_dll.spi_chaninfo_get_chan(serial_num.encode())
        self.lock.release()
        return res

    def _spi_init(self, dev_index, cs, clock_rate, latency_timer, mode, pin, cs_active_level):
        self.lock.acquire()
        res = self.MbDrv_dll.spi_init(ctypes.c_uint8(dev_index), ctypes.c_uint8(cs), ctypes.c_uint32(clock_rate), ctypes.c_uint8(latency_timer), ctypes.c_uint8(mode), ctypes.c_uint32(pin), ctypes.c_uint8(cs_active_level))
        self.lock.release()
        return res

    def _spi_reconfig(self, dev_index, cs, clock_rate, latency_timer, mode, pin, cs_active_level):
        self.lock.acquire()
        res = self.MbDrv_dll.spi_reconfig(ctypes.c_uint8(dev_index), ctypes.c_uint8(cs), ctypes.c_uint32(clock_rate), ctypes.c_uint8(latency_timer), ctypes.c_uint8(mode), ctypes.c_uint32(pin), ctypes.c_uint8(cs_active_level))
        self.lock.release()
        return res

    def _spi_change_cs(self, dev_index, cs, mode, cs_active_level):
        self.lock.acquire()
        res = self.MbDrv_dll.spi_change_cs(ctypes.c_uint8(dev_index), ctypes.c_uint8(cs), ctypes.c_uint8(mode), ctypes.c_uint8(cs_active_level))
        if res == 0:
            self.current_cs = cs
            self.current_mode = mode
            self.current_cs_active_level = cs_active_level
        self.lock.release()
        return res

    def _spi_read(self, dev_index, send_buffer, rcv_buffer_size):
        self.lock.acquire()
        send_buffer_array = (ctypes.c_uint8 * len(send_buffer))(*send_buffer)
        receive_buffer = [0xff] * rcv_buffer_size
        receive_buffer_array = (ctypes.c_uint8 * len(receive_buffer))(*receive_buffer)
        res = self.MbDrv_dll.spi_read(ctypes.c_uint8(dev_index), send_buffer_array, ctypes.c_uint32(len(send_buffer)), receive_buffer_array, ctypes.c_uint32(len(receive_buffer)))
        if res != 0:
            self.lock.release()
            return None
        self.lock.release()
        return list(receive_buffer_array)

    def _spi_write(self, dev_index, send_buffer):
        self.lock.acquire()
        send_buffer_array = (ctypes.c_uint8 * len(send_buffer))(*send_buffer)
        res = self.MbDrv_dll.spi_write(ctypes.c_uint8(dev_index), send_buffer_array, ctypes.c_uint32(len(send_buffer)))
        self.lock.release()
        return res

    def _spi_read_write(self, dev_index, send_buffer):
        self.lock.acquire()
        send_buffer_array = (ctypes.c_uint8 * len(send_buffer))(*send_buffer)
        receive_buffer = [0] * len(send_buffer)
        receive_buffer_array = (ctypes.c_uint8 * len(receive_buffer))(*receive_buffer)
        res = self.MbDrv_dll.spi_read_write(ctypes.c_uint8(dev_index), send_buffer_array, ctypes.c_uint32(len(send_buffer)), receive_buffer_array)
        if res != 0:
            self.lock.release()
            return None
        self.lock.release()
        return list(receive_buffer_array)

    def _spi_gpio(self, dev_index, pin, value, pin_direction):
        self.lock.acquire()
        res = self.MbDrv_dll.spi_gpio(ctypes.c_uint8(dev_index), ctypes.c_uint8(pin), ctypes.c_uint8(value), ctypes.c_uint8(pin_direction))
        self.lock.release()
        return res

    def _spi_gpio_grp_set_dir(self, dev_index, direction, dir_mask):
        self.lock.acquire()
        res = self.MbDrv_dll.spi_gpio_grp_set_dir(ctypes.c_uint8(dev_index), ctypes.c_uint8(direction), ctypes.c_uint8(dir_mask))
        self.lock.release()
        return res

    def _spi_grp_gpio(self, dev_index, value, direction, dir_mask):
        self.lock.acquire()
        res = self.MbDrv_dll.spi_grp_gpio(ctypes.c_uint8(dev_index), ctypes.c_uint8(value), ctypes.c_uint8(direction), ctypes.c_uint8(dir_mask))
        self.lock.release()
        return res

    def _spi_gpio_get(self, dev_index, pin, pin_direction):
        self.lock.acquire()
        value = ctypes.c_uint8(0)
        value_p = ctypes.pointer(value)
        res = self.MbDrv_dll.spi_gpio_get(ctypes.c_uint8(dev_index), ctypes.c_uint8(pin), value_p, ctypes.c_uint8(pin_direction))
        if res != 0:
            self.lock.release()
            return None
        self.lock.release()
        return value_p.contents.value

    def _spi_gpio_dir(self, dev_index, pin, dir):
        self.lock.acquire()
        res = self.MbDrv_dll.spi_gpio_dir(ctypes.c_uint8(dev_index), ctypes.c_uint8(pin), ctypes.c_uint8(dir))
        self.lock.release()
        return res

    def _spi_close(self, dev_index):
        self.lock.acquire()
        res = self.MbDrv_dll.spi_close(ctypes.c_uint8(dev_index))
        self.lock.release()
        return res

    def _cleanup_libmpsse(self):
        self.lock.acquire()
        self.MbDrv_dll.cleanup_libmpsse()
        self.lock.release()

    def _get_signal(self, dev_index, signal_index, pin_direction):
        self.lock.acquire()
        value = ctypes.c_uint8(0)
        value_p = ctypes.pointer(value)
        res = self.MbDrv_dll.get_signal(ctypes.c_uint8(dev_index), ctypes.c_uint16(signal_index), value_p, ctypes.c_uint8(pin_direction))
        if res != 0:
            self.lock.release()
            return None
        self.lock.release()
        return value_p.contents.value

    def _set_signal(self, dev_index, signal_index, on, pin_direction, pulse, pulse_width_ms):
        self.lock.acquire()
        res = self.MbDrv_dll.set_signal(ctypes.c_uint8(dev_index), ctypes.c_uint16(signal_index), ctypes.c_bool(on), ctypes.c_uint8(pin_direction), ctypes.c_bool(pulse), ctypes.c_uint16(pulse_width_ms))
        self.lock.release()
        return res

    def _set_grp_signal(self, dev_index, grp, value, direction, dir_mask):
        self.lock.acquire()
        res = self.MbDrv_dll.set_grp_signal(ctypes.c_uint8(dev_index), ctypes.c_uint8(grp), ctypes.c_uint8(value), ctypes.c_uint8(direction), ctypes.c_uint8(dir_mask))
        self.lock.release()
        return res

    def _get_grp_signal(self, dev_index, grp, direction, dir_mask):
        self.lock.acquire()
        value = ctypes.c_uint8(0)
        value_p = ctypes.pointer(value)
        res = self.MbDrv_dll.get_grp_signal(ctypes.c_uint8(dev_index), ctypes.c_uint8(grp), ctypes.c_uint8(direction), ctypes.c_uint8(dir_mask), value_p)
        if res != 0:
            self.lock.release()
            return None
        self.lock.release()
        return value_p.contents.value

    def _set_signal_direction(self, dev_index, signal_index, output):
        self.lock.acquire()
        res = self.MbDrv_dll.set_signal_direction(ctypes.c_uint8(dev_index), ctypes.c_uint16(signal_index), ctypes.c_bool(output))
        self.lock.release()
        return res

    def _get_signal_direction(self, dev_index, signal_index):
        self.lock.acquire()
        res = self.MbDrv_dll.get_signal_direction(ctypes.c_uint8(dev_index), ctypes.c_uint16(signal_index))
        self.lock.release()
        return res

    def _get_signal_grp_direction(self, dev_index, grp):
        self.lock.acquire()
        res = self.MbDrv_dll.get_signal_grp_direction(ctypes.c_uint8(dev_index), ctypes.c_uint8(grp))
        self.lock.release()
        return res

    def _set_signal_grp_direction(self, dev_index, grp, direction, dir_mask):
        self.lock.acquire()
        res = self.MbDrv_dll.set_signal_grp_direction(ctypes.c_uint8(dev_index), ctypes.c_uint8(grp), ctypes.c_uint8(direction), ctypes.c_uint8(dir_mask))
        self.lock.release()
        return res

    def _i2c_chaninfo_init(self):
        self.lock.acquire()
        res = self.MbDrv_dll.i2c_chaninfo_init()
        self.lock.release()
        return res

    def _i2c_chaninfo_get_chan(self, serial_num):
        self.lock.acquire()
        res = self.MbDrv_dll.i2c_chaninfo_get_chan(serial_num.encode())
        self.lock.release()
        return res

    def _i2c_init(self, dev_index, pin):
        self.lock.acquire()
        res = self.MbDrv_dll.i2c_init(ctypes.c_uint8(dev_index), ctypes.c_uint32(pin))
        self.lock.release()
        return res

    def _i2c_gpio(self, dev_index, pin, value, pin_direction):
        self.lock.acquire()
        res = self.MbDrv_dll.i2c_gpio(ctypes.c_uint8(dev_index), ctypes.c_uint8(pin), ctypes.c_uint8(value), ctypes.c_uint8(pin_direction))
        self.lock.release()
        return res

    def _i2c_gpio_get(self, dev_index, pin, pin_direction):
        self.lock.acquire()
        value = ctypes.c_uint8(0)
        value_p = ctypes.pointer(value)
        res = self.MbDrv_dll.i2c_gpio_get(ctypes.c_uint8(dev_index), ctypes.c_uint8(pin), value_p, ctypes.c_uint8(pin_direction))
        if res != 0:
            self.lock.release()
            return None
        self.lock.release()
        return value_p.contents.value

    def _i2c_gpio_dir(self, dev_index, pin, dir):
        self.lock.acquire()
        res = self.MbDrv_dll.i2c_gpio_dir(ctypes.c_uint8(dev_index), ctypes.c_uint8(pin), ctypes.c_uint8(dir))
        self.lock.release()
        return res

    def _i2c_close(self, dev_index):
        self.lock.acquire()
        res = self.MbDrv_dll.i2c_close(ctypes.c_uint8(dev_index))
        self.lock.release()
        return res

    def _i2c_read(self, dev_index, device_address, rcv_buffer_size, start_condition, stop_condition, nack_last_byte, multi_byte, multi_bit, ignore_address):
        self.lock.acquire()
        receive_buffer = [0] * rcv_buffer_size
        receive_buffer_array = (ctypes.c_uint8 * len(receive_buffer))(*receive_buffer)
        res = self.MbDrv_dll.i2c_read(ctypes.c_uint8(dev_index), ctypes.c_uint32(device_address), receive_buffer_array, ctypes.c_uint32(rcv_buffer_size), 
                                      ctypes.c_bool(start_condition), ctypes.c_bool(stop_condition), ctypes.c_bool(nack_last_byte), ctypes.c_bool(multi_byte), 
                                      ctypes.c_bool(multi_bit), ctypes.c_bool(ignore_address))
        if res != 0:
            self.lock.release()
            return {'status':res, 'data':None}
        self.lock.release()
        return {'status':res, 'data':list(receive_buffer_array)}

    def _i2c_write(self, dev_index, device_address, send_buffer, start_condition, stop_condition, break_on_nack, multi_byte, multi_bit, ignore_address):
        self.lock.acquire()
        send_buffer_array = (ctypes.c_uint8 * len(send_buffer))(*send_buffer)
        res = self.MbDrv_dll.i2c_write(ctypes.c_uint8(dev_index), ctypes.c_uint32(device_address), send_buffer_array, ctypes.c_uint32(len(send_buffer)), 
                                       ctypes.c_bool(start_condition), ctypes.c_bool(stop_condition), ctypes.c_bool(break_on_nack), ctypes.c_bool(multi_byte), 
                                       ctypes.c_bool(multi_bit), ctypes.c_bool(ignore_address))
        self.lock.release()
        return res

    def _gpio_init(self, dev_index, chan, pin):
        self.lock.acquire()
        res = self.MbDrv_dll.gpio_init(ctypes.c_uint8(dev_index), ctypes.c_uint8(chan), ctypes.c_uint32(pin))
        self.lock.release()
        return res

    def _gpio_pin_set(self, dev_index, chan, pin, val, pin_direction):
        self.lock.acquire()
        res = self.MbDrv_dll.gpio_pin_set(ctypes.c_uint8(dev_index), ctypes.c_uint8(chan), ctypes.c_uint8(pin), ctypes.c_uint8(val), ctypes.c_uint8(pin_direction))
        self.lock.release()
        return res

    def _gpio_grp_set(self, dev_index, chan, val, mask):
        self.lock.acquire()
        res = self.MbDrv_dll.gpio_grp_set(ctypes.c_uint8(dev_index), ctypes.c_uint8(chan), ctypes.c_uint8(val), ctypes.c_uint8(mask))
        self.lock.release()
        return res

    def _gpio_grp_set_direction(self, dev_index, chan, direction, dir_mask):
        self.lock.acquire()
        res = self.MbDrv_dll.gpio_grp_set_direction(ctypes.c_uint8(dev_index), ctypes.c_uint8(chan), ctypes.c_uint8(direction), ctypes.c_uint8(dir_mask))
        self.lock.release()
        return res

    def _gpio_pin_set_direction(self, dev_index, chan, pin, direction):
        self.lock.acquire()
        res = self.MbDrv_dll.gpio_pin_set_direction(ctypes.c_uint8(dev_index), ctypes.c_uint8(chan), ctypes.c_uint8(pin), ctypes.c_uint8(direction))
        self.lock.release()
        return res

    def _gpio_pin_get(self, dev_index, chan, pin, pin_direction):
        self.lock.acquire()
        value = ctypes.c_uint8(0)
        value_p = ctypes.pointer(value)
        res = self.MbDrv_dll.gpio_pin_get(ctypes.c_uint8(dev_index), ctypes.c_uint8(chan), ctypes.c_uint8(pin), value_p, ctypes.c_uint8(pin_direction))
        if res != 0:
            self.lock.release()
            return None
        self.lock.release()
        return value_p.contents.value

    def _gpio_grp_get(self, dev_index, chan, direction, dir_mask):
        self.lock.acquire()
        value = ctypes.c_uint8(0)
        value_p = ctypes.pointer(value)
        res = self.MbDrv_dll.gpio_grp_get(ctypes.c_uint8(dev_index), ctypes.c_uint8(chan), value_p, ctypes.c_uint8(direction), ctypes.c_uint8(dir_mask))
        self.lock.release()
        return value_p.contents.value

    def _gpio_close(self, dev_index, chan):
        self.lock.acquire()
        res = self.MbDrv_dll.gpio_close(ctypes.c_uint8(dev_index), ctypes.c_uint8(chan))
        self.lock.release()
        return res

    def _set_vcm(self, dev_index, vcm_mv):
        self.lock.acquire()
        res = self.MbDrv_dll.set_vcm(ctypes.c_uint8(dev_index), ctypes.c_uint16(vcm_mv))
        self.lock.release()
        return res

    def _set_vchp(self, dev_index, vchp_mv):
        self.lock.acquire()
        res = self.MbDrv_dll.set_vchp(ctypes.c_uint8(dev_index), ctypes.c_uint16(vchp_mv))
        self.lock.release()
        return res

    def _get_chpc(self, dev_index):
        self.lock.acquire()
        value = ctypes.c_uint8(0)
        value_p = ctypes.pointer(value)
        res = self.MbDrv_dll.get_chpc(ctypes.c_uint8(dev_index), value_p)
        if res != 0:
            self.lock.release()
            return None
        self.lock.release()
        return value_p.contents.value

    def _set_default_spi_setting(self):
        self.current_cs              = 3
        self.current_pin             = 0x8fdb8fdb
        self.current_mode            = 0
        self.current_cs_active_level = 0
        self.current_clock_rate      = 20000000
        self.current_latency_timer   = 1

    def _set_default_i2c_setting(self):
        self.current_i2c_pin = 0x00000000


# Exported functions

    def version(self):
        return self.mbdrv_version()

    def mbdrv_version(self):
        self.lock.acquire()
        ver_str = self.MbDrv_dll.get_mbdrv_version()
        self.lock.release()
        return ver_str.decode()

    def num_of_channels(self):
        self.lock.acquire()
        res = self.MbDrv_dll.get_num_of_channels()
        self.lock.release()
        return res

    def update_mpsse_channel_info(self):
        num_of_channels = self.num_of_channels()
        if num_of_channels > 0:
            dev_info_array = self._list_devs()
        self._i2c_chaninfo_init()
        return self._spi_chaninfo_init()

    def get_channel_info(self, chan_number):
        num_of_channels = self.num_of_channels()
        if chan_number > (num_of_channels - 1):
            return None
        dev_info_array = self._list_devs()
        chan_info = {'Flags': dev_info_array[chan_number].Flags, 'Type': dev_info_array[chan_number].Type, 'ID': dev_info_array[chan_number].ID, 'LocId': dev_info_array[chan_number].LocId, 
                     'SerialNumber': dev_info_array[chan_number].SerialNumber.decode(), 'Description': dev_info_array[chan_number].Description.decode(), 'ftHandle': dev_info_array[chan_number].ftHandle}
        return chan_info

    def get_channel(self, serial_number):
        return self._spi_chaninfo_get_chan(serial_number)

    def get_board_type(self, board_id):
        desc = self._get_board_type(board_id)
        return desc

    def get_board_id(self, serial_number):
        return self._get_device_id(serial_number)

    def print_dev_info(self, index):
        return self._print_dev_info(index)

    def spi_open(self, board_id, cs=None, clock_rate=None, latency_timer=None, mode=None, pin=None, cs_active_level=None):
        if cs == None:
            cs = self.current_cs
        if clock_rate == None:
            clock_rate = self.current_clock_rate
        if latency_timer == None:
            latency_timer = self.current_latency_timer
        if mode == None:
            mode = self.current_mode
        if pin == None:
            pin = self.current_pin
        if cs_active_level == None:
            cs_active_level = self.current_cs_active_level
        res = self._spi_init(board_id, cs, clock_rate, latency_timer, mode, pin, cs_active_level)
        if res == 0:
            self.current_cs = cs
            self.current_clock_rate = clock_rate
            self.current_latency_timer = latency_timer
            self.current_mode = mode
            self.current_pin = pin
            self.current_cs_active_level = cs_active_level
        return res

    def spi_reconfig(self, board_id, cs, clock_rate=None, latency_timer=None, mode=None, pin=None, cs_active_level=None):
        if clock_rate == None:
            clock_rate = self.current_clock_rate
        if latency_timer == None:
            latency_timer = self.current_latency_timer
        if mode == None:
            mode = self.current_mode
        if pin == None:
            pin = self.current_pin
        if cs_active_level == None:
            cs_active_level = self.current_cs_active_level
        res = self._spi_reconfig(board_id, cs, clock_rate, latency_timer, mode, pin, cs_active_level)
        if res == 0:
            self.current_cs = cs
            self.current_clock_rate = clock_rate
            self.current_latency_timer = latency_timer
            self.current_mode = mode
            self.current_pin = pin
            self.current_cs_active_level = cs_active_level
        return res

    def spi_change_cs(self, board_id, cs, clock_rate=None, latency_timer=None, mode=None, pin=None, cs_active_level=None):
        if clock_rate == None:
            clock_rate = self.current_clock_rate
        if latency_timer == None:
            latency_timer = self.current_latency_timer
        if mode == None:
            mode = self.current_mode
        if pin == None:
            pin = self.current_pin
        if cs_active_level == None:
            cs_active_level = self.current_cs_active_level
        res = self._spi_change_cs(board_id, cs, mode, cs_active_level)
        if res == 0:
            self.current_cs = cs
            self.current_mode = mode
            self.current_cs_active_level = cs_active_level
        return res

    def spi_close(self, board_id):
        self._set_default_spi_setting()
        return self._spi_close(board_id)

    def i2c_open(self, board_id, pin=None):
        self._set_default_i2c_setting()
        if pin == None:
            pin = self.current_i2c_pin
        res = self._i2c_init(board_id, pin)
        if res == 0:
            self.current_i2c_pin = pin
        return res

    def i2c_close(self, board_id):
        self._set_default_i2c_setting()
        return self._i2c_close(board_id)

    def gpio_open(self, board_id, chan, pin):
        return self._gpio_init(board_id, chan, pin)

    def gpio_close(self, board_id, chan):
        return self._gpio_close(board_id, chan)

    def spi_read(self, board_id, chip_select, send_data, rcv_buffer_size):
        if self.current_cs != chip_select:
            res = self._spi_change_cs(board_id, chip_select, self.current_mode, self.current_cs_active_level)
        data = self._spi_read(board_id, send_data, rcv_buffer_size)
        return data

    def spi_write(self, board_id, chip_select, send_data):
        if self.current_cs != chip_select:
            res = self._spi_change_cs(board_id, chip_select, self.current_mode, self.current_cs_active_level)
        res = self._spi_write(board_id, send_data)
        return res

    def spi_read_write(self, board_id, chip_select, send_data):
        if self.current_cs != chip_select:
            res = self._spi_change_cs(board_id, chip_select, self.current_mode, self.current_cs_active_level)
        res = self._spi_read_write(board_id, send_data)
        return res

    def i2c_read(self, board_id, device_address, rcv_buffer_size, start_condition=True, stop_condition=True, 
                       nack_last_byte=False, multi_byte=False, multi_bit=False, ignore_address=False):
        return self._i2c_read(board_id, device_address, rcv_buffer_size, start_condition, stop_condition, nack_last_byte,
                              multi_byte, multi_bit, ignore_address)

    def i2c_write(self, board_id, device_address, send_data, send_data_size, start_condition=True, stop_condition=True, 
                        break_on_nack=False, multi_byte=False, multi_bit=False, ignore_address=False):
        return self._i2c_write(board_id, device_address, send_data, start_condition, stop_condition, break_on_nack,
                                multi_byte, multi_bit, ignore_address)

    def i2c_scan(self, board_id, printit=False, start_device_address=0x00, end_device_address=0x7f):
        found_dev = []
        if start_device_address > end_device_address:
            start_device_address = 0
        if start_device_address > 0x7f:
            start_device_address = 0
        if end_device_address > 0x7f:
            end_device_address = 0x7f
        for dev_addr in range(start_device_address, end_device_address+1):
            res = self._i2c_read(board_id, dev_addr, 1, True, True, False, False, False, False)
            if res != None:
                found_dev.append(dev_addr)
                if printit:
                    print('addr: 0x{:02x} (shifted 0x{:02x}) detected'.format(dev_addr, dev_addr<<1))
        return found_dev

    def gpio_set(self, board_id, sig_num, value, dir=1, pulse=False, pulse_duration=1):
        return self._set_signal(board_id, sig_num, value, dir, pulse, pulse_duration)

    def gpio_grp_set(self, board_id, grp, value, dir=0xff, mask=0xff):
        return self._set_grp_signal(board_id, grp, value, dir, mask)

    def gpio_grp_get(self, board_id, grp, dir=0, mask=0):
        return self._get_grp_signal(board_id, grp, dir, mask)

    def gpio_get(self, board_id, sig_num, dir=2):
        return self._get_signal(board_id, sig_num, dir)

    def gpio_dir_get(self, board_id, sig_num):
        return self._get_signal_direction(board_id, sig_num)

    def gpio_grp_dir_get(self, board_id, grp):
        res = self._get_signal_grp_direction(board_id, grp)
        if res == -1:
            return None
        return res

    def gpio_dir_set(self, board_id, sig_num, dir):
        if dir > 1:
            return None
        return self._set_signal_direction(board_id, sig_num, dir)

    def gpio_grp_dir_set(self, board_id, grp, dir, mask=0xff):
        return self._set_signal_grp_direction(board_id, grp, dir, mask)

    def set_vcm_dac(self, board_id, voltage_mv):
        return self._set_vcm(board_id, voltage_mv)
