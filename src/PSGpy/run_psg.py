# *******************************************************
# Lorenzo Buriola - University of Bologna - CNR-ISAC
# PSGpy - run_psg.py
# Python wrapper for run PSG within python apps
# ******************************************************* 

import PSGpy.docker_utils as docker_utils
from requests import post
from warnings import warn
import pandas as pd
import numpy as np
import tempfile
import os
import PSGpy.cfg as cfg
from PSGpy.utils import read_out

def run_psg(cfg_file, out_file = 'temp.txt', 
            kind = 'rad', wgeo = 'y', wephm = 'n', watm = 'n', whdr = 'y',
            local = True, verbose = True,
            docker_socket = 'unix:///run/user/1007/docker.sock'):
    """
    It runs PSG requesting to http

    Parameters
    ----------
    cfg_file: string - path of the configuration file
    type: string - type of output wanted, default is Radiance (rad)
    out_file: string - path of the output file
    local: boolean - if run psg locally or not, default is yes (not local run will raise a warning)
    verbose: boolean - if print details, default is yes
    """

    # Check if type selected exists
    kind_list = ['rad', 'noi', 'trn', 'atm', 'str', 'tel', 'srf', 'cfg', 'ret', 'lyo', 'lyr', 'lyc', 'all']
    if kind not in kind_list:
        warn(f'{kind} is not a known type, output file will be empty!')

    # Check for wgeo
    if wgeo not in ['y', 'n']:
        warn(f'{wgeo} is not a known type, output file will be empty!')
    
    #Check for wephm
    wephm_list = ['y', 'N', 'T', 'S', 'P', 'n']
    if wephm not in wephm_list:
        warn(f'{wephm} is not a known type, output file will be empty!')

    # Check for watm
    if watm not in ['y', 'n']:
        warn(f'{watm} is not a known type, output file will be empty!')
    
    # Check for watm
    if whdr not in ['y', 'n']:
        warn(f'{whdr} is not a known type, output file will be empty!')
        
    data = {
        'type': kind,
        'wgeo' : wgeo,
        'wephm' : wephm,
        'watm' : watm,
        'whdr' : whdr,
        'file': open(cfg_file).read(),
    }
    if local == True:
        url = 'http://localhost:3000/api.php'
        # Check if PSG is running locally
        if not docker_utils.is_container_running('psg', url=docker_socket):
            raise Exception('Container psg is not running, please start container or select local=False')
    else:
        url = 'https://psg.gsfc.nasa.gov/api.php'
    # 'curl' command
    response = post(url, data=data)                 
    if verbose == True:
        print(f'PSG is running at {url}')
        print(f'type = {kind}')
        print(f'Input file: {cfg_file}')
        print(f'Output file: {out_file}')
    # write to output file
    with open(out_file, 'w') as ofile:
        ofile.write(response.text)                  

def run_psg_forw(ifile, ofile, w1, w2, dw,
                    kind = 'rad', wgeo = 'y', wephm = 'n', watm = 'n', whdr = 'y',
                    local = True, verbose = False,
                    docker_socket = 'unix:///run/user/1007/docker.sock'):
    cfg_df = cfg.read_cfg(ifile)
    cfg_df['GENERATOR-RESOLUTION'] = dw
    F1 = np.round(w1,4)
    F2 = np.round(w2,4)
    ranges = np.round(np.arange(F1, F2+40, 40), decimals=4)
    temp_files = []
    with tempfile.TemporaryDirectory() as tmpdir:
        temp_files = []
        for i in range(len(ranges)-1):
            if verbose:
                print(f"Running PSG for range {ranges[i]}-{ranges[i+1]} cm-1")
            cfg_df['GENERATOR-RANGE1'] = ranges[i]
            cfg_df['GENERATOR-RANGE2'] = ranges[i+1]
            cfg.dict_to_cfg(cfg_df, 'temp.txt')
            opath = os.path.join(tmpdir, f'psg_{kind}_freq{ranges[i]}_{ranges[i+1]}')
            kind_list = ['rad', 'trn', 'atm', 'str', 'srf']
            if kind not in kind_list:
                warn(f'{kind} is not a known type, ERROR')
                return
            run_psg(cfg_file='temp.txt', out_file=opath, 
                    kind = kind, wgeo = wgeo, wephm = wephm, watm = watm, whdr = whdr,
                    local = local, verbose = verbose,
                    docker_socket = docker_socket)
            temp_files.append(opath)
        rad = pd.concat((read_out(file).iloc[:int(40/dw)]  for file in temp_files), ignore_index= True)
        rad.sort_values(by='Wave/freq', ignore_index=True, inplace=True)
        rad.to_csv(ofile, index=False)
