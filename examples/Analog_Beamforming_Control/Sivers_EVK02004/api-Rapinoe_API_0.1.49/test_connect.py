import time
import os
import sys
import threading
import rlcompleter
import readline
import fileHandler as json
import multiprocessing
import beamSweep_host

def get_args():
    import argparse
    parser = argparse.ArgumentParser(description='Command line options.')
    parser.add_argument('-s', '--serial', dest='serial_num', metavar='Serial number', default=None,
                         help='Specify MB serial name')
    parser.add_argument('-b', '--bsp', dest='bsp', choices=['rapvalbsp','rapvalx','rapvalt','bfm02803','dbm1','none'], default='rapvalbsp',
                         help='Specify type of BSP')
    parser.add_argument('-n', '--no_diff', dest='ref_is_diff', action='store_false',
                         help='Set this flag if reference clock is NOT differential')
    parser.add_argument('-i', '--spi', dest='fspi', metavar='<spi_freq>', default=None,
                         help='Specify SPI clock frequency <spi_freq>')
    parser.add_argument('-r', '--fref', dest='fref', metavar='<ref_freq>', default=None,
                         help='Specify reference clock frequency <ref_freq>')
    parser.add_argument('-d', '--fdig', dest='fdig', metavar='<dig_freq>', default=None,
                         help='Specify digital clock frequency <dig_freq>')
    parser.add_argument('-f', '--flo', dest='flo', metavar='<lo_freq>', default=None,
                         help='Specify LO clock frequency <lo_freq>')
    parser.add_argument('-t', '--test', dest='test', default=None,
                         help='Specify test')
    parser.add_argument('-c', '--cfg', dest='cfg_file', metavar='<cfg filename>', default=None,
                         help='Specify configuration file name')
    parser.add_argument('-g', '--gui', dest='gui', metavar='rap? | rap? rap? ... | rapAll', nargs='*', default=None,
                         help='Start GUI[s]')
    parser.add_argument('-x', '--xgui', dest='xgui', metavar='rap? | rap? rap? ... | rapAll', nargs='*', default=None,
                         help='Start GUI[s] with extended features')
    return parser.parse_args()


def initialize_evk(serial_num, bsp, fref, fdig, flo, fspi):
    info_logger.log_info('Connecting to motherboard with serial number {0} ...'.format(serial_num),2)
    host_instance = beamSweep_host.Host(serial_num=serial_num, bsp=bsp, fref=fref, fdig=fdig, flo=flo, fspi=fspi, indent=2)
    rapAll = []
    for num in range(0,host_instance.chip._chip_info.get_num_devs()):
        exec("rap{:} = host_instance.rap{:}".format(num,num))
        exec("rapAll.append(rap{:})".format(str(num)))

    if args.gui != None:
        if len(args.gui) == 0:
            guis = rapAll
        else:
            guis = []
            for gui in args.gui:
                guis.append(eval(gui))
        host.open_gui(guis)

    if args.xgui != None:
        if len(args.xgui) == 0:
            guis = rapAll
        else:
            guis = []
            for gui in args.xgui:
                guis.append(eval(gui))
        host.open_gui(guis, extended=True)

    if args.test != None:
        if not args.test.endswith('.py'):
            args.test = args.test+'.py'
        if os.path.isfile(args.test):
            test_file_exist = True
        else:
            test_file_exist = False
            for dir in ['tests']:
                if os.path.isfile(os.path.join(dir,args.test)):
                    args.test = os.path.join(dir,args.test)
                    test_file_exist = True
                    break
            if not test_file_exist:
                info_logger.log_error('No file found matching {}'.format(args.test),2)
                possible_test_files = []
                for dir in ['tests']+sys.path:
                    if os.path.isfile(os.path.join(dir,os.path.basename(args.test))):
                        possible_test_files.append(os.path.join(dir,os.path.basename(args.test)))
                if len(possible_test_files) > 0:
                    info_logger.log_error('Maybe you meant one of these files?',4)
                    for file in possible_test_files:
                        info_logger.log_error(file,4)
        if test_file_exist:
            info_logger.log_info('Running file {}'.format(args.test),2)
            t=open(args.test,'r')
            exec(t.read())
            t.close()
    info_logger.delayed_reset()


