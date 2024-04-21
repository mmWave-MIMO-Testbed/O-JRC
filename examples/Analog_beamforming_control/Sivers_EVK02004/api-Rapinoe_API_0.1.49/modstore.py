import json
import os
from pathlib import Path

dir_path = os.path.dirname(os.path.realpath(__file__))
config_path = dir_path + "/config/"
Path(config_path).mkdir(parents=True, exist_ok=True)

def save(mod):
    class obj():
        def __init__(self):
            pass
    x = obj()
    for member in dir(mod):
        accepted_type = eval("isinstance(mod." + member + ", (float, int, str, list, dict, tuple))")
        if accepted_type and not member.startswith("__"):
            exec("x."+member+"=mod."+member)
    with open( config_path + mod.get_name() + ".json" , "w" ) as fp:
        json.dump(x.__dict__, fp, sort_keys=True, indent=4)

def load(mod):
    class obj():
        def __init__(self):
            pass
    x = obj()
    with open( config_path + mod.get_name() + ".json" , "r" ) as fp:
        x = json.load(fp)
    for key in x:
        exec("mod."+key+"=x['"+key+"']")
