import sys
import time
import beamSweep
import hunter 
hunter.trace(module='posixpath', action=hunter.CallPrinter)

process_tx = beamSweep.beamSweep_start(1, "T582306548", "rapvalbsp", None, None, None, None, None, None, "tx_setup_25Ghz")
process_rx = beamSweep.beamSweep_start(2, "T582306549", "rapvalbsp", None, None, None, None, None, None, "rx_setup_25Ghz")
   
if process_tx  is None:
   sys.exit(1)  # Exeit the program if initialization failed

if process_rx is None:
   sys.exit(1)  # Exeit the program if initialization failed

beam_index = 0
tpol = 'th'
rpol = 'rh'

for ii in range(63):
    # Format the command string with the current beam_index and tpol
    command_tx = f"host.chip.tx.beam(rap0, {beam_index}, '{tpol}')"
    command_rx = f"host.chip.rx.beam(rap0, {beam_index}, '{rpol}')"
    # inject command to subprocess
    process_tx.update_cmd(command_tx)
    process_rx.update_cmd(command_rx)
    time.sleep(1)  # Sleep to allow processing time between commands
    beam_index += 1
    print(f'Config TX beam index: {beam_index}')

process_tx.stop()
process_rx.stop()


