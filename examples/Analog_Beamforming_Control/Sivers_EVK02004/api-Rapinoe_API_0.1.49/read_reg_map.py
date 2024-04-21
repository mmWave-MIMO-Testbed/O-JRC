# -*- coding: utf-8 -*-
"""
Created on Fri Jan 15 07:30:34 2021

@author: joahal
"""

#Usage examples: /home/tools/anaconda3/bin/python read_reg_map.py 
#                /home/tools/anaconda3/bin/python read_reg_map.py ../docs/Rapinoe_reg_map_57.xlsx

import h5py
import tables
import pandas as pd
import sys
import re

if not (sys.version_info > (3, 0)): 
    print ('Use python 3')
else:
    folder_path='doc/'
    
    #Check arguments
    if len(sys.argv)>1:
        file_name=sys.argv[1]
    else:
        #file_name='Rapinoe_reg_map.PA166.xlsx'
        file_name = 'TRB02801_R5_register_map.xlsx'

    #hdf_file='reg_map.h5'
    hdf_file='reg_map_r5.h5'
    
    out_path='../'
    
    #signals_file='signals.sv'
    #sig=open(out_path+signals_file,'w') 
    
    #Compile patterns
    pat_check_array=re.compile("(.*)\[(\d+):(\d+)\]")
    pat_check_signal=re.compile(".*\[|\]")
    
    
    df=pd.read_excel(folder_path+file_name,sheet_name=None)
    #Read date and revision
    #df_date=pd.read_excel(folder_path+file_name,sheet_name='Setup',usecols="B:C",skiprows=3, nrows=1)
    df_date=pd.read_excel(folder_path+file_name,sheet_name='Setup',usecols="B:C",skiprows=0, nrows=1) # R5
    print (df_date)
    version=df_date['Revision'][0]
    date=df_date['Revision date'][0]
    print (version,date)
    
    #Read address offsets
    df_offs = pd.read_excel(folder_path+file_name,sheet_name=None,usecols="A:A",nrows=1)
    address_offsets={}
    for k,v in df_offs.items():
        #Skip the Setup tab
        if k !='Setup':
            #Read the offset
            address_offsets.update({k:int(v['Address Offset'][0],0)})
            
    #Read everything else
    df_dict = pd.read_excel(folder_path+file_name,sheet_name=None,skiprows=2)
         
    #Check if addresses and reg names are unique
    #Create dictionary with reg names as keys and addresses as values
    regs={}
    regs_group = {}
    regs_inv={}
    regs_desc = {}
    for sheet,df in df_dict.items():
        if not sheet=='Setup':
            #Drop rows with missing addresses
            df.dropna(subset=['Address'],inplace=True)
            for idx in df.index:
                sheet_addr=int(df.loc[idx,'Address'])
                addr=int(address_offsets[sheet]+sheet_addr)
                if not pd.isna(df.loc[idx,'Reg Name']):
                    reg_name=df.loc[idx,'Reg Name']
                    desc = df.loc[idx,'Description']
                    if reg_name in regs:
                        if addr!=regs[reg_name]:
                            print ('Sheet {}, Reg name already defined for {} with address {} and sheet address {}. First defined as sheet address {}'\
                                   .format(sheet,reg_name,addr,sheet_addr,regs[reg_name]-address_offsets[sheet]))
                    else:
                        regs.update({reg_name:addr})
                        regs_group.update({reg_name:sheet})
                        regs_desc.update({reg_name:desc})
                    if addr in regs_inv:
                        if reg_name!=regs_inv[addr]:
                            print ('Sheet {}, Address already defined for {} with reg_name {} and sheet address {}. First defined as {}'\
                                   .format(sheet,addr,reg_name,sheet_addr,regs_inv[addr]))
                    else:
                        regs_inv.update({addr:reg_name})
                else:
                    print ('Error: Sheet {},Reg Name is missing for sheet address {} '.format(sheet,sheet_addr))
                    
    #Check if field bit allocations overlap
    #Create dictionary reg_map of with addresses as keys
    #and values as a list of dictionaries with keys: {'Reg Name','Field Name','Msb','Lsb','Type','Default','Signal Name','Sheet'}
    reg_map={}
    reg_field_bits={}
    field_arrays={}
    for sheet,df in df_dict.items():
        if not sheet=='Setup':
            #Drop rows with missing addresses
            df.dropna(subset=['Address'],inplace=True)
            for idx in df.index:
                sheet_addr=int(df.loc[idx,'Address'])
                addr=int(address_offsets[sheet]+sheet_addr)
                if not pd.isna(df.loc[idx,'Field Name']):
                    field_name=df.loc[idx,'Field Name']
                    reg_name=df.loc[idx,'Reg Name']
                    msb=int(df.loc[idx,'Msb'])
                    lsb=int(df.loc[idx,'Lsb'])
                    bits_left=(1<<(msb-lsb+1))-1
                    bits=bits_left<<lsb
                    
                    #Handle default
                    #Set nan to 0
                    if pd.isna(df.loc[idx,'Default']):
                        default=0
                    else:
                        default=df.loc[idx,'Default']
                        if isinstance(default,str):
                            default=int(default,0)
                        else:
                            default=int(default)
                            
                    #Check default
                    if default>bits_left:
                        print ('Error: Sheet {},default value too large for reg name {},{},{}'.format(sheet,reg_name,field_name,sheet_addr))
                    #Handle signal name
                    #Set nan to ''
                    if pd.isna(df.loc[idx,'Signal Name']):
                        signal_name=''
                    else:
                        signal_name=df.loc[idx,'Signal Name']
                        
                    #Handle signal direction
                    try:
                        if pd.isna(df.loc[idx,'Dir']):
                            direction=''
                        else:
                            direction=df.loc[idx,'Dir']
                    except:
                        direction=''
                        
                    if not addr in reg_map:
                        reg_map.update({addr:[{'Reg Name':reg_name,'Field Name':field_name,'Msb':msb,'Lsb':lsb,\
                                               'Type':df.loc[idx,'Type'],'Default':default,'Signal Name':signal_name,'Sheet':sheet,'Dir':direction}]})
                        reg_field_bits.update({addr:bits})
                    else:
                        reg_map[addr].append({'Reg Name':reg_name,'Field Name':field_name,'Msb':msb,'Lsb':lsb,\
                                               'Type':df.loc[idx,'Type'],'Default':default,'Signal Name':signal_name,'Sheet':sheet,'Dir':direction})
                        #Now check if bits overlap
                        if (bits & reg_field_bits[addr]):
                            print ('Error: Sheet {},Field Name bit allocation overlap for reg name {},{},{}'.format(sheet,reg_name,field_name,sheet_addr))
                        else:
                            reg_field_bits[addr] |=bits
                    if signal_name !='':
                        if field_name != signal_name:
                            print ('Warning: Sheet {},field name not equal to signal name for reg name {},{},{}'.format(sheet,reg_name,field_name,sheet_addr))
                        
                    
                    #Look for field names of array form, split over registers
                    m=pat_check_array.match(field_name)
                    if m:
                        base=m.group(1)
                        msb=int(m.group(2))
                        lsb=int(m.group(3))
                        signal_base=''
                        if signal_name !='':
                            m=pat_check_array.match(signal_name)
                            signal_base=m.group(1)
                            signal_msb=int(m.group(2))
                            signal_lsb=int(m.group(3))
                            if (base !=signal_base) or (signal_msb != msb) or (signal_lsb !=lsb):
                                print ('Signal and field name mismatch for sheet {}, reg name {},{},{}'.format(sheet,reg_name,field_name,sheet_addr))
                        
                        if not base in field_arrays:
                            field_dict={base:{'msb':[msb],'lsb':[lsb],'sheet':[sheet],'sheet_addr':[sheet_addr],'signal_base':signal_base,'dir':[direction]}}
                            field_arrays.update(field_dict)
                        else:
                            field_arrays[base]['msb'].append(msb)
                            field_arrays[base]['lsb'].append(lsb)
                            field_arrays[base]['sheet'].append(sheet)
                            field_arrays[base]['sheet_addr'].append(sheet_addr)
                            
    #Now check if field names of array form are contiguous/complete
    signal_names={}
    for base,value in field_arrays.items():
        msb_sorted=sorted(value['msb'])
        lsb_sorted=sorted(value['lsb'])
        msb_max=msb_sorted[-1]
        lsb_min=lsb_sorted[0]
        prev_msb=-1
        #Pick first value for direction. Ignore inconsistencies for now
        direction=value['dir'][0]
        for idx,lsb in enumerate(lsb_sorted):
            if lsb !=prev_msb+1:
                print ('Error, non-contiguous field array for sheet {},{}'.format(value['sheet'],value['sheet_addr']))
            prev_msb=msb_sorted[idx]
        signal_base=value['signal_base']
        if signal_base !='':
            signal_names.update({signal_base:{'Length':msb_max-lsb_min+1,'Dir':direction}})
   
    #Add signal names not split over registers
    #to the signal_names dictionary
    for address,value in reg_map.items():
        for row in value:
            signal_name=row['Signal Name']
            if  signal_name !='':
                if pat_check_signal.match(signal_name):
                    print ('Error: signal name not of allowed form,{}, address {}'.format(signal_name,address))
                elif not pat_check_array.match(signal_name):
                    if signal_name in signal_names:
                        print ('Error: signal name already used,{}, address {}'.format(signal_name,address))
                    else:
                        signal_names.update({signal_name:{'Length':row['Msb']-row['Lsb']+1,'Dir':row['Dir']}})
    
    allocated_addresses={}                  
    #Check allocation of addresses
    tx_ram_size=24
    rx_ram_size=80
    bf_ram_size=512
    for address,value in reg_map.items():
        sheet=value[0]['Sheet']
        if sheet=='TX_RAM': 
            bits_allowed=tx_ram_size
        elif sheet=='RX_RAM':
            bits_allowed=rx_ram_size
        elif sheet=='BF_RAM':
            bits_allowed=bf_ram_size
        else:
            bits_allowed=8
        #Find the largest msb for the given address
        msb_max=0
        for row in value:
            msb=row['Msb']
            if msb>msb_max:
                msb_max=msb
        #No of addresses needed for register
        no_addr=msb_max//bits_allowed+1
        for idx in range(no_addr):
            if address+idx in allocated_addresses:
                print ('Address allocation error for sheet {}, reg name {}'.format(row['Sheet'],row['Reg Name']))
            else:
                allocated_addresses.update({address+idx:row['Reg Name']})
                
    #Write signal names to file
    # print ('Signal declarations written to {}'.format(signals_file))
    # for name,value in sorted(signal_names.items()):
        # length=value['Length']
        # direction=value['Dir']
        # if length>1:
            # if direction=='in':
                # string='  input  logic [{:<10}  {},\n'.format(str(length-1)+':0]',name)
                # sig.write(string)
            # else:
                # string='  output logic [{:<10}  {},\n'.format(str(length-1)+':0]',name)
                # sig.write(string)
        # else:
            # if direction=='in':
                # string='  input  logic{:14}{},\n'.format('',name)
                # sig.write(string)
            # else:
                # string='  output logic{:14}{},\n'.format('',name)
                # sig.write(string)
    # sig.close()
    
    #Calculate the register size for each register name
    reg_size={}
    for value in allocated_addresses.values():
        if not value in reg_size:
            reg_size[value]=1
        else:
            reg_size[value]+=1
    reg_size['ram']=bf_ram_size//8
    reg_size['tx_ram_v']=tx_ram_size//8
    reg_size['tx_ram_h']=tx_ram_size//8
    reg_size['rx_ram_v']=rx_ram_size//8
    reg_size['rx_ram_h']=rx_ram_size//8
    
    #Create dataframes suitable for hdf storage
    df_reg_map=pd.DataFrame()
    for addr,value in reg_map.items():
        for item in value:
            item.update({'Addr':addr})
            df_reg_map=pd.concat([df_reg_map,pd.DataFrame.from_dict(item,orient='index').T])
    df_reg_map.reset_index(inplace=True)
    df_reg_map.drop(['index'],axis=1,inplace=True)
    
    #Convert column types
    df_reg_map[['Msb', 'Lsb','Addr','Default']] = df_reg_map[['Msb', 'Lsb','Addr','Default']].apply(pd.to_numeric)
    
    df_regs=pd.DataFrame()
    for name,addr in regs.items():
        regs[name]={'group': regs_group[name], 'addr':addr, 'length':reg_size[name], 'desc':regs_desc[name]}
    df_regs=pd.DataFrame.from_dict(regs,orient='index')
    
    #Save dataframes to hdf
    store=pd.HDFStore(hdf_file,'w')
    store.put('df_reg_map',df_reg_map,format='table')
    store.put('df_regs',df_regs,format='table')
    store.put('df_date',df_date,format='table')
    store.close()