#Script to setup EVK02004 in Tx mode
#Author: Sivers Semiconductors

#Choose Low IF or BB mode
mode   = 'IF' # IF = Low IF mode, BB = baseband/zero IF mode
pol1    = 'V'
pol2    = 'H'
tpol   = 'tv' #tv = vertical pol, th = horizontal pol, tvth = dual pol


#switch on power domains on the motherboard
host_instance.misc.on(['VCXO', 'PLL'])
host_instance.pwr.on('ALL')

#setup the 245.76 MHz Ref clock on MB2
host_instance.pll.setup()  # Lock the MB2-VCXO to 245.76 MHz
vcxo_freq=host_instance.pll.setup()['vcxo_freq'] #Read back the exact frequency (typically 245759996.9474969 Hz)
host_instance.chip.ref_clk.set(rap0, vcxo_freq) #Set the Rapinoe clock to vcxo_freq.

#RFIC initialisation
host_instance.chip.init(rap0, 'CHIP')
host_instance.chip.init(rap0, 'SYNTH')
host_instance.chip.init(rap0, 'VALIDATION')
host_instance.chip.init(rap0, 'ADC')
host_instance.chip.init(rap0, 'TX', printit=False)

# Synth setup with freq_rff
freq_rff = 22.6e9 # LO frequency. The script is for IF mode. So RF will be IF freq + freq_rff
host_instance.chip.synth.setup(rap0)
host_instance.chip.synth.set(rap0,freq_rff, frac_mode=True, sd_order=2, printit=True)
host_instance.chip.ram.fill(rap0, '27GHz') # Loads beam for 27GHz from file to RAM. Depending on the RF value a different beambook should be loaded

#Enabling 16 elements on V pol
host_instance.chip.tx.setup(rap0, mode, tpol, ant_en_v=0xFFFF, ant_en_h=0x0000) # for H pol or dual pol write appropriate values for ant_en_h. 0xFFFF is for all 16 paths (each bit is for one path). for ex, if you want just one path write 0x0001. 

#setting up the RFIC in Tx mode and choosing the required gain and beam indices. Check the 'ram.xml' file @C:\Sivers Semiconductors\Rapinoe\API\config\ram for more details
host_instance.chip.trx.mode(rap0,tpol)
host_instance.chip.tx.beam(rap0, 5, tpol)
host_instance.chip.tx.gain_rf(rap0, 0, tpol)

#calibrating for H and V pol separately
host_instance.chip.tx.dco.calibrate(rap0, mode, pol1)
#host.chip.tx.dco.calibrate(rap0, mode, pol2) # uncomment this cmd and comment the line above if H pol is used or uncomment both lines if dual pol is used (two DCO calibrations are needed then)

beam_index = 0
for i in range (64):
    host_instance.chip.tx.beam(rap0, beam_index, tpol)  #Beam begin with index 0
    time.sleep(0.01)
    beam_index += 1
    print('Config TX beam index: {}'.format(beam_index))

