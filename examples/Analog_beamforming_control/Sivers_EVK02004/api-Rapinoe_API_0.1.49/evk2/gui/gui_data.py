
from threading import Lock
from random import randint
import rpyc

# Use host.spi.register_map.regs to get address, length, desc ...

class GuiData(object):

    def __init__(self, dev, port):
        self.dev = dev
        self.lock = Lock()
        self._register_groups = {}
        self._registers = {}

        self.rem_evk = rpyc.connect('localhost', port, config={'allow_public_attrs': True})
        self.rem_evk._config['sync_request_timeout'] = 240
        self.rem_evk = self.rem_evk.root

        self._group_registers()
        self._read_all_groups()

    def get_register_fields(self, reg_name):
        return self.rem_evk.get_register_fields(reg_name)

    def get_register_field(self, reg_name, field):
        return self.rem_evk.get_register_field(reg_name, field)

    def _group_registers(self):
        register_map_keys = self.rem_evk.get_register_map_keys()
        self.register_map_regs = self.rem_evk.get_register_map_regs()
        for reg in register_map_keys:
            try:
                self._register_groups[self.register_map_regs[reg]['group']].append(reg)
            except KeyError:
                self._register_groups[self.register_map_regs[reg]['group']] = [reg]
            self._registers[reg] = 0

    def get_register_map_regs(self):
        return self.register_map_regs

    def _read_all_groups(self):
        exclude_groups = ['BF_RAM', 'RX_RAM', 'TX_RAM']
        for group in list(self._register_groups.keys()):
            if not group in exclude_groups:
                self._update_register_group_data(group)

    def _update_register_group_data(self, group):
        self.lock.acquire()
        try:
            for reg in self._register_groups[group]:
                self._registers[reg] = self.rem_evk.read_register(self.dev, reg)
        except:
            print ('ERROR: _update_register_group_data!')
        self.lock.release()

    def get_register_group(self, group):
        if group in self.register_groups:
            return self.register_groups[group]
        return None

    def read_register(self, reg_name):
        try:
            return self.rem_evk.read_register(self.dev, reg_name)
        except:
            return None

    def write_register(self, reg_name, value):
        try:
            self.rem_evk.write_register(self.dev, reg_name, value)
            if isinstance(value, int):
                self._registers[reg_name] = value
        except:
            print ('ERROR: write_register!')

    def read_temperature(self, src):
        return self.rem_evk.get_temp(self.dev, src)

    def read_adc(self, amux_src):
        return self.rem_evk.get_adc_data(self.dev, amux_src)

    def read_ram(self, ram, row):
        return self.rem_evk.read_ram(self.dev, ram, row)

    def write_ram(self, ram, row, value):
        return self.rem_evk.write_ram(self.dev, ram, row, value)

    def read_ram_complete(self, ram, formatit):
        return self.rem_evk.read_ram_complete(self.dev, ram, formatit=formatit)

    def ram_fill(self, table_id, filename):
        return self.rem_evk.ram_fill(self.dev, table_id, filename)

    def sync_ram(self, txrx, polarization):
        """_summary_

        Args:
            txrx (string): Should be 'TX_RAM' or 'RX_RAM'
            polarization (string): Should be 'V', 'H', 'VH' or 'HV'
        """
        return
        #tx_control_reg_mode
        txrx = txrx.upper()
        polarization = polarization.upper()
        print('Sync', txrx, polarization)
        SYNC_GAIN = 0b01 << 13
        SYNC      = 0b1  << 12

        #host.spi.wrrd(rap0,'trx_control_reg',0+(14<<8)+(1<<12)+(0<<13))  # beam index 0, w sync

        #host.spi.wrrd(rap0,'trx_control_reg',0+(14<<8)+(1<<12)+(1<<13))  # gain index 0 Tx V-pol + H-pol, w sync

        #host.spi.wrrd(rap0,'trx_control_reg',3+(14<<8)+(1<<12)+(3<<13))  # mode TX, w sync

    def exec_command(self, command):
        command = command.replace('__RAP__', 'self._host.{}'.format(self.dev))
        return self.rem_evk.run_command(command)

    def reset(self):
        self.rem_evk.reset(self.dev)


