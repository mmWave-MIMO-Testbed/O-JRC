import sys
import time
import beamSweep

process_tx = beamSweep.beamSweep_start(1, "T582306548", "rapvalbsp", None, None, None, None, None, None, "beamSweep_tx_setup")
    
if process_tx is None:
    sys.exit(1)  # Exit the program if initialization failed

beam_index = 0
tpol = 'tv'

for ii in range(64):
    # Format the command string with the current beam_index and tpol
    command = f"host_instance.chip.tx.beam(rap0, {beam_index}, '{tpol}')"
    process_tx.update_cmd(command)
    time.sleep(0.02)  # Sleep to allow processing time between commands
    beam_index += 1
    print(f'Config TX beam index: {beam_index}')

process_tx.stop()


