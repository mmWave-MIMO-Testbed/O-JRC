# Reset chip
# As part of reset, bias bist for avdd1v2 and vdd2v5 is enabled
host.reset(rap0)

fhex(host.spi.rd(rap0, 'chip_id'), 8)


freq_ref = 245.764750e6
#freq_ref = 122.88e6

def synth_status():
    status = host.spi.rd(rap0, 'sm_config_status')
    print("  lock status: ", fhex(host.spi.rd(rap0, 'sm_config_status'), 2))
    print("  lock status: ", fhex(host.spi.rd(rap0, 'sm_config_status'), 2))
    print("  dig_tune:    ", fhex(host.spi.rd(rap0, 'vco_digtune_read'), 2))
    print("  ibias:       ", fhex(host.spi.rd(rap0, 'vco_ibias_read'), 2))


def freq_calc(freq, ref=freq_ref):
    freq_rel = freq/3.0/ref
    N = int(freq_rel)
    frac = round((freq_rel-N)*2**24)
    return N, frac


def freq_set(freq, frac_mode=None, sd_order=None, ref=freq_ref):
    (N, k) = freq_calc(freq, ref)
    sm_set(N, k, frac_mode=frac_mode, sd_order=sd_order)


def sm_set(N, k=0, frac_mode=None, sd_order=None):
    if frac_mode == None:
        frac_mode = (host.spi.rd(rap0, 'sd_config') & 1)
    if sd_order == None:
        sd_order = ((host.spi.rd(rap0, 'sd_config') >> 2) & 3)
    if (frac_mode == 0) | (frac_mode == False):
        sd_cfg(rst_n=0, order=sd_order)
        print(
            "  Integer mode active. N={:} (used), k={:} (ignored)".format(N, k))
        print("  RF frequency: {:7.6} GHz (LO = {:8.7} GHz)".format(
            N*3.0*freq_ref/1e9, N*freq_ref/1e9))
    else:
        sd_cfg(rst_n=1, order=sd_order)
        print(
            "  Fractional mode active. N={:} (used), k={:} (used)".format(N, k))
        print("  RF frequency: {:9.8} GHz (LO = {:8.7} GHz)".format(
            (N*3.0*freq_ref+k/2**24*freq_ref)/1.0e9, (N*freq_ref+k/2**24*freq_ref)/1.0e9))
    print("lock start")
    synth_status()
    host.spi.wrrd(rap0, 'sd_n', N)
    host.spi.wrrd(rap0, 'sd_k', k)
    host.spi.wrrd(rap0, 'sm_sd_fsm_ctrl', 0x0A)
    host.spi.wrrd(rap0, 'sm_sd_fsm_ctrl', 0x05)
    synth_status()
    print("lock start done")


def sd_cfg_info():
    cfg = host.spi.rd(rap0, 'sd_config')
    print("prbs_en       : {:}".format((cfg >> 7) & 1))
    print("dither_en     : {:}".format((cfg >> 4) & 7))
    print("order         : {:}".format((cfg >> 2) & 3))
    print("no_rst        : {:}".format((cfg >> 1) & 1))
    print("rst_n         : {:}".format((cfg >> 0) & 1))
    cfg = host.spi.rd(rap0, 'sm_sd_fsm_config')
    print("sd_wait_on_sm : {:}".format(cfg))
    cfg = host.spi.rd(rap0, 'sm_sd_fsm_delay')
    print("sm_sd_delay   : 0x{:X}".format(cfg))


def sd_cfg(prbs_en=None, dither_en=None, order=None, no_rst=None, rst_n=None, sd_wait_on_sm=None, sm_sd_delay=None):
    cfg = host.spi.rd(rap0, 'sd_config')
    if prbs_en == None:
        wr_byte = cfg & 0x80
    else:
        wr_byte = (prbs_en & 1) << 7
    if dither_en == None:
        wr_byte = wr_byte | cfg & 0x70
    else:
        wr_byte = wr_byte | (dither_en & 7) << 4
    if order == None:
        wr_byte = wr_byte | cfg & 0x0C
    else:
        wr_byte = wr_byte | (order & 3) << 2
    if no_rst == None:
        wr_byte = wr_byte | cfg & 0x02
    else:
        wr_byte = wr_byte | (no_rst & 1) << 1
    if rst_n == None:
        wr_byte = wr_byte | cfg & 0x01
    else:
        wr_byte = wr_byte | (rst_n & 1) << 0
    host.spi.wr(rap0, 'sd_config', wr_byte)

    if sd_wait_on_sm != None:
        host.spi.wrrd(rap0, 'sm_sd_fsm_config', sd_wait_on_sm)

    if sm_sd_delay != None:
        host.spi.wrrd(rap0, 'sm_sd_fsm_delay', sm_sd_delay)

    sd_cfg_info()


# VCO, PLL and SM setup
host.spi.wrrd(rap0, 'biastop_en', (1 << 5)+(1 << 4)+(1 << 3)+(1 << 2))
host.spi.wrrd(rap0, 'vco_en', (1 << 6)+(1 << 4)+(1 << 3)+(1 << 1)+1)
host.spi.wrrd(rap0, 'vco_digtune_ibias_override', 0)
host.spi.wrrd(rap0, 'pll_ref_sel', 1)
host.spi.wrrd(rap0, 'pll_config', 0x04)
host.spi.wrrd(rap0, 'pll_ld_config', 0x10)
host.spi.wrrd(rap0, 'pll_en', (1 << 7)+(1 << 6)+(1 << 5)+(1 << 4)+(1 << 1)+1)
host.spi.wrrd(rap0, 'sm_clk_config', 25+(200 << 8)+(246 << 24)+(25 << 32)) # 245.76 MHz ref
#host.spi.wrrd(rap0, 'sm_clk_config', 12+(200 << 8)+(123 << 24)+(12 << 32))
host.spi.wrrd(rap0, 'sm_dac', 163)
host.spi.wrrd(rap0, 'sm_dac_cal', 8)
host.spi.wrrd(rap0, 'sm_en', 3)
host.spi.wrrd(rap0, 'sd_n', 30)

# Trigger SM to lock PLL
# vco_digtune and vco_ibias should have values close to 0x5D and 0x20
# sm_config_status should be 0x21 after first read and then 0x31 (PLL unlocked -> locked indication)
host.spi.wrrd(rap0, 'sm_sd_fsm_ctrl', 0)
host.spi.wrrd(rap0, 'sm_sd_fsm_ctrl', 1)
synth_status()

# Set new PLL N-div value
# vco_digtune and vco_ibias should remain at previous values, but
# sm_config_status should now be 0x01 for both reads (PLL unlocked indication)
host.spi.wrrd(rap0, 'sd_n', 40)
synth_status()

# Trigger SM to re-lock PLL
# vco_digtune and vco_ibias should have new values close to 0x69 and 0x1E
# sm_config_status should be 0x21 after first read and then 0x31 (PLL unlocked -> locked indication)
host.spi.wrrd(rap0, 'sm_sd_fsm_ctrl', 0)
host.spi.wrrd(rap0, 'sm_sd_fsm_ctrl', 1)
synth_status()
