import copy
import rpyc

class MyService(rpyc.Service):
    def __init__(self, host):
        self._host = host
        print(self._host)

    def on_connect(self, conn):
        # code that runs when a connection is created
        # (to init the service, if needed)
        pass

    def on_disconnect(self, conn):
        # code that runs after the connection has already closed
        # (to finalize the service, if needed)
        pass

    def exposed_get_answer(self): # this is an exposed method
        return 42

    exposed_the_real_answer_though = 43     # an exposed attribute

    def exposed_get_question(self):  # while this method is not exposed
        return "what is the airspeed velocity of an unladen swallow?"

    def exposed_reset(self, dev):
        self._host.reset(eval('self._host.'+dev))

    def exposed_tx_dco_calibrate(self, dev):
        self._host.chip.tx.dco.calibrate(eval('self._host.'+dev), 'IF', 'V', True)
        
    def exposed_get_host(self):
        return self._host
        
    def exposed_read_register(self, dev, reg_name):
        return self._host.spi.rd(eval('self._host.'+dev), reg_name)
        
    def exposed_get_reg_groups_keys(self):
        return self._host.spi.reg_groups.keys()
        
    def exposed_get_reg_groups(self):
        return self._host.spi.reg_groups
        
    def exposed_get_register_map(self):
        return self._host.spi.register_map
        
    def exposed_get_register_map_regs(self):
        return self._host.spi.register_map.regs
        
    def exposed_get_register_map_keys(self):
        return self._host.spi.register_map.regs.keys()
        
    def exposed_get_register_attribs(self, reg_name):
        return self._host.spi.register_map.regs[reg_name]
        
    def exposed_get_register_fields(self, reg_name):
        return self._host.spi.register_map.reg_map[reg_name].keys()
        
    def exposed_get_register_field(self, reg_name, field):
        return self._host.spi.register_map.reg_map[reg_name][field]
        
    def exposed_write_register(self, dev, reg_name, value):
        return self._host.spi.wr(eval('self._host.'+dev), reg_name, value)
        
    def exposed_get_temp(self, dev, src):
        return self._host.chip.temp.get(eval('self._host.'+dev), src, printit=False)
        
    def exposed_write_ram(self, dev, ram_name, row, value):
        return self._host.chip.ram.wr(eval('self._host.'+dev), ram_name, row, value)
        
    def exposed_read_ram(self, dev, ram_name, row):
        return self._host.chip.ram.rd(eval('self._host.'+dev), ram_name, row)
        
    def exposed_get_adc_data(self, dev, amux_src):
        return self._host.chip.adc.get_data(eval('self._host.'+dev), amux_src)
        
    def exposed_read_ram_complete(self, dev, ram, formatit):
        return self._host.chip.ram.dump(eval('self._host.'+dev), ram, formatit=formatit, printit=False)
        
    def exposed_run_command(self, command):
        return eval(command)

if __name__ == "__main__":
    from rpyc.utils.server import ThreadedServer
    t = ThreadedServer(MyService, port=18861)
    t.start()