# this script combines multiple files to compare
# specimens over time

import pandas as pd
import os
import re
from data_regroup import load_data, prepend_folder, create_path

time_unit = "mo"

data_file = 'IL10KO 1.0 4mo RAW.xls'
sub_folder = 'IL10KO'
table_file = 'IL10KO 1.0 Table 01.xlsx'
table_folder = 'Table'

load_folder = 'Transposed Calculated for Prism'
load_folder = os.path.join(load_folder,sub_folder)

save_folder = 'Transposed Calculated for Prism'

load_folder = prepend_folder(load_folder)
save_folder = prepend_folder(save_folder)
table_folder = prepend_folder(table_folder)

def grp(pat,txt):
    r = re.search(pat,txt)
    return r.group(0) if r else '&'


def sort_files(file_list,time_unit):
    file_list.sort(key= lambda l: grp("[0-9]" + time_unit,l))
    file_list.sort(key= lambda l: grp("[0-9].[0-9]" ,l))

if __name__ == "__main__":

    file_list = os.listdir(load_folder)
    sort_files(file_list,time_unit)
    print file_list
    #iterate through files in directory
    for f in file_list:
        print f
        load_path = create_path(load_folder,f, ' GraphPad Transposed ')
        df = load_data(load_path,sheet_name = None)
        sheet_names = list(df)

        #iterate through sheets in file
        for sheet in sheet_names:
            print df[sheet].columns
        break
