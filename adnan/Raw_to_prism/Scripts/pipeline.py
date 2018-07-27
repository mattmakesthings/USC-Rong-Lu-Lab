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

# the Data folder has been restructured so that all files of a group
# sub_folder specifies the sub folder for all folders created
# like the 'IL10KO' group are under the same subfolder
sub_folder = 'IL10KO'
data_folder = 'Data'
data_folder = os.path.join(data_folder,sub_folder)
#table file
table_file = 'IL10KO 1.0 Table 01.xlsx'
table_folder = 'Table'



save_folder_dr = 'Rearranged Data'
save_folder_ap = 'Calculated for Prism'
save_folder_ss = 'Transposed Calculated for Prism'

save_folder_dr = os.path.join(save_folder_dr,sub_folder)
save_folder_ap = os.path.join(save_folder_ap,sub_folder)
save_folder_ss = os.path.join(save_folder_ss,sub_folder)

data_folder = dr.prepend_folder(data_folder)
table_folder = dr.prepend_folder(table_folder)
save_folder_dr = dr.prepend_folder(save_folder_dr)
save_folder_ap = dr.prepend_folder(save_folder_ap)
save_folder_ss = dr.prepend_folder(save_folder_ss)

table_path = os.path.join(table_folder,table_file)

#max length of subgroups
ss.chimerism = 10

if __name__ == "__main__":

    for data_file in os.listdir(data_folder):
        if data_file.endswith('.xls') or data_file.endswith('.xlsx'):
            print data_file
        #data regroup
            # load data into pandas dataframe
            data_path = os.path.join(data_folder,data_file)
            df_RAW = dr.load_data(data_path)
            # load table data into dataframe
            table_path = os.path.join(table_folder,table_file)
            df_table = dr.load_table(table_path)
            # group data
            df_RAW = dr.get_grouped_data(df_RAW,df_table)

            #save data to excel file
            dr.create_save_folder(save_folder_dr)
            save_path = dr.create_path(save_folder_dr,data_file,' Rearranged ')
            dr.save_to_excel(save_path,df_RAW)

        #append percent
            rearranged_df = ap.load_data(save_path)
            all_df , subtype_df , gp_paste_df = ap.create_dfs(rearranged_df)

            dr.create_save_folder(save_folder_ap)
            save_path = ap.create_path(save_folder_ap,data_file,' GraphPad ')
            ap.save_to_excel(save_path,all_df,rearranged_df,subtype_df,gp_paste_df)

        #subtype_sheets
            #load data into pandas dataframe
            gp_paste_df = ss.load_excel(save_path)
            df_table = dr.load_data(table_path)
            save_path = dr.create_path(save_folder_ss,data_file,' Graph Pad Transposed ')
            writer = ss.create_cell_sheets(gp_paste_df,df_table,save_path)
            dr.create_save_folder(save_folder_ss)
            ss.save_to_excel(writer)
