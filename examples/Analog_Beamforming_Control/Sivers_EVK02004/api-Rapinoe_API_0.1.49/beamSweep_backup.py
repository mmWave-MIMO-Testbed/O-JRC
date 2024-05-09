import os
import sys
import time
import readline
import argparse
import multiprocessing
import beamSweep_host

def get_args():
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

def info_file(fname="evk.info"):
    import evk_logger
    evk_logger.evk_logger = evk_logger.EvkLogger(fname)
    return evk_logger.evk_logger


def evk_setup(serial_num, bsp, fref, fdig, flo, fspi, gui, xgui, test):

    if sys.platform == 'linux':
        print('  Unloading USB Serial driver...')
        os.system('sudo modprobe -r ftdi_sio')

    info_logger=info_file()

    readline.set_history_length(1000)
    readline.parse_and_bind('tab:complete')

    try:
        fref = float(fref)
    except:
        fref = None

    try:
        fdig = float(fdig)
    except:
        fdig = None
        
    try:
        flo = float(flo)
    except:
        flo = None
        
    try:
        fspi = int(fspi)
    except:
        fspi = None

    
    info_logger.log_info('Connecting to motherboard with serial number {0} ...'.format(serial_num),2)
    host_instance = beamSweep_host.Host(serial_num=serial_num, bsp=bsp, fref=fref, fdig=fdig, flo=flo, fspi=fspi, indent=2)
    rapAll = []
    for num in range(0,host_instance.chip._chip_info.get_num_devs()):
        exec("rap{:} = host_instance.rap{:}".format(num,num))
        exec("rapAll.append(rap{:})".format(str(num)))

    if gui != None:
        if len(gui) == 0:
            guis = rapAll
        else:
            guis = []
            for gui in gui:
                guis.append(eval(gui))
        host_instance.open_gui(guis)

    if xgui != None:
        if len(xgui) == 0:
            guis = rapAll
        else:
            guis = []
            for gui in xgui:
                guis.append(eval(gui))
        host_instance.open_gui(guis, extended=True)

    if test != None:
        if not test.endswith('.py'):
            test = test+'.py'
        if os.path.isfile(test):
            test_file_exist = True
        else:
            print("222")
            test_file_exist = False
            for dir in ['tests']:
                print(dir)
                if os.path.isfile(os.path.join(dir,test)):
                    print("333")
                    print(os.path.join(dir,test))
                    test = os.path.join(dir,test)
                    test_file_exist = True
                    break
            if not test_file_exist:
                info_logger.log_error('No file found matching {}'.format(test),2)
                possible_test_files = []
                for dir in ['tests']+sys.path:
                    if os.path.isfile(os.path.join(dir,os.path.basename(test))):
                        possible_test_files.append(os.path.join(dir,os.path.basename(test)))
                if len(possible_test_files) > 0:
                    info_logger.log_error('Maybe you meant one of these files?',4)
                    for file in possible_test_files:
                        info_logger.log_error(file,4)
        if test_file_exist:
            info_logger.log_info('Running file {}'.format(test),2)
            t=open(test,'r')
            exec(t.read())
            t.close()


            # print("gggggggggggggggggggggggggggggg")
            # exec("host_instance.chip.tx.dco.calibrate(rap0, mode, pol1)")
            # t.close()
    info_logger.delayed_reset()

def main(serial_num, bsp, fref, fdig, flo, fspi, gui, xgui, test):
    process = multiprocessing.Process(target=evk_setup, args=(serial_num, bsp, fref, fdig, flo, fspi, gui, xgui, test))
    process.start()
    process.join()

if __name__ == '__main__':
    args = get_args()
    main(args.serial_num, args.bsp, args.fref, args.fdig, args.flo, args.fspi, args.gui, args. xgui, args.test)
    
    
    
    # evk_beam()

def evk_beam(beam_index):
    host_instance.chip.tx.beam(rap0, beam_index, tpol)




# if __name__ == '__main__':

#     args = get_args()

#     process = multiprocessing.Process(target=initialize_evk, args=(args.serial_num, args.bsp, args.fref, args.fdig, args.flo, args.fspi))
#     # process.daemon = True
#     process.start()
#     process.join()


# python3 beamSweep.py -s  T582306548 -t beamSweep_tx_setup