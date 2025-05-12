/* -*- c++ -*- */

#define FMCW_MIMO_API

%include "gnuradio.i"           // the common stuff

//load generated python docstrings
%include "FMCW_MIMO_swig_doc.i"

%{
#include "FMCW_MIMO/FMCW_MIMO_USRP.h"
#include "FMCW_MIMO/FMCW_Multiplexing.h"
#include "FMCW_MIMO/FMCW_Radar.h"
#include "FMCW_MIMO/FMCW_Radar_Plot.h"
#include "FMCW_MIMO/TDM_FMCW_Generator.h"
%}

%include "FMCW_MIMO/FMCW_MIMO_USRP.h"
GR_SWIG_BLOCK_MAGIC2(FMCW_MIMO, FMCW_MIMO_USRP);
%include "FMCW_MIMO/FMCW_Multiplexing.h"
GR_SWIG_BLOCK_MAGIC2(FMCW_MIMO, FMCW_Multiplexing);
%include "FMCW_MIMO/FMCW_Radar.h"
GR_SWIG_BLOCK_MAGIC2(FMCW_MIMO, FMCW_Radar);
%include "FMCW_MIMO/FMCW_Radar_Plot.h"
GR_SWIG_BLOCK_MAGIC2(FMCW_MIMO, FMCW_Radar_Plot);
%include "FMCW_MIMO/TDM_FMCW_Generator.h"
GR_SWIG_BLOCK_MAGIC2(FMCW_MIMO, TDM_FMCW_Generator);
