import math
import datetime
import time
import functools
import numpy as np
import matplotlib.pyplot as plt
import evk_logger
from scipy.odr import Model, Data, ODR
from scipy.stats import linregress

### int -> list ###
def int2intlist(x, intmax=256, num_ints=0):
    """Convert x (integer) into list of integers.
       The size of each integer in the list can optionally be controlled
       by intmax so that the integer range is 0 to intmax-1 (default: 0-255).
       Number integers in the list can optionally be controlled by parameter num_ints,
       where num_ints=0 (default) means minimum number of integers required.
    """
    vals = []
    temp = x
    if (num_ints == 0):
        if (x != 0):
            num_ints=int(math.ceil(math.log(x,intmax)))
        else:
            num_ints = 1
    for i in range(num_ints-1,-1,-1):
        vals.append(int(temp//intmax**i))
        temp=temp%intmax**i
    return vals



### list -> int ###
def intlist2int(intlist, intmax=256):
    """Convert list of integers (range: 0 - intmax-1) to integer."""
    return functools.reduce(lambda x, y: x * intmax + y, intlist)


### list -> list ###
def intlist2intlist(intlist,intmax_out,num_ints=0,intmax_in=256):
    return int2intlist(intlist2int(intlist,intmax_in),intmax_out,num_ints)


def fhex(data, size=0, select='all'):
    """Return a sized hex-string of value"""
    if isinstance(data, int):
        return '0x{:0{}X}'.format(data,size)
    elif isinstance(data, list):
        data_l = []
        for data_int in data:
            if isinstance(data_int, int):
                data_l.append('0x{:0{}X}'.format(data_int,size))
            elif isinstance(data_int, list):
                data_l.append(fhex(data_int,size))
            elif isinstance(data_int, tuple):
                data_l.append(tuple(fhex(list(data_int),size)))
            else:
                data_l.append('{:}'.format(data_int))
        return data_l
    elif isinstance(data, tuple):
        return tuple(fhex(list(data),size))
    elif isinstance(data, dict):
        data_d = {}
        if select is None:
            select = {}
        elif isinstance(select, list):
            new_sel={}
            for sel in select:
                new_sel[sel]=1
            select=new_sel
        for key,val in data.items():
            if (((key in select) and select[key]) or (select == 'all')):
                if isinstance(val, int):
                    data_d[key] = '0x{:0{}X}'.format(val,size)
                elif isinstance(val, list):
                    data_d[key] = fhex(val,size)
                elif isinstance(val, tuple):
                    data_d[key] = tuple(fhex(list(val),size))
                else:
                    data_d[key] = '{:}'.format(val)
            else:
                data_d[key] = val
        return data_d
    else:
        return data


def str2int(data, base=0):
    """Convert a string to value assuming base"""
    data_list = []
    if isinstance(data, str):
        return int(data,base)
    elif isinstance(data, list):
        for data_str in data:
            if isinstance(data_str, str):
                data_list.append(int(data_str,base))
            elif isinstance(data_str, list):
                data_list.append(str2int(data_str,base))
            else:
                data_list.append('{:}'.format(data_str))
        return data_list


def reverse_bits(x, start_pos, stop_pos):
    answer = x
    for i in range(start_pos, stop_pos + 1):
        if (x & (1 << i)):
            answer |= (1 << (stop_pos + start_pos - i))
        else:
            answer &= ~(1 << (stop_pos + start_pos - i))
    return answer
    
def ashl(val,offset,nof_bits=None):
    val = val<<offset
    if nof_bits is not None:
        val = val & (2**nof_bits-1)
    return val
lshl = ashl
shl  = lshl

def mshl(val,offset,nof_bits):
    return ((val & (2**nof_bits-1))<<offset)

def ashr(val,offset,nof_bits=None):
    val = val>>offset
    if nof_bits is not None:
        val = val & (2**nof_bits-1)
    return val

def lshr(val,offset,nof_bits=None):
    if nof_bits is not None:
        val = val & (2**nof_bits-1)
    return (val>>offset)
shr = lshr
mshr = lambda val,offset,nof_bits:lshr(val,offset,nof_bits)

def mshr(val,offset,nof_bits):
    val = val & (2**nof_bits-1)
    return ((val & (2**nof_bits-1))>>offset)

def testBit(int_type, offset):
    mask = 1 << offset
    return(int_type & mask)

def clearBit(int_type, offset):
    mask = ~(1 << offset)
    return(int_type & mask)

def get_time_stamp(fmt='%Y-%m-%d %H:%M:%S'):
    return datetime.datetime.now().strftime(fmt)


def timediff(to_id=None):
    tp = time.monotonic_ns()
    if to_id is None:
        return tp
    else:
        return tp-to_id

def _twoscomp2dec(val, nobits):
    val_filt = val & (2**nobits - 1)
    if val_filt >= 2**(nobits-1):
        return -2**nobits+val_filt
    else:
        return val_filt
def twoscomp2dec(val, nobits):
    if isinstance(val, list):
        res = [_twoscomp2dec(elem, nobits) for elem in val]
    else:
        res = _twoscomp2dec(val, nobits)
    return res


def _dec2twoscomp(val, nobits):
    return val & (2**nobits - 1)
def dec2twoscomp(val, nobits):
    if isinstance(val, list):
        res = [_dec2twoscomp(elem, nobits) for elem in val]
    else:
        res = _dec2twoscomp(val, nobits)
    return res


def _binoffs2dec(val, nobits):
    val_filt = val & (2**nobits - 1)
    return val_filt - 2**(nobits-1)
def binoffs2dec(val, nobits):
    if isinstance(val, list):
        res = [_binoffs2dec(elem, nobits) for elem in val]
    else:
        res = _binoffs2dec(val, nobits)
    return res


def _dec2binoffs(val, nobits):
    val_filt = val + 2**(nobits-1)
    return val_filt & (2**nobits - 1)
def dec2binoffs(val, nobits):
    if isinstance(val, list):
        res = [_dec2binoffs(elem, nobits) for elem in val]
    else:
        res = _dec2binoffs(val, nobits)
    return res


def twoscomp2volt(val, nobits=11, volt=1.2):
    if isinstance(val, list):
        res = [twoscomp2dec(elem,nobits)/2**(nobits-1)*volt for elem in val]
    else:
        res = twoscomp2dec(val,nobits)/2**(nobits-1)*volt
    return res


def _volt_limited(val,nobits,limits):
    if val >= limits[1]-2**-nobits:
        val = limits[1]-2**-nobits
    if val < limits[0]:
        val = limits[0]
    return val
def volt2twoscomp(val, nobits=11, volt=1.2):
    if isinstance(val, list):
        res = [dec2twoscomp(round(_volt_limited(elem,nobits,[-volt,volt])*2**(nobits-1)/volt),nobits) for elem in val]
    else:
        res = dec2twoscomp(round(_volt_limited(val,nobits,[-volt,volt])*2**(nobits-1)/volt),nobits)
    return res


def binoffs2volt(val, nobits=11, volt=1.2):
    if isinstance(val, list):
        res = [binoffs2dec(elem,nobits)/2**(nobits-1)*volt for elem in val]
    else:
        res = binoffs2dec(val,nobits)/2**(nobits-1)*volt
    return res

def volt2binoffs(val, nobits=11, volt=1.2):
    if isinstance(val, list):
        res = [dec2binoffs(round(_volt_limited(elem,nobits,[-volt,volt])*2**(nobits-1)/volt),nobits) for elem in val]
    else:
        res = dec2binoffs(round(_volt_limited(val,nobits,[-volt,volt])*2**(nobits-1)/volt),nobits)
    return res


def print_dict(dict2print, indent):
    for key,val in dict2print.items():
        evk_logger.evk_logger.log_info('{:<10}: {:<6}'.format(key,val),indent)
        
        
  
  
def linregr(x, y, method='orthogonal'):
    """Perform an Orthogonal Distance Regression (method="orthogonal") or
    linear MMSE on the given data.

    Arguments:
    x: x data
    y: y data

    Returns:
    [offset, slope]
    """
    def f(p, x):
        return (p[1] * x) + p[0]

    linreg = linregress(x, y)
    if method == 'orthogonal':
        mod    = Model(f)
        dat    = Data(x, y)
        od     = ODR(dat, mod, beta0=linreg[0:2])
        out    = od.run()
        return {'offs':out.beta[0], 'slope':out.beta[1]}
    else:
        return {'offs':linreg.intercept, 'slope':linreg.slope}


def linregr_plot(x, y, p=None):
    x = np.array(x)
    y = np.array(y)
    # plotting the actual points as scatter plot
    plt.scatter(x, y, color = "m",
               marker = "o", s = 30)
  
    # predicted response vector
    if p is None:
        p = linregr(x,y)
    y_pred = p['offs'] + p['slope']*x
  
    # plotting the regression line
    plt.plot(x, y_pred, color = "g")
  
    # putting labels
    plt.xlabel('x')
    plt.ylabel('y')
  
    # function to show plot
    plt.show()