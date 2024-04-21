def get_pin(pin):
    return(host.ctrl.conn.mb.gpio_get(host.ctrl.conn.board_id,pin), host.ctrl.conn.mb.gpio_dir_get(host.ctrl.conn.board_id,pin))

def set_pin(pin,val,io=None):
    host._conn.mb.gpio_set(host.ctrl.conn.board_id,pin,val,io)
    return get_pin(pin)

def dump_pins(start,end):
    for i in range(start,end):
        print(i, get_pin(i))


CTRL_7_A = host.ctrl.conn.config.CTRL_7_A
host.spi.wrrd(rap0,'ctrl_gpio_config',{'mode':1, 'en':1})
set_pin(CTRL_7_A, 1, 'O')
