import sys
import time
import beamSweep
import hunter 

with open('hunter_output.log','a') as f:

   hunter.trace(module='posixpath', action=hunter.CallPrinter(stream=f))


   # choose polarization for TX and RX
   tpol = 'th'
   rpol = 'rh'


   # initialize TX
   process_tx = beamSweep.beamSweep_start(1, "T582306548", "rapvalbsp", None, None, None, None, None, None, "tx_setup_25Ghz")

   if process_tx  is None:
      sys.exit(1)  # Exeit the program if initialization failed

   # initialize RX
   process_rx = beamSweep.beamSweep_start(2, "T582306549", "rapvalbsp", None, None, None, None, None, None, "rx_setup_25Ghz")
      
   if process_rx is None:
      sys.exit(1)  # Exeit the program if initialization failed


   # settings for TX and Rx gains
   tx_gain_index = 0
   tx_gain_com_h = 32
   tx_gain_bf_h = 64

   rx_gain_index = 0
   rx_lna_gain_h = 12
   rx_bf_gain_h = 54
   rx_com_gain_h = 54

   command_tx_chip_ram_wr = f"host.chip.ram.wr(rap0, 'tx_ram_h', {tx_gain_index}, ({tx_gain_bf_h}<<6)+({tx_gain_com_h}<<0))"
   command_tx_gain = f"host.chip.tx.gain_rf(rap0, {tx_gain_index}, 'TH')"

   command_rx_chip_ram_wr = f"host.chip.ram.wr(rap0, 'rx_ram_h', {rx_gain_index}, ({rx_lna_gain_h}<<61)+({rx_bf_gain_h}<<55)+({rx_com_gain_h}<<49))"
   command_rx_gain = f"host.chip.rx.gain(rap0, {rx_gain_index}, 'rh')"


   process_tx.update_cmd(command_tx_gain)
   process_rx.update_cmd(command_rx_gain)


   # chossing beam indices for TX and RX
   tx_beam_index = 0
   rx_beam_index = 0
   command_tx_beam = f"host.chip.tx.beam(rap0, {tx_beam_index}, '{tpol}')"
   process_tx.update_cmd(command_tx_beam)
   command_rx_beam = f"host.chip.rx.beam(rap0, {rx_beam_index}, '{rpol}')"
   process_rx.update_cmd(command_rx_beam)
   time.sleep(0.01) 

   tx_beam_index = 6
   rx_beam_index = 12
   command_tx_beam = f"host.chip.tx.beam(rap0, {tx_beam_index}, '{tpol}')"
   process_tx.update_cmd(command_tx_beam)
   command_rx_beam = f"host.chip.rx.beam(rap0, {rx_beam_index}, '{rpol}')"
   process_rx.update_cmd(command_rx_beam)
   time.sleep(0.01) 

   tx_beam_index = 24
   rx_beam_index = 18
   command_tx_beam = f"host.chip.tx.beam(rap0, {tx_beam_index}, '{tpol}')"
   process_tx.update_cmd(command_tx_beam)
   command_rx_beam = f"host.chip.rx.beam(rap0, {rx_beam_index}, '{rpol}')"
   process_rx.update_cmd(command_rx_beam)
   time.sleep(0.01) 

   tx_beam_index = 42
   rx_beam_index = 53
   command_tx_beam = f"host.chip.tx.beam(rap0, {tx_beam_index}, '{tpol}')"
   process_tx.update_cmd(command_tx_beam)
   command_rx_beam = f"host.chip.rx.beam(rap0, {rx_beam_index}, '{rpol}')"
   process_rx.update_cmd(command_rx_beam)
   time.sleep(0.01) 


   tx_beam_index = 63
   rx_beam_index = 63
   command_tx_beam = f"host.chip.tx.beam(rap0, {tx_beam_index}, '{tpol}')"
   process_tx.update_cmd(command_tx_beam)
   command_rx_beam = f"host.chip.rx.beam(rap0, {rx_beam_index}, '{rpol}')"
   process_rx.update_cmd(command_rx_beam)
   time.sleep(0.01) 


   process_tx.stop()
   process_rx.stop()


