import os
import h5py
import pandas as pd
from env_config import env_config

class Register():

    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super(Register, cls).__new__(cls)
            cls.__instance.__initialized = False
        return cls.__instance

    def __init__(self,reg_map_file=os.path.join(env_config.register_map_path(),'reg_map.h5')):
        self.reg_map,self.regs,self.df_date,self.regs_inv,self.defaults=self.init_regs(reg_map_file)

    #Read register map from file into dataframe and dictionary
    def init_regs(self, reg_map_file=os.path.join(env_config.register_map_path(),'reg_map.h5')):
        #print ('Register Map Path: {}'.format(reg_map_file))
        store=pd.HDFStore(reg_map_file)
        df_reg_map=store['df_reg_map']
        df_regs=store['df_regs']
        df_date=store['df_date']
        store.close()
        regs=df_regs.T.to_dict()
        #Create inverse regs dictionary
        regs_inv={}
        for k,v in regs.items():
            regs_inv[v['addr']]=k
        #Pick selected columns from the reg_map DataFrame
        df=df_reg_map[df_reg_map['Addr'].notnull()][['Reg Name','Field Name','Msb','Lsb','Type','Default']]
        
        #Assemble to dictionary with register names as keys
        #Keep default values in a separate dictionary
        reg_map={}
        defaults={}
        for index, row in df.iterrows():
            reg_name=row['Reg Name']
            if not reg_name in reg_map:
                defaults[reg_name]=int(row['Default'])<<row['Lsb']
                reg_map[reg_name]={row['Field Name']:{'Msb':int(row['Msb']),'Lsb':int(row['Lsb']),'Type':row['Type']}}
            else:
                defaults[reg_name]+=(int(row['Default'])<<row['Lsb'])
                reg_map[reg_name].update({row['Field Name']:{'Msb':int(row['Msb']),'Lsb':int(row['Lsb']),'Type':row['Type']}})
        
        return reg_map,regs,df_date,regs_inv,defaults

