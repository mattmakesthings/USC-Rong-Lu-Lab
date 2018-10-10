#! /usr/bin/python2.7
from __future__ import division
################################################################################
data_folder = "/home/matt/Documents/USC-Rong-Lu-Lab/ania/Aging/"
key_date = "D420"
time_unit = "D"
cell_types = ['Cgr','Cb']
threshold = 0.2
################################################################################
output_file_name = "lineage bias graph"

import pandas as pd

def get_times(df,cell_type = None):
    time_list = []
    for col_name in df.columns:
        if cell_type != None:
            if cell_type in col_name:
                m = re.search(time_unit + "[0-9]+",col_name)
                if m is not None:
                    s = m.group(0)
                    time_list.append(s)
        else:
            m = re.search(time_unit + "[0-9]+",col_name)
            if m is not None:
                s = m.group(0)
                time_list.append(s)
    return sorted(set(time_list))



if __name__ == "__main__":
    
