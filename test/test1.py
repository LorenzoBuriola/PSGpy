
import PSGpy.cfg as cfg
from PSGpy.run_psg import run_psg
from PSGpy.utils import name_file

date = '2020/07/12 10:00'
lat = 0
long = 0
    
# Generate profiles
cfg_df = {
        'OBJECT' : 'Planet',
        'OBJECT-NAME' : 'Mars',
        'GEOMETRY-REF' : 'User',
        'GEOMETRY' : 'Nadir', 
        'GEOMETRY-OBS-ALTITUDE' : '400.0',
        'GEOMETRY-ALTITUDE-UNIT' : 'km',
        'ATMOSPHERE-STRUCTURE' : 'Model_MCD',
        'GENERATOR-INSTRUMENT':'user',
        'GENERATOR-RANGE1':'100',
        'GENERATOR-RANGE2':'3000',
        'GENERATOR-RANGEUNIT':'cm',
        'GENERATOR-RESOLUTION':'5',
        'GENERATOR-RESOLUTIONUNIT':'cm'
}

cfg_df['OBJECT-DATE'] = date
cfg_df['OBJECT-OBS-LATITUDE'] = str(lat)
cfg_df['OBJECT-OBS-LONGITUDE'] = str(long)
cfg.dict_to_cfg(cfg_dict=cfg_df, file_path='cfg_temp.cfg')
run_psg(cfg_file='cfg_temp.cfg', kind='cfg', wephm = 'y', watm='y',
out_file=f"{name_file('cfg', date, lat, long)}.cfg", verbose=False)

