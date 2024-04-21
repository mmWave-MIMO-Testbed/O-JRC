from common import *
import evk_logger

class RxFiltCal():

    __instance = None
    __initialized = False

    _pol_codes = {'H':0,'V':1,'H-pol':0,'V-pol':0,'H-polarization':0,'V-polarization':1}
    _pol_names = {0:'H-pol',1:'V-pol'}
    _bw_codes  = {'25MHz':0,'50MHz':1,'100MHz':2,'200MHz':3,'400MHz':4,'600MHz':5}
    _bw_names  = {0:'25MHz',1:'50MHz',2:'100MHz',3:'200MHz',4:'400MHz',5:'600MHz'}

    # BW -20% cnt max div4 margin hex
    #  25  20   6560   1640  1600  640
    #  50  40  13120   3280  3200  C80
    # 100  80  26240   6560  6500 1964
    # 200 160  52480  13120 13000 32C8
    # 400 320 104960  26240 26000 6590
    # 600 480 157441  39360 39000 9858
    _lut_golden_osc = {
        25:    6500,
        50:   13000,
        100:  26000,
        200:  52000,
        400: 104000,
        600: 157000
    }

    _lut_calosc_div_h = {
        0:  3,
        1:  3,
        2:  3,
        3:  3,
        4:  3,
        5:  3
    }
    _lut_calosc_div_v = {
        0:  3,
        1:  3,
        2:  3,
        3:  3,
        4:  3,
        5:  3
    }


    def __new__(cls, spi):
        if cls.__instance is None:
            cls.__instance = super(RxFiltCal, cls).__new__(cls)
            cls.__instance.__initialized = False
        return cls.__instance

    def __init__(self, spi):
        if not RxFiltCal.__initialized:
            self._spi = spi
            RxFiltCal.__initialized = True

    def _is_set(self, data, bit_no):
        """
        Return True if bit is 1, otherwise False
        """
        mask = 1 << bit_no
        return (mask & data) == mask

    def _is_clr(self, data, bit_no):
        """
        Return True if bit is 0, otherwise False
        """
        mask = 1 << bit_no
        return (mask & data) == 0

    def _get_bit(self, data, bit_no):
        """
        Return wanted bit
        """
        mask = 1 << bit_no
        return (mask & data) >> bit_no

    def _get_pol(self, pol):
        if isinstance(pol, int):
            if (pol == 1):
                return 1
            elif (pol == 0):
                return 0
            else:
                evk_logger.evk_logger.log_info("Unsupported polarization parameter {}".format(pol),self.indent)
                return None
        elif isinstance(pol, str):
            if (pol.lower() == 'v')   | (pol.lower() == 'v-pol'):
                return 1
            elif (pol.lower() == 'h') | (pol.lower() == 'h-pol'):
                return 0
            else:
                evk_logger.evk_logger.log_info("Unsupported polarization parameter {}".format(pol),self.indent)
                return None
        else:
            evk_logger.evk_logger.log_info("Unsupported polarization parameter {}".format(pol),self.indent)
            return None

    def _get_bw(self, bw):
        if isinstance(bw, int):
            if (bw >= 0) & (bw <= 5):
                return bw
            elif bw == 25:
                return 0
            elif bw == 50:
                return 1
            elif bw == 100:
                return 2
            elif bw == 200:
                return 3
            elif bw == 400:
                return 4
            elif bw == 600:
                return 5
            else:
                evk_logger.evk_logger.log_info("Unsupported bandwidth parameter {}".format(bw),self.indent)
                return None
        elif isinstance(bw, str):
            if   bw.lower() == '25mhz':
                return 0
            elif bw.lower() == '50mhz':
                return 1
            elif bw.lower() == '100mhz':
                return 2
            elif bw.lower() == '200mhz':
                return 3
            elif bw.lower() == '400mhz':
                return 4
            elif bw.lower() == '600mhz':
                return 5
            else:
                evk_logger.evk_logger.log_info("Unsupported bandwidth parameter {}".format(bw),self.indent)
                return None
        else:
            evk_logger.evk_logger.log_info("Unsupported bandwidth parameter {}".format(bw),self.indent)
            return None

    def reset(self, devs):
        """RX BB Filter Calibration reset

        Args:
            devs (_type_): _description_
        """
        self._spi.set(devs, 'rx_bb_ctrl_0', 0x04)
        self._spi.clr(devs, 'rx_bb_ctrl_0', 0x04)

    def enable(self, devs):
        """ 
        """ 
        self._spi.set(devs, 'cgu_slave_clk',  0b100000000000)
        self._spi.set(devs, 'cgu_module_clk', 0b100000000000)
        self._spi.clr(devs, 'rx_bb_ctrl_0', 0x04)

    def disable(self, devs):
        """
        """ 
        self._spi.set(devs, 'rx_bb_ctrl_0', 0x04)
        self._spi.clr(devs, 'cgu_slave_clk',  0b100000000000)
        self._spi.clr(devs, 'cgu_module_clk', 0b100000000000)

    def setting(self, devs):
        """
        Dump RX register setting
        """
        evk_logger.evk_logger.log_info("golden_ref     {}".format(fhex(self._spi.rd(devs, 'golden_ref'))))
        evk_logger.evk_logger.log_info("rx_bb_ctrl_0   {}".format(fhex(self._spi.rd(devs, 'rx_bb_ctrl_0'))))
        evk_logger.evk_logger.log_info("rx_bb_info_0   {}".format(fhex(self._spi.rd(devs, 'rx_bb_info_0'))))
        evk_logger.evk_logger.log_info("capval_v       {}".format(fhex(self._spi.rd(devs, 'capval_v'))))
        evk_logger.evk_logger.log_info("capval_h       {}".format(fhex(self._spi.rd(devs, 'capval_h'))))
        evk_logger.evk_logger.log_info("calmask        {}".format(fhex(self._spi.rd(devs, 'calmask'))))
        evk_logger.evk_logger.log_info("lut_calosc_div {}".format(fhex(self._spi.rd(devs, 'lut_calosc_div'))))
        evk_logger.evk_logger.log_info("lut_golden_osc {}".format(fhex(self._spi.rd(devs, 'lut_golden_osc'))))

    def setup(self, devs):
        """
        """
        self._spi.wr(devs, 'golden_ref', 0xffff)

        lut_golden_osc = (RxFiltCal._lut_golden_osc[600] << 5*16) | \
                         (RxFiltCal._lut_golden_osc[400] << 4*16) | \
                         (RxFiltCal._lut_golden_osc[200] << 3*16) | \
                         (RxFiltCal._lut_golden_osc[100] << 2*16) | \
                         (RxFiltCal._lut_golden_osc[50]  << 1*16) | \
                         (RxFiltCal._lut_golden_osc[25]  << 0*16)
        self._spi.wr(devs, 'lut_golden_osc', lut_golden_osc)

        lut_calosc_div = (RxFiltCal._lut_calosc_div_v[5] << 11*2) | \
                         (RxFiltCal._lut_calosc_div_v[4] << 10*2) | \
                         (RxFiltCal._lut_calosc_div_v[3] <<  9*2) | \
                         (RxFiltCal._lut_calosc_div_v[2] <<  8*2) | \
                         (RxFiltCal._lut_calosc_div_v[1] <<  7*2) | \
                         (RxFiltCal._lut_calosc_div_v[0] <<  6*2) | \
                         (RxFiltCal._lut_calosc_div_h[5] <<  5*2) | \
                         (RxFiltCal._lut_calosc_div_h[4] <<  4*2) | \
                         (RxFiltCal._lut_calosc_div_h[3] <<  3*2) | \
                         (RxFiltCal._lut_calosc_div_h[2] <<  2*2) | \
                         (RxFiltCal._lut_calosc_div_h[1] <<  1*2) | \
                         (RxFiltCal._lut_calosc_div_h[0] <<  0*2)
        self._spi.wr(devs, 'lut_calosc_div', lut_calosc_div)

    def calibrate(self, devs, pol, bw, printit=False):
        """ 
        Run automatic calibration of one or several configurations
        - pol: 1-3
        - bw : 1-63
        
        Prerequisites:
        golden_ref     needs to be setup before running this function
        lut_golden_osc needs to be setup before running this function
        lut_calosc_div needs to be setup before running this function
        
        """ 
        calmask_data = 0
        if isinstance(pol,list):
            for i,one_pol in enumerate(pol):
                pol_int = self._get_pol(one_pol)
                if isinstance(pol_int,str):
                    evk_logger.evk_logger.log_info("Unsupported polarization {}!".format(one_pol))
                    return
                if isinstance(pol_int,int):
                    if pol_int > 1:
                        evk_logger.evk_logger.log_info("Unsupported polarization {}!".format(one_pol))
                        return
                else:
                    evk_logger.evk_logger.log_info("Unsupported polarization {}!".format(one_pol))
                    return
                calmask_data = calmask_data | (1 << (6+pol_int))
        else:
            pol_int = self._get_pol(pol)
            if isinstance(pol_int,str):
                evk_logger.evk_logger.log_info("Unsupported polarization {}!".format(pol))
                return
            if isinstance(pol_int,int):
                if pol_int > 1:
                    evk_logger.evk_logger.log_info("Unsupported polarization {}!".format(pol))
                    return
            else:
                evk_logger.evk_logger.log_info("Unsupported polarization {}!".format(pol))
                return
            calmask_data = calmask_data | (1 << (6+pol_int))

        if isinstance(bw,list):
            for i,one_bw in enumerate(bw):
                bw_int = self._get_bw(one_bw)
                if isinstance(bw_int,str):
                    evk_logger.evk_logger.log_info("Unsupported bandwidth {}!".format(one_bw))
                    return
                if isinstance(bw_int,int):
                    if bw_int > 5:
                        evk_logger.evk_logger.log_info("Unsupported bandwidth {}!".format(one_bw))
                        return
                else:
                    evk_logger.evk_logger.log_info("Unsupported bandwidth {}!".format(one_bw))
                    return
                calmask_data = calmask_data | (1 << bw_int)
        else:
            bw_int = self._get_bw(bw)
            if isinstance(bw_int,str):
                evk_logger.evk_logger.log_info("Unsupported bandwidth {}!".format(bw))
                return
            if isinstance(bw_int,int):
                if bw_int > 5:
                    evk_logger.evk_logger.log_info("Unsupported bandwidth {}!".format(bw))
                    return
            else:
                evk_logger.evk_logger.log_info("Unsupported bandwidth {}!".format(bw))
                return
            calmask_data = calmask_data | (1 << bw_int)

        cgu_misc_clk_backup = self._spi.rd(devs, 'cgu_misc_clk')
        self._spi.wr(devs, 'cgu_misc_clk', 0x5)

        # Ensure that the calibration start bit is 0
        self._spi.clr(devs, 'rx_bb_ctrl_0', 1)

        # Ensure that previous run did not stall
        if self._is_set(self._spi.rd(devs, 'rx_bb_info_0'),1):
            self.reset(devs) # Reset due to earlier stalling run

        if (calmask_data & 0xC0 > 0) & (calmask_data & 0x3F > 0):
            evk_logger.evk_logger.log_info("Running BBRX Filter Calibration with following modes enabled:")
            text = " "
            for i in range(7,6-1,-1):
                if self._is_set(calmask_data,i): text = text + str(RxFiltCal._pol_names[i-6]) + " "
            for i in range(6):
                if self._is_set(calmask_data,i): text = text + str(RxFiltCal._bw_names[i]) + " "
        evk_logger.evk_logger.log_info("{}".format(text))
        self._spi.wr(devs, 'calmask', calmask_data)
        
        # Start automatic calibration
        self._spi.set(devs, 'rx_bb_ctrl_0', 0x01) # Start RX BB Filter Calibration
        
        test_done  =  0 
        rd_mask  =  0x2  # Only bit [1] is interesting 
        for check in range(0, 100):
          if (test_done == 0) :
                rd_data = self._spi.rd(devs, 'rx_bb_info_0')
                if ((rd_data & rd_mask ) == rd_mask ) : 
                    # Start detected
                    test_done  =  1  # End for loop
                    break

        if (test_done == 0) :
            evk_logger.evk_logger.log_info("ERROR: RX BB Filter Calibration did not start. BBRX Filter Cal reset is toggled!")
            self.reset(devs) # Reset due to earlier stalling run
        else:
            test_done  =  0 
            rd_mask  =  0x1  # Only bit [0] is interesting 
            for check in range(0, 10000):
                if (test_done == 0) :
                    rd_data = self._spi.rd(devs, 'rx_bb_info_0')
                    if ((rd_data & rd_mask ) == rd_mask ) : 
                        # Finish detected
                        test_done  =  1  # End for loop
                        break
            
            if (test_done == 0) :
                evk_logger.evk_logger.log_info("ERROR: RX BB Filter Calibration did not finish!")
            else:
                evk_logger.evk_logger.log_info("RX BB Filter Calibration done!")

        # Clear automatic calibration
        self._spi.clr(devs, 'rx_bb_ctrl_0', 0x01 ) # Stop RX BB Filter Calibration 

        # Restore cgu_misc_clk value
        self._spi.wr(devs, 'cgu_misc_clk', cgu_misc_clk_backup)


    def meas_freq(self, devs, pol, bw, fdigclk=199800000, printit=False):
        
        """ 
        Return the frequency of a single BBRX Filter Calibration Oscillator setup where 0 means dead osc.
        
        Prerequisites:
        * dig_clk frequency will be hardcoded to 199.8 MHz until we have a function which returns the dig_clk frequency
        * R1 TO has BBRX Cal Osc clock divider 4-7, i.e. not the expected 1-4
        * BBRX Cal Osc 25 MHz mode => max 25/4 MHz frequency in to dig_core

        Test setup:
        
        """

        
        # Save register settings which this function will update
        save_calmask    = self._spi.rd(devs, 'calmask')
        save_golden_ref = self._spi.rd(devs, 'golden_ref')

        # Enable the Calibration clock in dig_core
        self._spi.set(devs, 'cgu_misc_clk', 0x4)
        
        # Ensure single run bit is inactive
        self._spi.clr(devs, 'rx_bb_ctrl_0', 0x2 ) # Stop RX BB Filter single run

        # Ensure that previous run did not stall
        if self._is_set(self._spi.rd(devs, 'rx_bb_info_0'),1):
            self.reset(devs) # Reset due to earlier stalling run
        
        pol_int = self._get_pol(pol)
        if pol_int > 1:
            evk_logger.evk_logger.log_info("Only a single polarization is supported by this function, i.e. not {}!".format(pol))
            return 0
        bw_int = self._get_bw(bw)
        if bw_int > 5:
            evk_logger.evk_logger.log_info("Only a single bandwidth is supported by this function, i.e. not {}!".format(bw))
            return 0
        wr_data = (1 << pol_int +6) | (1 << bw_int)
        print('calmask', hex(wr_data))
        self._spi.wr(devs, 'calmask', wr_data )
        # Need to restore golden_ref if calmask is updated due to RX BB SAB bug in R1
        self._spi.wr(devs, 'golden_ref', 0xFFFF ) # Max register value gives max frequency resolution
        #
        # R5 will have the correct osc divider design => divide by 1,2,3,4
        #
        # R1 has a faulty divider macro with min divider = 4 + margin =>
        # R1 max frequency with lowest divider value:
        # BW 0:  25+20% /4 =   7.5 MHz in to dig_core
        # BW 1:  50+20% /4 =  15
        # BW 2: 100+20% /4 =  30
        # BW 3: 200+20% /4 =  60
        # BW 4: 400+20% /4 = 120
        # BW 5: 600+20% /4 = 180
        #
        # A dig clk of 200 MHz and a counter value of 0xFFFF => osc clk counter values:
        # BW 0: 0x0999
        # BW 1: 0x1333
        # BW 2: 0x2666
        # BW 3: 0x4CCC
        # BW 4: 0x9999
        # BW 5: 0xE665
        #
        #[0] 9C4 [1] 1388 [2] 2710 [3] 4E20 [4] 9C40 [5] EA60
        #lut_golden_osc = 0xEA609C404E202710138809C4
        #lut_golden_osc = (0xEA60 << 5*16) | (0x9C40 << 4*16) | (0x4E20 << 3*16) | (0x2710 << 2*16) | (3600 << 1*16) | (1800 << 0*16)
        #self._spi.wr(devs, 'lut_golden_osc', lut_golden_osc)
        # Avoid using spi.set() due to strange malfunction in R1
        self._spi.set(devs, 'rx_bb_ctrl_0', 0x2) # Start RX BB Filter single run 
        meas_done = 0
        for wait_loop in range(1, 1000+1):
            if (meas_done == 0) :
                rd_data = self._spi.rd(devs, 'rx_bb_info_0')
                if (rd_data & 0x1 == 0x1) :
                    # Single run test done!
                    meas_done  =  1
                    break
        self._spi.clr(devs, 'rx_bb_ctrl_0', 0x2) # Stop RX BB Filter single run 
        print('meas_done', meas_done)
        if (wait_loop > 999) :
            # Time-out reached when waiting for test finished register field!
            #print("Time-out with golden_ref = {}",self._spi.rd(devs, 'golden_ref'))
            # Restore register settings which this function updated
            self._spi.wr(devs, 'calmask',   save_calmask)
            self._spi.wr(devs, 'golden_ref',save_golden_ref)
            # Activate cal_reset due to dead oscillator in this setup.
            self.reset(devs)
            # Should we disable the Calibration clock gate here?
            print('?????')
            return 0
        else:
            golden_ref = self._spi.rd(devs, 'golden_ref')
            print('golden_ref', golden_ref)
            golden_clks = 0xFFFF - golden_ref
            #lut_golden_osc_bw = (0xFFFF < 16*bw)
            #osc_clk = fdigclk/golden_clks*lut_golden_osc
            #print('bw',bw)
            #print('bw_int',bw_int)
            lut_golden_osc_bw = 0xFFFF & (self._spi.rd(devs, 'lut_golden_osc') >> 16*bw_int)
            osc_clk = fdigclk/golden_clks*lut_golden_osc_bw*4
            #print("{} {} {} {}",osc_clk,fdigclk,golden_clks,lut_golden_osc_bw, golden_ref)
            # Restore register settings which this function updated
            self._spi.wr(devs, 'calmask',   save_calmask)
            self._spi.wr(devs, 'golden_ref',save_golden_ref)
            # Should we disable the Calibration clock gate here?
            return osc_clk
