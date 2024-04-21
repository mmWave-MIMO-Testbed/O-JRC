#Script to setup EVK02004 in Rx mode
#Author: Sivers Semiconductors

#Choose Low IF or BB mode
mode   = 'IF' # IF = Low IF mode, BB = baseband/zero IF mode
pol1    = 'V'
pol2    = 'H'
rpol   = 'rv' #rv = vertical pol, rh = horizontal pol, rvrh = dual pol

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
host.chip.init(rap0, 'RX', printit=False)

# Synth setup with freq_rff
freq_rff = 22.6e9 # LO frequency. The script is for IF mode. So RF will be IF freq + freq_rff
host.chip.synth.setup(rap0)
host.chip.synth.set(rap0,freq_rff, frac_mode=True, sd_order=2, printit=True)
host.chip.ram.fill(rap0, '27GHz') # Loads beam for 27GHz from file to RAM. Depending on the RF value a different beambook should be loaded

#Enabling 16 elements on V pol
host.chip.rx.setup(rap0, mode, rpol, ant_en_v=0xFFFF, ant_en_h=0x0000)# for H pol or dual pol write appropriate values for ant_en_h. 0xFFFF is for all 16 paths (each bit is for one path). for ex, if you want just one path write 0x0001.

#setting up the RFIC in Rx mode and choosing the required gain and beam indices. Check the 'ram.xml' file @C:\Sivers Semiconductors\Rapinoe\API\config\ram for more details
host.chip.trx.mode(rap0,rpol)
host.chip.rx.beam(rap0, 5, rpol)
host.chip.rx.gain(rap0, 0, rpol)

#calibrating for H and V pol separately
host.chip.rx.dco.calibrate(rap0, pol1, 0)
#host.chip.rx.dco.calibrate(rap0, pol2, 0)# uncomment this cmd and comment the line above if H pol is used or uncomment both lines if dual pol is used (two DCO calibrations are needed then)

#Copy paste the cmds below to change the gain. Modify lna_gain, bf_gain, and com_gain as you see fit.All the 3 cmds i.e. ram.wr,rx.gain and dco.calibrate need to be run for the changed gain values to take effect

#settings for Rx gain
# H pol
#lna_gain_h = 12
#bf_gain_h = 54
#com_gain_h = 54
#host.chip.ram.wr(rap0, 'rx_ram_h', 0, (lna_gain_h<<61)+(bf_gain_h<<55)+(com_gain_h<<49))
#host.chip.rx.gain(rap0, 0, 'rh')
#host.chip.rx.dco.calibrate(rap0, pol2, 0)

# V pol
#lna_gain_v = 12
#bf_gain_v = 54
#com_gain_v = 54
#host.chip.ram.wr(rap0, 'rx_ram_v', 0, (lna_gain_v<<61)+(bf_gain_v<<55)+(com_gain_v<<49))
#host.chip.rx.gain(rap0, 0, 'rv')
#host.chip.rx.dco.calibrate(rap0, pol1, 0)
