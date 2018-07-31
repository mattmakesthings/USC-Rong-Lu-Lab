# this script combines multiple files to compare
# specimens over time

import pandas as pd
import os
import re
from data_regroup import load_data, prepend_folder, create_path
from collections import OrderedDict

time_unit = "d"

data_file = 'IL10KO 1.0 4mo RAW.xls'
sub_folder = 'CLP 2.0'
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
    #file_list.sort(key= lambda l: grp("[0-9].[0-9]" ,l))
    return file_list

if __name__ == "__main__":

    file_list = os.listdir(load_folder)

    file_dict = OrderedDict(zip(file_list,[0]*len(file_list)))
    for k,v in file_dict.items():
        m = re.search(r"[0-9]+" + re.escape(time_unit), k)
        s = m.group(0).replace('d','')
        file_dict[k] = int(s)
        if '.~lock' in k:
            del file_dict[k]

    #sort file dictionary by given time unit
    file_list = []
    for key, value in sorted(file_dict.iteritems(), key=lambda (k,v): (v,k)):
        file_list.append(key)
    # print file_dict
    # for i in file_list:
    #     print i

    #create list of files for dataframe index
    f_ind = OrderedDict()
    for f in file_list:
        ind = f.replace(' Graph Pad Transposed ','')
        ind = ind.replace(' GraphPad Transposed ','')
        f_ind[f] = ind


    # iterate through file to create sheet names
    sheet_list = []
    for data_file, ind in f_ind.items():
        load_path = create_path(load_folder,data_file, '')
        df = load_data(load_path,sheet_name = None)
        sheet_names = list(df)
        print data_file
        #iterate through sheets in file
        for sheet in sheet_names:
            for name in df[sheet].index:
                sheet_list.append(name)
        break

    # create dictionary to tie
    # sheet names to dataframe
    sheet_list = [s for s in sheet_list if s != 'group']
    df_list = []
    for i in range(len(sheet_list)):
        df_list.append(pd.DataFrame(columns=))

    sheet_dict = OrderedDict(zip(sheet_list,df_list))

    print sheet_dict[sheet_list[0]]

    # iterate through files to create dataframe
    for data_file, ind in f_ind.items():
        load_path = create_path(load_folder,data_file, '')
        df = load_data(load_path,sheet_name = None)
        sheet_names = list(df)
        #print data_file
        #iterate through sheets in file
        # for sheet in sheet_names:
        #      print df[sheet]
        # break
