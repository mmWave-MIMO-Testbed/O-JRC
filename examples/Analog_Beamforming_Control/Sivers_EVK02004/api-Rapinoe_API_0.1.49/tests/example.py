import rapinoe
from common import *

rap_env = rapinoe.Rapinoe('SNSP210088')
rap0    = rap_env._conn.mb.bsp.rap0


fhex(rap_env.spi.rd(rap0,'chip_id'))

rap_env.spi.dump(rap0)

rap_env.ctrl.set_ctrl_a(rap0, 0, 1)
