#Script to setup EVK02004 in Tx mode
#Author: Sivers Semiconductors

#Choose Low IF or BB mode
mode   = 'BB' # IF = Low IF mode, BB = baseband/zero IF mode
pol1    = 'V'
pol2    = 'H'
tpol   = 'th' #tv = vertical pol, th = horizontal pol, tvth = dual pol


#switch on power domains on the motherboard
host.misc.on(['VCXO', 'PLL'])
host.pwr.on('ALL')

#setup the 245.76 MHz Ref clock on MB2
host.pll.setup()  # Lock the MB2-VCXO to 245.76 MHz
vcxo_freq=host.pll.setup()['vcxo_freq'] #Read back the exact frequency (typically 245759996.9474969 Hz)
host.chip.ref_clk.set(rap0, vcxo_freq) #Set the Rapinoe clock to vcxo_freq.

#RFIC initialisation
host.chip.init(rap0, 'CHIP')
host.chip.init(rap0, 'SYNTH')
host.chip.init(rap0, 'VALIDATION')
host.chip.init(rap0, 'ADC')
host.chip.init(rap0, 'TX', printit=False)

# Synth setup with freq_rff
freq_rff = 25e9 # LO frequency. The script is for IF mode. So RF will be IF freq + freq_rff
host.chip.synth.setup(rap0)
host.chip.synth.set(rap0,freq_rff, frac_mode=True, sd_order=2, printit=True)
host.chip.ram.fill(rap0, '25GHz') # Loads beam for 24GHz from file to RAM. Depending on the RF value a different beambook should be loaded

#Enabling 16 elements on V pol
host.chip.tx.setup(rap0, mode, tpol, ant_en_v=0x0000, ant_en_h=0xFFFF) # for H pol or dual pol write appropriate values for ant_en_h. 0xFFFF is for all 16 paths (each bit is for one path). for ex, if you want just one path write 0x0001. 

#setting up the RFIC in Tx mode and choosing the required gain and beam indices. Check the 'ram.xml' file @C:\Sivers Semiconductors\Rapinoe\API\config\ram for more details
host.chip.trx.mode(rap0,tpol)
host.chip.tx.beam(rap0, 5, tpol)
host.chip.tx.gain_rf(rap0, 0, tpol)

#calibrating for H and V pol separately
#host.chip.tx.dco.calibrate(rap0, mode, pol1)
#host.chip.tx.dco.calibrate(rap0, mode, pol2) # uncomment this cmd and comment the line above if H pol is used or uncomment both lines if dual pol is used (two DCO calibrations are needed then)


#Copy paste the cmds below to change the gain. Modify gain_com and gain_bf as you see fit. Both the ram.wr and tx.gain_rf cmds need to be run for the changed gain values to take effect

#Setting gain values for Tx

#for H pol
#gain_com_h = 32
#gain_bf_h = 64
#host.chip.ram.wr(rap0, 'tx_ram_h', 0, (gain_bf_h<<6)+(gain_com_h<<0))
#host.chip.tx.gain_rf(rap0, 0, 'TH')

#for V pol
#gain_com_v = 32
#gain_bf_v = 64
#host.chip.ram.wr(rap0, 'tx_ram_v', 0, (gain_bf_v<<6)+(gain_com_v<<0))
#host.chip.tx.gain_rf(rap0, 0, 'TV')
