
from threading import Lock
from random import randint

import evk_logger

# Use host.spi.register_map.regs to get address, length, desc ...

class GuiData(object):

    def __init__(self, gui_handler, dev):
        self.gh = gui_handler
        self.dev = dev
        self.lock = Lock()
        self._register_groups = {}
        self._registers = {}
        self._group_registers()
        self._read_all_groups()

    def _group_registers(self):
        for reg in self.gh.host.spi.register_map.regs.keys():
            try:
                self._register_groups[self.gh.host.spi.register_map.regs[reg]['group']].append(reg)
            except KeyError:
                self._register_groups[self.gh.host.spi.register_map.regs[reg]['group']] = [reg]
            self._registers[reg] = 0

    def _read_all_groups(self):
        exclude_groups = ['BF_RAM', 'RX_RAM', 'TX_RAM']
        evk_logger.evk_logger.set_max_call_log_level(-1)
        for group in list(self._register_groups.keys()):
            if not group in exclude_groups:
                self._update_register_group_data(group)
        evk_logger.evk_logger.set_max_call_log_level(0)

    def _update_register_group_data(self, group):
        self.lock.acquire()
        evk_logger.evk_logger.set_max_call_log_level(-1)
        try:
            for reg in self._register_groups[group]:
                self._registers[reg] = self.gh.host.spi.rd(self.dev, reg)
        except:
            print ('ERROR: _update_register_group_data!')
        evk_logger.evk_logger.set_max_call_log_level(0)
        self.lock.release()

    def get_register_group(self, group):
        if group in self.register_groups:
            return self.register_groups[group]
        return None

    def read_register(self, reg_name):
        try:
            return self._registers[reg_name]
        except:
            return None

    def write_register(self, reg_name, value):
        try:
            self.gh.host.spi.wr(self.dev, reg_name, value)
            if isinstance(value, int):
                self._registers[reg_name] = value
        except:
            print ('ERROR: write_register!')

    def read_temperature(self, src):
        evk_logger.evk_logger.set_max_call_log_level(-1)
        t = self.gh.host.chip.temp.get(self.dev, src, formatit='temp', printit=False)
        evk_logger.evk_logger.set_max_call_log_level(0)
        return t

    def read_adc(self, amux_src):
        return self.gh.host.chip.adc.get_data(self.dev, amux_src)

    def read_ram(self, ram, row):
        return self.gh.host.chip.ram.rd(self.dev, ram, row)

    def write_ram(self, ram, row, value):
        return self.gh.host.chip.ram.wr(self.dev, ram, row, value)

    def read_ram_complete(self, ram, formatit):
        return self.gh.host.chip.ram.dump(self.dev, ram, formatit=formatit, printit=False)

    def sync_ram(self, txrx, polarization):
        """_summary_

        Args:
            txrx (string): Should be 'TX_RAM' or 'RX_RAM'
            polarization (string): Should be 'V', 'H', 'VH' or 'HV'
        """
        #tx_control_reg_mode
        txrx = txrx.upper()
        polarization = polarization.upper()
        print('Sync', txrx, polarization)
        SYNC_GAIN = 0b01 << 13
        SYNC      = 0b1  << 12

        #host.spi.wrrd(rap0,'trx_control_reg',0+(14<<8)+(1<<12)+(0<<13))  # beam index 0, w sync

        #host.spi.wrrd(rap0,'trx_control_reg',0+(14<<8)+(1<<12)+(1<<13))  # gain index 0 Tx V-pol + H-pol, w sync

        #host.spi.wrrd(rap0,'trx_control_reg',3+(14<<8)+(1<<12)+(3<<13))  # mode TX, w sync