def info_file(fname="evk.info"):
    import evk_logger
    evk_logger.evk_logger = evk_logger.EvkLogger(fname)
    return evk_logger.evk_logger


if __name__ == '__main__':

    if sys.platform == 'linux':
        print('  Unloading USB Serial driver...')
        os.system('sudo modprobe -r ftdi_sio')
    args = get_args()
    info_logger=info_file()
    readline.set_history_length(1000)
    readline.parse_and_bind('tab:complete')

    try:
        fref = float(args.fref)
    except:
        fref = None

    try:
        fdig = float(args.fdig)
    except:
        fdig = None
        
    try:
        flo = float(args.flo)
    except:
        flo = None
        
    try:
        fspi = int(args.fspi)
    except:
        fspi = None

    # Serial numbers for the devices
    serial_num1 = "T582306548"
    serial_num2 = "T582306549"


    # initialize_evk(serial_num2, args.bsp, fref, fdig, flo, fspi)
    # initialize_host(serial_num1, 'rapvalt', 1000000)
    process1 = multiprocessing.Process(target=initialize_evk, args=(serial_num1, args.bsp, fref, fdig, flo, fspi))
    process2 = multiprocessing.Process(target=initialize_evk, args=(serial_num2, args.bsp, fref, fdig, flo, fspi))

    # Start and join the processes
    
    process1.start()
    process1.join()

    process2.start()
    process2.join()


# class Connect:
    
#     def __init__(self, serial_num, bsp, clock_rate=10000000):
#         import mbdrv
#         self.serial_num = serial_num
#         self.mb         = mbdrv.MbDrv()
#         self.board_id  = self.mb.get_board_id(serial_num)

#         # Get MB configuration
#         self.board_type = self.mb.get_board_type(self.board_id)
#         if self.board_type == 'EVK06002':
#             import config.platform.mb1
#             self.config = config.platform.mb1
#         elif self.board_type == 'MB2':
#             import config.platform.mb2
#             self.config = config.platform.mb2
#             attributes = vars(self.config)
#             for key, value in attributes.items():
#                 print(f"{key} = {value}")
#                 break
#             for hw_obj in list(self.config.HW_OBJECTS):
#                 exec("self.{} = self.config.{}(**{})".format(hw_obj, self.config.HW_OBJECTS[hw_obj]['type'], self.config.HW_OBJECTS[hw_obj]['params']))
    
#         # Get module configuration
#         if (bsp == 'rapvalbsp') or (bsp == 'rapvalx'):
#             import config.bsp.rapvalx
#             self._override_signals(config.bsp.rapvalx, self.config)
#             for hw_obj in list(config.bsp.rapvalx.HW_OBJECTS):
#                 exec("self.{} = config.bsp.rapvalx.{}(**{})".format(hw_obj, config.bsp.rapvalx.HW_OBJECTS[hw_obj]['type'], config.bsp.rapvalx.HW_OBJECTS[hw_obj]['params']))
#         elif bsp == 'rapvalt':
#             import config.bsp.rapvalt
#             self._override_signals(config.bsp.rapvalt, self.config)
#             for hw_obj in list(config.bsp.rapvalt.HW_OBJECTS):
#                 exec("self.{} = config.bsp.rapvalt.{}(**{})".format(hw_obj, config.bsp.rapvalt.HW_OBJECTS[hw_obj]['type'], config.bsp.rapvalt.HW_OBJECTS[hw_obj]['params']))
        

#         self.mb.gpio_open(self.board_id, 0, self.config.GPIO_STATE_C)
#         self.mb.gpio_open(self.board_id, 1, self.config.GPIO_STATE_D)
#         print("  SPI speed set to {} MHz".format(clock_rate/1e6))
#         self.spi_chan = self.mb.spi_open(self.board_id, mode=0, clock_rate=clock_rate, pin=self.config.GPIO_STATE_A)
#         self.i2c_chan = self.mb.i2c_open(self.board_id, pin=self.config.GPIO_STATE_B)

#     def _override_signals(self, bsp, conf):
#         sig_names = [item for item in dir(conf)]
#         for sig_name in sig_names:
#             try:
#                 exec("conf.{} = bsp.{}".format(sig_name,sig_name))
#             except:
#                 pass
