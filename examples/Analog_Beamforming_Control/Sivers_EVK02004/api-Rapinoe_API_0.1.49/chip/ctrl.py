import gpio
import evk_logger

class Ctrl():

    __instance = None
    _state = {'SLEEP': 0b0001, 'SX':   0b1001,
              'RH':    0b0000, 'RV':   0b0010, 'RVRH': 0b0100, 'RHRV': 0b0100,
              'RVTH':  0b0110, 'THRV': 0b0110,
              'TH':    0b1000, 'TV':   0b1010, 'TVTH': 0b1110, 'THTV': 0b1110,
              'TVRH':  0b1100, 'RHTV': 0b1100
             }
    _cmd_3 = {'BEAM':0, 'GAIN':1, 'FREQ':2, 'MODE':3, 'STATE':3, 0:0, 1:1, 2:2, 3:3, '0':0, '1':1, '2':2, '3':3}
    _cmd_2 = {'FREQ':0, 'RX':2, 'TX':3, 0:0, 1:1, 2:2, 3:3, '0':0, '1':1, '2':2, '3':3}
    _cmd_0 = {'RX':0, 'TX':1, 0:0, 1:1, '0':0, '1':1, True:1, False:0}
    _sync  = {True:1, 1:1, 'TRUE':1, '1':1, False:0, 0:0, 'FALSE':0, '0':0}
    _tx_rx = {True:1, 1:1, 'TRUE':1, '1':1, 'TX':1, False:0, 0:0, 'FALSE':0, '0':0, 'RX':0}
    _true_false  = {True:1, 1:1, 'True':1, '1':1, False:0, 0:0, 'False':0, '0':0}
    _ctrl_mode = {'mode':0, 'enable':0}

    def __new__(cls, conn, spi):
        if cls.__instance is None:
            cls.__instance = super(Ctrl, cls).__new__(cls)
            cls.__instance.__initialized = False
        return cls.__instance

    def __init__(self, conn, spi):
        self._conn = conn
        self._spi  = spi
        self._gpio = gpio.Gpio(self._conn)
        self.CTRL_MODES  = self._conn.config.CTRL_MODES
        self.CTRL_DATA   = self._conn.config.CTRL_DATA
        self.CTRL_STROBE = self._conn.config.CTRL_STROBE

    def set_notreset(self, rap_addr, value):
        self._gpio.set(self._conn.config.DEVICE_NRESET_PIN, value)


    @evk_logger.log_call
    def set_mode(self, devs, mode, enable=1):
        if isinstance(mode,dict):
            enable = mode['enable']
            mode   = mode['mode']
        enable = self._true_false[enable]
        if (mode in self.CTRL_MODES):
            self._spi.wr(devs, 'ctrl_gpio_config',((mode&3)<<4)| enable)
            self._ctrl_mode = {'mode':mode&3, 'enable': enable}
            if (self.CTRL_DATA['grp'] is not None):
                self._gpio.grp_dir_set(grp=self.CTRL_DATA['grp'],  io=self.CTRL_DATA['pins'][self._ctrl_mode['mode']],  mask=self.CTRL_DATA['pins'][self._ctrl_mode['mode']])
            if (self.CTRL_STROBE['grp'] is not None):
                self._gpio.grp_dir_set(grp=self.CTRL_STROBE['grp'],io=self.CTRL_STROBE['pins'][self._ctrl_mode['mode']],mask=self.CTRL_STROBE['pins'][self._ctrl_mode['mode']])
        else:
            evk_logger.evk_logger.log_error('CTRL mode {} not supported on this platform. Supported modes are {}'.format(mode, self.CTRL_MODES))
        return self._ctrl_mode


    @evk_logger.log_call
    def get_mode(self, devs):
        res=self._spi.rd(devs, 'ctrl_gpio_config')
        self._ctrl_mode = {'mode':(res>>4)&3, 'enable': res&1}
        return self._ctrl_mode


    @evk_logger.log_call
    def send(self, devs, cmd=None, state=None, index=None, sync=1):
        if not self._ctrl_mode['enable']:
            self.get_mode(devs)
        
        if self._ctrl_mode['enable']:
            if (self._ctrl_mode['mode'] == 3) and (self._ctrl_mode['mode'] in self.CTRL_MODES):
                if (cmd == None) or (state == None) or (index == None):
                    evk_logger.evk_logger.log_error('cmd, state and index need to be specified.')
                    return {'header':None, 'data':None}

                if isinstance(cmd,str):
                    cmd  = cmd.upper()
                if isinstance(state,str):
                    state = state.upper()
                if isinstance(sync,str):
                    sync = sync.upper()
                    
                cmd   = self._cmd_3[cmd]
                state = self._state[state]
                sync  = self._sync[sync]

                header = (cmd<<5)|(sync<<4)|state|(index>>7)
                data   = index&0x7F
                self._gpio.grp_set(self.CTRL_DATA['grp']  ,header<<self.CTRL_DATA['shift'],mask=self.CTRL_DATA['pins'][3])
                self._gpio.grp_set(self.CTRL_STROBE['grp'],self.CTRL_STROBE['pins'][3]    ,mask=self.CTRL_STROBE['pins'][3])
                self._gpio.grp_set(self.CTRL_DATA['grp']  ,data<<self.CTRL_DATA['shift']  ,mask=self.CTRL_DATA['pins'][3])
                self._gpio.grp_set(self.CTRL_STROBE['grp'],0                              ,mask=self.CTRL_STROBE['pins'][3])
            elif (self._ctrl_mode['mode'] == 2) and (self._ctrl_mode['mode'] in self.CTRL_MODES):
                if (cmd == None):
                    evk_logger.evk_logger.log_error('cmd needs to be specified.')
                    return {'header':None, 'data':None}

                if isinstance(cmd,str):
                    cmd  = cmd.upper()
                cmd   = self._cmd_2[cmd]

                header = (cmd<<5)|(sync<<4)
                data   = 0
                self._gpio.grp_set(self.CTRL_DATA['grp']  ,header<<self.CTRL_DATA['shift'],mask=self.CTRL_DATA['pins'][2])
                self._gpio.grp_set(self.CTRL_STROBE['grp'],self.CTRL_STROBE['pins'][2]    ,mask=self.CTRL_STROBE['pins'][2])
                self._gpio.grp_set(self.CTRL_STROBE['grp'],0                              ,mask=self.CTRL_STROBE['pins'][2])
            elif (self._ctrl_mode['mode'] == 1) and (self._ctrl_mode['mode'] in self.CTRL_MODES):
                header = 0
                data   = 0
                self._gpio.grp_set(self.CTRL_STROBE['grp'],self.CTRL_STROBE['pins'][1]    ,mask=self.CTRL_STROBE['pins'][1])
                self._gpio.grp_set(self.CTRL_STROBE['grp'],0                              ,mask=self.CTRL_STROBE['pins'][1])
            elif (self._ctrl_mode['mode'] == 0) and (self._ctrl_mode['mode'] in self.CTRL_MODES):
                if (cmd == None):
                    evk_logger.evk_logger.log_error('cmd needs to be specified.')
                    return {'header':None, 'data':None}

                if isinstance(cmd,str):
                    cmd  = cmd.upper()
                cmd    = self._cmd_0[cmd]

                header = 0
                data   = 0
                if cmd:
                    self._gpio.grp_set(self.CTRL_STROBE['grp'],self.CTRL_STROBE['pins'][0],mask=self.CTRL_STROBE['pins'][0])
                else:
                    self._gpio.grp_set(self.CTRL_STROBE['grp'],0                          ,mask=self.CTRL_STROBE['pins'][0])
            else:
                header = None
                data   = None
                evk_logger.evk_logger.log_error('CTRL mode is incorrect or not supported on this platform. Supported modes are {}'.format(self.CTRL_MODES))
                evk_logger.evk_logger.log_error('Please set correct ctrl mode using set_mode(devs, mode[, enable=1])')
        else:
            header = None
            data   = None
            evk_logger.evk_logger.log_error('CTRL interface is not enabled. Please enable ctrl mode using set_mode(devs, mode[, enable=1])')
        return {'header':header, 'data':data}
