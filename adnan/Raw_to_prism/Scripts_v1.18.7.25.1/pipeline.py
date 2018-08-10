#! /usr/bin/python2.7

# script to automate the execution of converting raw data
# to prism friendly copy and paste formatting
'''
Directory structure::
    root folder
        Data
        Table
        Scripts_<version_identifier>

Primary Variables - Will be modified most often
    data_folder - contains the file(s) of raw data to be operated on
    table_file - Groups specimens according to column within table
    table_folder - contains table_file

Secondary Variables - Modify at user discretion, mainly names of folders to be created
    sub_folder - Use if multiple groups of data will be contained within the data_folder
                 rename this to match the subfolder containing the data you wish to operate on.
                 Otherwise leave blank (sub_folder = ''). Example folder structure
                    root folder
                        Data
                            sub_folder
                        Table
                        Scripts_<version_identifier>

    save_folder_(dr,ap,ss) - These variables name the folders at their respective steps of
                             the pipeline.
'''
################################################################################
# Primary Variables
data_folder = 'Data'
table_file = 'HSC-CLP 2.0 Table.xlsx'
table_folder = 'Table'
################################################################################
# Secondary Variables
sub_folder = ''
save_folder_dr = 'Rearranged Data'
save_folder_ap = 'Calculated for Prism'
save_folder_ss = 'Transposed Calculated for Prism'

import os
import data_regroup as dr
import append_percent as ap
import subtype_sheets as ss

#versioning scheme
#major_version.year.month.day.release_of_day
from version import get_version
version = get_version()

data_folder = os.path.join(data_folder,sub_folder)
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
chimerism = ss.chimerism
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
