# utils

import numpy as np
import pandas as pd
from datetime import datetime
from scipy.constants import speed_of_light,Planck,Boltzmann

def read_out(file_path, flag_header = True):
    if flag_header:
        # Read the lines in file
        with open(file_path) as ifile:
            bool = True
            line = str()
            while bool:
                prevline = line
                line = ifile.readline()
                if not line.startswith('#'):
                    bool = False
        # Last commented line is header
        header = prevline
        # Strip line and remove '#' 
        header = header[1:].strip().split()
        table = pd.read_csv(file_path, delimiter="\\s+", names=header, comment='#', dtype='float64')
    else:
        table = pd.read_csv(file_path, delimiter="\\s+", header=None, comment='#', dtype='float64')
    return table

def read_lyr(file_path, n_layers=55):
    edges = pd.read_csv(
        file_path,
        header=None,
        comment="#",
        delimiter='\\s+',
        nrows=n_layers+1,   # number of atmospheric layers
        )
    with open(file_path) as ifile:
        lines = ifile.readlines()
        start = None
        for i, line in enumerate(lines):
            if line.startswith('#  Layer'):
                header_edges = line.strip().split()[1:]
            if line.startswith('#   Low[km]'):
                header_layers = line.strip().split()
                start = i + 2
                break
    layers = pd.read_csv(
        file_path,
        header=None,
        delimiter='\\s+',
        skiprows=start,
        nrows=n_layers)
    edges.columns = header_edges
    layers.columns = header_layers
    return edges, layers

def safe_log(x, eps=1e-323):
    result = np.where(x > eps, x, np.log(eps))     
    np.log(result, out=result, where=result > 0)     
    return result

def transform_date(date_str, format1 = '%Y/%m/%d %H:%M', format2 = '%Y%m%d-%H%M'):
    date = datetime.strptime(date_str, format1)
    new_format_date = datetime.strftime(date, format2)
    return new_format_date

def name_file(type, date, lat, lon):
    return f"{type}_{'{:.0f}'.format(lat)}_{'{:.0f}'.format(lon)}_{transform_date(date)}"