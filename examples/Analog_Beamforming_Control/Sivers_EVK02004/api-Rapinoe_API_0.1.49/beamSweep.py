import os
import sys
import time
import readline
import argparse
import evk_logger
import multiprocessing
import host

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
    return evk_logger.EvkLogger(fname)

class beamSweep(multiprocessing.Process):

    def __init__(self, process_id,serial_num, bsp, fref, fdig, flo, fspi, gui, xgui, test):
        super().__init__()
        self.process_id = process_id
        self.serial_num = serial_num
        self.bsp = bsp
        self.fref = fref
        self.fdig = fdig
        self.flo = flo
        self.fspi = fspi
        self.gui = gui
        self.xgui = xgui
        self.test = test

        self.current_cmd = 0
        self.event = multiprocessing.Event()
        self.new_cmd = multiprocessing.Queue()
        self.terminate = multiprocessing.Event() # Additional event to handle termination
        self.init_done = multiprocessing.Event()  # Event to signal initialization completion
        self.initialization_successful = multiprocessing.Value('b', False)  # Boolean flag for checking success


    def run(self):
        if sys.platform == 'linux':
            print('Unloading USB Serial driver...')
            os.system('sudo modprobe -r ftdi_sio')

        info_logger = info_file()
        readline.set_history_length(1000)
        readline.parse_and_bind('tab:complete')
        try:
            self.setup_device(info_logger)
            self.initialization_successful.value = True
        except Exception as e:
            info_logger.log_error(f"Initialization failed: {str(e)}")
            self.initialization_successful.value = False
        finally:
            self.init_done.set()  # Signal that initialization attempt is complete
        
        if self.initialization_successful.value:
            self.process_commands(info_logger)
        else:
            info_logger.log_info('Process will terminate due to failed initialization.')
            return  # Terminate the process if setup fails


    def setup_device(self, info_logger):

        # Convert and check parameters
        fref = self.try_convert_float(self.fref)
        fdig = self.try_convert_float(self.fdig)
        flo = self.try_convert_float(self.flo)
        fspi = self.try_convert_int(self.fspi)

        
        info_logger.log_info(f'Connecting to motherboard with serial number {0} ...'.format(self.serial_num),2)
        
        try:
            # Attempt to create the host instance
            self.host = host.Host(serial_num=self.serial_num, bsp=self.bsp, fref=fref, fdig=fdig, flo=flo, fspi=fspi, indent=2)
            if not self.host:
                raise ValueError("Host instance creation returned None.")
            info_logger.log_info('Host instance created successfully.')
        except Exception as e:
            # Log the exception and raise it to be caught by the calling block
            info_logger.log_error(f'Failed to create host instance: {e}')
            raise  # Reraising the exception to be handled by the caller
        
        self.manage_gui()
        
        if self.test:
            self.run_test(info_logger)

        info_logger.delayed_reset()

    def try_convert_float(self, value):
        try:
            return float(value)
        except (TypeError, ValueError):
            return None
        
    def try_convert_int(self, value):
        try:
            return int(value)
        except (TypeError, ValueError):
            return None

    def manage_gui(self):
        if self.gui:
            guis = [getattr(self.host, gui_item.strip()) for gui_item in self.gui]
            self.host.open_gui(guis)
        if self.xgui:
            xguis = [getattr(self.host, xgui_item.strip()) for xgui_item in self.xgui]
            self.host.open_gui(xguis, extended=True)

    def run_test(self, info_logger):
        test_path = f"{self.test}.py" if not self.test.endswith('.py') else self.test
        
        if os.path.isfile(test_path):
            test_file_exist = True
        else:
            test_file_exist = False            
            for dir in ['tests']:
                print(os.path.join(dir,test_path))
                print(os.path.isfile(os.path.join(dir,test_path)))
                if os.path.isfile(os.path.join(dir,test_path)):
                    test = os.path.join(dir,test_path)
                    test_file_exist = True
                    print(test)
                    break
            if not test_file_exist:
                info_logger.log_error('No file found matching {}'.format(test_path),2)
                possible_test_files = []
                for dir in ['tests']+sys.path:
                    if os.path.isfile(os.path.join(dir,os.path.basename(test_path))):
                        possible_test_files.append(os.path.join(dir,os.path.basename(test_path)))
                if len(possible_test_files) > 0:
                    info_logger.log_error('Maybe you meant one of these files?',4)
                    for file in possible_test_files:
                        info_logger.log_error(file,4)
        if test_file_exist:
            info_logger.log_info('Running file {}'.format(test_path),2)
            t=open(test,'r')
            exec(t.read(), {'host': self.host, 'rap0': self.host.rap0})
            t.close()

    def process_commands(self, info_logger):
        while not self.terminate.is_set():
            self.event.wait()
            while not self.new_cmd.empty():
                input_cmd = self.new_cmd.get()
                exec(input_cmd, {'host': self.host, 'rap0': self.host.rap0})
                info_logger.log_info('Command executed.', 2)
            self.event.clear()

    def update_cmd(self, new_cmd):
        self.new_cmd.put(new_cmd)
        self.event.set()

    def stop(self):
        self.terminate.set()
        self.event.set()
        self.join()

def beamSweep_start(process_id, serial_num, bsp, fref, fdig, flo, fspi, gui, xgui, test):
    beamSweep_process = beamSweep(process_id, serial_num, bsp, fref, fdig, flo, fspi, gui, xgui, test)
    beamSweep_process.start()
    beamSweep_process.init_done.wait()  # Wait here until initialization is done
    
    if not beamSweep_process.initialization_successful.value:
        print("Initialization failed, the process will exit.")
        beamSweep_process.terminate()  # Ensure process is terminated
        beamSweep_process.join()       # Clean up the process resources
        return None  # Return None to indicate failure
    else:
        print("Initialization successful, the process is running.")
    
    return beamSweep_process


# if __name__ == '__main__':
#     args = get_args()
#     beamSweep_process_1 = beamSweep_start(1, args.serial_num, args.bsp, args.fref, args.fdig, args.flo, args.fspi, args.gui, args. xgui, args.test)
    
#     if beamSweep_process_1 is None:
#         sys.exit(1)  # Exit the program if initialization failed

#     beam_index = 0
#     tpol = 'tv'

#     for ii in range(64):
#         # Format the command string with the current beam_index and tpol
#         command = f"host.chip.tx.beam(rap0, {beam_index}, '{tpol}')"
#         beamSweep_process_1.update_cmd(command)
#         time.sleep(0.02)  # Sleep to allow processing time between commands
#         beam_index += 1
#         print(f'Config TX beam index: {beam_index}')

#     beamSweep_process_1.stop()