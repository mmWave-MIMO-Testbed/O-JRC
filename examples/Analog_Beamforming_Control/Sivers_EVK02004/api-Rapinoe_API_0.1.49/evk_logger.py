import traceback
import logging
from logging import handlers
import colorama
import re
import os

import threading
from functools import wraps
from common import get_time_stamp

_call_log_timestamp = '%Y-%m-%d %H:%M:%S.%f'
evk_logger = None
FUNC_CALL = 1
CALL_ENTRY_PROCESS = True
MAX_LOG_FILE_SIZE = 30000000
replacement_dict = {}

class FontColors:
    HEADER    = '\033[95m'
    OKBLUE    = '\033[94m'
    OKGREEN   = '\033[92m'
    DEBUG     = '\033[94m'
    WARNING   = '\033[93m'
    FAIL      = '\033[91m'
    CRITICAL  = '\033[91m'
    ENDC      = '\033[0m'
    BOLD      = '\033[1m'
    UNDERLINE = '\033[4m'

class EvkLogger(object):

    import readline

    __instance = None

    def __new__(cls, fname='evk.info', indent=0):
        if cls.__instance is None:
            cls.__instance = super(EvkLogger, cls).__new__(cls)
            cls.__instance.__initialized = False
        return cls.__instance

    def __init__(self, fname='evk.info', indent=0):
        if self.__initialized:
            return
        colorama.init(autoreset=True)
        self._indent = indent
        self._logger = logging.getLogger('evk_logger')
        self._logger.setLevel(logging.DEBUG)
        self._fh = handlers.RotatingFileHandler(fname, maxBytes=MAX_LOG_FILE_SIZE, backupCount=3)
        self._fh.setLevel(FUNC_CALL)
        self._ch = logging.StreamHandler()
        self._ch.setLevel(logging.INFO)
        file_format = logging.Formatter('%(asctime)s %(levelname)-5s: # %(message)s')
        scr_format = logging.Formatter('%(message)s')
        self._ch.setFormatter(scr_format)
        self._fh.setFormatter(file_format)
        self._logger.addHandler(self._ch)
        self._logger.addHandler(self._fh)
        self._call_level = 0
        self._max_call_level = 0
        self.__initialized = True
        self._last_hist_item_idx = 0

    def delayed_reset(self):
        threading.Timer(0.1, self.reset).start()

    def reset(self):
        self._last_hist_item_idx = self.readline.get_current_history_length()

    def set_max_call_log_level(self, max_call_level):
        self._max_call_level = max_call_level

    def log_info(self, message, indentation=None):
        if indentation == None:
            indentation = self._indent
        self._log_cmd_hist()
        self._logger.info(' '*indentation + str(message))

    def log_bold(self, message, indentation=None):
        if indentation == None:
            indentation = self._indent
        self._log_cmd_hist()
        self._logger.info(' '*indentation + colorama.Style.BRIGHT + str(message))

    def log_warning(self, message, indentation=None):
        if indentation == None:
            indentation = self._indent
        self._log_cmd_hist()
        self._logger.warning(' '*indentation + colorama.Style.BRIGHT + colorama.Fore.YELLOW + str(message))

    def log_debug(self, message, indentation=None):
        if indentation == None:
            indentation = self._indent
        self._log_cmd_hist()
        self._logger.debug(' '*indentation + colorama.Fore.BLUE + str(message))

    def log_error(self, message, indentation=None):
        if indentation == None:
            indentation = self._indent
        self._log_cmd_hist()
        self._logger.error(' '*indentation + colorama.Style.BRIGHT + colorama.Fore.RED + str(message))

    def log_critical(self, message, indentation=None):
        if indentation == None:
            indentation = self._indent
        self._log_cmd_hist()
        self._logger.critical(' '*indentation + colorama.Style.BRIGHT + colorama.Fore.RED + str(message))

    def log_header(self, message, indentation=None):
        if indentation == None:
            indentation = self._indent
        self._log_cmd_hist()
        self._logger.info(' '*indentation + colorama.Style.BRIGHT + str(message))

    def _log_cmd_hist(self):
        current_hist_length = self.readline.get_current_history_length()
        if current_hist_length > self._last_hist_item_idx:
            for index in range(self._last_hist_item_idx+1, current_hist_length+1):
                self._logger.debug(self.readline.get_history_item(index))
        self._last_hist_item_idx = current_hist_length

    def _set_formatters(self, log_msg_type):
        if log_msg_type == 'info':
            file_format = logging.Formatter('%(asctime)s %(levelname)-5s: # %(message)s')
            scr_format = logging.Formatter('%(message)s')
        elif log_msg_type == 'call':
            file_format = logging.Formatter('%(asctime)s %(message)s')
            scr_format = logging.Formatter('')
        self._ch.setFormatter(scr_format)
        self._fh.setFormatter(file_format)

def _simplify_rapx(s):
    p = re.compile("rap.")
    _a = 0
    found_rapx = []
    while _a != None:
        _a = re.search(p, s)
        if _a != None:
            rapx = s[_a.start():_a.end()]
            s = s.replace(rapx, 'RAP{}'.format(rapx.replace('rap','')))
            found_rapx.append(rapx)

    for rapx in found_rapx:
        p = re.compile("<.*module '" + rapx.upper() + "'.*" + rapx.upper() + "\.py'>")
        _a = re.search(p, s)
        s = s.replace(s[_a.start():_a.end()], rapx)

    return s

def _simplify_rapx2(s):
    replacement_keys = replacement_dict.keys()
    for key in replacement_keys:
        s = s.replace(key, replacement_dict[key])
    return s

def log_call(func):
    @wraps(func)
    def fn(*a, **ka):
        try:
            replacement_dict[a[1].__str__()] = a[1].get_name()
        except:
            pass
        evk_logger._log_cmd_hist()
        if (evk_logger._max_call_level != None) and (evk_logger._call_level > evk_logger._max_call_level):
            evk_logger._set_formatters('info')
            evk_logger._call_level = evk_logger._call_level + 1
            res = None
            try:
                res = func(*a, **ka)
            except:
                traceback.print_exc()
            evk_logger._call_level = evk_logger._call_level - 1
            return res
        evk_logger._set_formatters('call')
        prefix = 'CALL [{}] :'.format(evk_logger._call_level) + ' ' + (evk_logger._call_level)*'    '
        if CALL_ENTRY_PROCESS:
            _a = a[1:]
            if _a == ():
                p_ka = ('**',ka)
                debug_output_str = '{}{}{}'.format(prefix, func.__qualname__, p_ka).replace("'**', ", "**")
            elif ka == {}:
                debug_output_str = '{}{}{}'.format(prefix, func.__qualname__, _a)
            else:
                p_a_ka = _a + ('**',ka)
                debug_output_str = '{}{}{}'.format(prefix, func.__qualname__, p_a_ka).replace("'**', ", "**")
            # Replace complete rapX module with simple rapX
            debug_output_str = _simplify_rapx2(debug_output_str)
            evk_logger._logger.debug(debug_output_str)
        evk_logger._fh.flush()
        evk_logger._set_formatters('info')
        evk_logger._call_level = evk_logger._call_level + 1
        res = None
        try:
            res = func(*a, **ka)
        except:
            traceback.print_exc()
        evk_logger._call_level = evk_logger._call_level - 1
        return res
    return fn
