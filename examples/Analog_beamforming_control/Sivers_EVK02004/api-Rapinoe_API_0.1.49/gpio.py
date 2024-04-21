import evk_logger
from common import fhex

class Gpio():

    __instance = None
    __dir     = {0:0, 1:1, '0':0, '1':1, 'I':0, 'O':1, 'i':0, 'o':1}
    __grp     = {0:0, 1:1, 2:2, 3:3, '0':0, '1':1, '2':2, '3':3, 'A':0, 'B':1, 'C':2, 'D':3, 'a':0, 'b':1, 'c':2, 'd':3}
    __dir_txt = {0:'I', 1:'O', '0':'I', '1':'O'}
    def __new__(cls, conn):
        if cls.__instance is None:
            cls.__instance = super(Gpio, cls).__new__(cls)
            cls.__instance.__initialized = False
        return cls.__instance

    def __init__(self, conn):
        self.conn = conn

    def get(self,pin):
        pin = int(pin)
        return self.conn.mb.gpio_get(self.conn.board_id,pin)

    def grp_get(self, grp):
        grp = Gpio.__grp[grp]
        return self.conn.mb.gpio_grp_get(self.conn.board_id, grp)

    def dir_get(self,pin):
        pin = int(pin)
        return Gpio.__dir_txt[self.conn.mb.gpio_dir_get(self.conn.board_id,pin)]

    def grp_dir_get(self, grp):
        grp = Gpio.__grp[grp]
        grp_dir = self.conn.mb.gpio_grp_dir_get(self.conn.board_id, grp)
        res = ''
        for i in range(8):
            if grp_dir & (1<<i):
                res = 'O' + res
            else:
                res = 'I' + res
        return res

    def set(self,pin,val,io=None):
        pin = int(pin)
        if not io == None:
            io = Gpio.__dir[io]
            self.conn.mb.gpio_set(self.conn.board_id,pin,val,io)
        else:
            self.conn.mb.gpio_set(self.conn.board_id,pin,val)
        return self.get(pin)

    def grp_set(self, grp, val, io=None, mask=0xff):
        grp = Gpio.__grp[grp]
        if not io is None:
            if not isinstance(io,int):
                io = int(io.replace('I','0').replace('O', '1'), 2)
            if not isinstance(mask,int):
                mask = int(mask.replace('I','0').replace('O', '1'), 2)
            self.conn.mb.gpio_grp_set(self.conn.board_id, grp, val, io, mask)
        else:
            self.conn.mb.gpio_grp_set(self.conn.board_id, grp, val)
        return self.grp_get(grp)

    def dir_set(self,pin,io):
        pin = int(pin)
        io = Gpio.__dir[io]
        return self.conn.mb.gpio_dir_set(self.conn.board_id,pin,io)

    def grp_dir_set(self, grp, io, mask=0xff):
        grp = Gpio.__grp[grp]
        if not isinstance(io,int):
            io = int(io.replace('I','0').replace('O', '1'), 2)
        if not isinstance(mask,int):
            mask = int(mask.replace('I','0').replace('O', '1'), 2)
        self.conn.mb.gpio_grp_dir_set(self.conn.board_id, grp, io, mask)
        return self.grp_dir_get(grp)

    def dump(self,start,end=None):
        if isinstance(start,list):
            pin_list = start
        elif end is None:
            if isinstance(start,int):
                pin_list = [start]
            else:
                pin_list = start
        else:
            pin_list = range(int(start),int(end))
        for pin in pin_list:
            print('{:2} {} {}'.format(pin, self.get(pin), self.dir_get(pin)))

    def grp_dump(self,grp_list):
        if isinstance(grp_list,int):
            grp_list = [grp_list]
        for grp in grp_list:
            print('{:1} {} {}'.format(grp, fhex(self.grp_get(grp),2), self.grp_dir_get(grp)))
