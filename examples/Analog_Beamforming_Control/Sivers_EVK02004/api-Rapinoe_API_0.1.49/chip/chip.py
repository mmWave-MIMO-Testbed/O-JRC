import os
import chip_info
import ctrl
import evk_logger
import i2c
import rapspi
import rcu
import ref_clk
import register
import trx
from common import *
from env_config import env_config

class Chip():
    __instance = None

    def __new__(cls, conn, fref, indent=None):
        if cls.__instance is None:
            cls.__instance = super(Chip, cls).__new__(cls)
            cls.__instance.__initialized = False
        return cls.__instance

    def __init__(self, conn, fref, indent=None):
        if self.__initialized != True:
            if indent is None:
                self.indent = evk_logger.evk_logger._indent
            else:
                self.indent = indent
            self.fref = fref
            # Starting with R3 register map
            self._reg_map   = register.Register(os.path.join(env_config.register_map_path(),'reg_map.h5'))
            self._conn      = conn
            self.spi        = rapspi.RapSPI(self._conn, self._reg_map)
            self.ctrl       = ctrl.Ctrl(self._conn, self.spi)
            self._chip_info = chip_info.Chip_info(self.spi,indent=self.indent+2)
            self.spi._set_chip_info(self._chip_info)
            num_devs        = self._chip_info.get_num_devs()
            print("[CHIP]The num_devs:{:}".format(num_devs))
            if num_devs == 0:
                evk_logger.evk_logger.log_info('Expecting 0 devices.',self.indent)
            elif num_devs == 1:
                evk_logger.evk_logger.log_info('Expecting {} device. Trying to connect to it ...'.format(num_devs),self.indent)
            else:
                evk_logger.evk_logger.log_info('Expecting {} devices. Trying to connect to them ...'.format(num_devs),self.indent)

            self.__initialized = True


    @evk_logger.log_call
    def init(self, devs, grps=['CHIP','EN VCC HIGH w OVR'], printit=False):
        """Initialise registers.
        Init values are defined in the file init.py.
        Each set of init values can be grouped depending on use case, e.g
        only init values for the group 'SYNTH'.
        The default group 'CHIP' must always exist.
        Examples:
        # Init chip rap0 with values from group 'CHIP'
        init(rap0)
        # Init chip rap0 with values from groups ADC and EFC
        init(rap0, ['ADC', 'EFC'])
        # Init chip rap0 with values from group 'MY GROUP' given on command line
        init(rap0, {'MY GROUP': {'bist_config': {'cmd': 'WR', 'data' : 0x20}}})
        # Init chips rap0 and rap1 with values from group 'CHIP'
        init([rap0, rap1],'CHIP')
        """
        if grps is not None:
            return self._init.set(devs, grps, printit)

    @evk_logger.log_call
    def init_get(self, devs, grps=None, printit=False):
        return self._init.get(devs, grps, printit)

    @evk_logger.log_call
    def init_get_grps(self, devs, printit=False):
        return self._init.get_grps(devs, printit)

    @evk_logger.log_call
    def info(self, devs, printit=False):
        return self._chip_info.get(devs, printit)

    @evk_logger.log_call
    def override_mode(self, devs, enable):
        self.rx.override_mode(devs, enable)
        self.tx.override_mode(devs, enable)

    def stage2_setup(self):
        self._init      = init.Init(self.spi)
        self.amux       = amux.Amux(self.spi)
        self.adc        = adc.Adc(self.spi)
        self.i2c        = i2c.I2c(self.spi, self._chip_info)
        self.ram        = ram.Ram(self.spi)
        self.rcu        = rcu.Rcu(self.spi)
        self.ref_clk    = ref_clk.Ref_clk(self.spi, self.fref)
        self.synth      = synth.Synth(self.spi, self.ram, self.fref)
        self.temp       = temp.Temp(self.spi)
        self.rx         = rx.Rx(self.spi, self.ram)
        self.rx.dco     = rx_dco.RxDco(self.rx, self.ram, self.adc)
        if rx_filtcal != None:
            self.rx.filtcal = rx_filtcal.RxFiltCal(self.spi)
        if rx_lvl_det != None:
            self.rx.lvl_det = rx_lvl_det.RxLvlDet(self.spi)
        self.tx         = tx.Tx(self.spi, self.ram)
        self.tx.dco     = tx_dco.TxDco(self)
        if tx_dco_pdet != None:
            self.tx.dco_det = tx_dco_pdet.TxDcoPdet(self)
        if fir != None:
            self.fir = fir.Fir(self.spi)
        self.trx        = trx.Trx(self.spi)

    def update_revision_data(self, chip_id):
        self.import_modules(chip_id)
        self.select_register_map(chip_id)
        self.stage2_setup()

    def select_register_map(self, chip_id):
        if chip_id == 0x12532212 or chip_id == 0x02741812:
            self._reg_map._Register__instance = None
            self._reg_map = register.Register(os.path.join(env_config.register_map_path(),'reg_map_r5.h5'))
            self.spi.update_reg_groups()
            print('    R5 register map')

    def import_modules(self, chip_id):
        global init
        global synth
        global rx
        global tx
        global ram
        global rx_dco
        global tx_dco
        global tx_dco_pdet
        global amux
        global adc
        global temp
        global fir
        global rx_filtcal
        global rx_lvl_det

        if chip_id == 0x12532212 or chip_id == 0x02741812:
            import r5.init as init
            print('    Imported R5 init')
            import block.r5.synth as synth
            print('    Imported R5 synth')
            import block.subblock.r5.temp as temp
            print('    Imported R5 temp')
            import block.r5.rx as rx
            print('    Imported R5 rx')
            import block.r5.tx as tx
            print('    Imported R5 tx')
            import block.r5.fir as fir
            print('    Imported R5 fir')
            import block.subblock.r5.ram as ram
            print('    Imported R5 ram')
            import block.subblock.r5.rx_dco as rx_dco
            print('    Imported R5 rx_dco')
            import block.subblock.r5.tx_dco as tx_dco
            print('    Imported R5 tx_dco')
            import block.subblock.r5.tx_dco_pdet as tx_dco_pdet
            print('    Imported R5 tx_dco_pdet')
            import block.subblock.r5.amux as amux
            print('    Imported R5 amux')
            import block.subblock.r5.adc as adc
            print('    Imported R5 adc')
            import block.subblock.r5.rx_filtcal as rx_filtcal
            print('    Imported R5 rx_filtcal')
            import block.subblock.r5.rx_lvl_det as rx_lvl_det
            print('    Imported R5 rx_lvl_det')
        else:
            import init as init
            import block.synth as synth
            import block.subblock.temp as temp
            import block.rx as rx
            import block.tx as tx
            import block.subblock.ram as ram
            import block.subblock.rx_dco as rx_dco
            import block.subblock.tx_dco as tx_dco
            tx_dco_pdet = None
            fir = None
            rx_filtcal = None
            rx_lvl_det = None
            import block.subblock.amux as amux
            import block.subblock.adc as adc


