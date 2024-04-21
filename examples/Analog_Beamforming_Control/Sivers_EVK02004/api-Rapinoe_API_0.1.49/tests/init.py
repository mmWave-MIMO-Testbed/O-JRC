import rapinoe
from common import *

#raps = rapinoe.Rapinoe('SNSP210088')
raps = rapinoe.Rapinoe('SN0341')
rap0 = raps._conn.mb.bsp.rap0
raps.reset(rap0)

print("chip_id:     ", fhex(raps.spi.rd(rap0, 'chip_id'), 8))
print("bist_config: ", raps.spi.wrrd(rap0, 'bist_config', 1))
print("biastop_en:  ", raps.spi.wrrd(rap0, 'biastop_en', 0x20))
