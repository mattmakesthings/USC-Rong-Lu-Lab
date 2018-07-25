#! /usr/bin/python2.7

# script to automate the execution of converting raw data
# to prism friendly copy and paste formatting


import os

import data_regroup as dr
import append_percent as ap
import subtype_sheets as ss

#versioning scheme
#major_version.year.month.day.release_of_day
from version import get_version
version = get_version()


#iterator over all files in a directory
data_file = 'CLP 2.0 2mo RAW.xls'
data_folder = 'RAW Data/'

#table file
table_file = 'HSC-CLP 2.0 Table.xlsx'
table_folder = 'Table/'

save_folder_dr = 'Rearranged Data/'
save_folder_ap = 'Calculated for Prism/'
save_folder_ss = 'Transposed Calculated for Prism/'

data_folder = dr.prepend_folder(data_folder)
table_folder = dr.prepend_folder(table_folder)
save_folder_dr = dr.prepend_folder(save_folder_dr)
save_folder_ap = dr.prepend_folder(save_folder_ap)
save_folder_ss = dr.prepend_folder(save_folder_ss)

#max length of subgroups
chimerism = 10

if __name__ == "__main__":

#data regroup
    # load data into pandas dataframe
    df_RAW = dr.load_data(data_folder + data_file)
    # load table data into dataframe
    df_table = dr.load_table(data_folder + table_file)

    # group data
    df_RAW = dr.get_grouped_data(df_RAW,df_table)

    #save data to excel file

    save_path = dr.create_path(save_folder_dr,data_file,' Rearranged ')
    dr.save_to_excel(save_path,df_RAW)

#append percent
    rearranged_df = ap.load_data(save_path)
    all_df , subtype_df , gp_paste_df = ap.create_dfs(rearranged_df)

    save_path = ap.create_path(save_folder_ap,data_file,' GraphPad ')
    ap.save_to_excel(save_path,all_df,rearranged_df,subtype_df,gp_paste_df)

#subtype_sheets
    #load data into pandas dataframe
    gp_paste_df = ss.load_excel(save_path)
    save_path = dr.create_path(save_folder_ss,data_file,' Graph Pad Transposed ')
    writer = ss.create_cell_sheets(gp_paste_df,save_path)
    ss.save_to_excel(writer)
