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
    time_unit - this is unit of time that is expressed in the filename of your data
    specimen_limit - this is the size limit of each group from the table file.
                     if set to 0, specimen_limit will be determined from table_files

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
outlier_file = 'Outliers and Warnings.xlsx'
table_folder = 'Table'
time_unit = 'd'
specimen_limit = 0
################################################################################
# Secondary Variables
sub_folder = ''
save_folder_dr = 'Rearranged Data'
save_folder_ap = 'Calculated for Prism'

save_folder_ss = 'Transposed Calculated for Prism'
graphpad_paste_folder_ss = 'Graph Pad Transposed'
chimerism_folder_ss = 'Chimerism vs. All'

save_folder_tc = 'Time course for Prism'
file_marker_tc = 'Time Course '
################################################################################

import os
import data_regroup as dr
import append_percent as ap
import subtype_sheets as ss
import time_course as tc

#versioning scheme
#major_version.year.month.day.release_of_day
from version import get_version
version = get_version()

data_folder = os.path.join(data_folder,sub_folder)
save_folder_dr = os.path.join(save_folder_dr,sub_folder)
save_folder_ap = os.path.join(save_folder_ap,sub_folder)
save_folder_ss = os.path.join(save_folder_ss,sub_folder)
save_folder_tc = os.path.join(save_folder_tc,sub_folder)

data_folder = dr.prepend_folder(data_folder)
table_folder = dr.prepend_folder(table_folder)
save_folder_dr = dr.prepend_folder(save_folder_dr)
save_folder_ap = dr.prepend_folder(save_folder_ap)
save_folder_ss = dr.prepend_folder(save_folder_ss)
save_folder_tc = dr.prepend_folder(save_folder_tc)

#folders to store output from subtype sheets (ss) script
save_folder_ss_cva = os.path.join(save_folder_ss,chimerism_folder_ss)
save_folder_ss_gp = os.path.join(save_folder_ss,graphpad_paste_folder_ss)

table_path = os.path.join(table_folder,table_file)


table_path = os.path.join(table_folder,table_file)
df_table = dr.load_table(table_path)
specimen_limit = ss.get_specimen_limit(df_table,specimen_limit)
ss.specimen_limit = specimen_limit


if __name__ == "__main__":

    for data_file in os.listdir(data_folder):
        if data_file.endswith('.xls') or data_file.endswith('.xlsx'):
            print data_file
        #data regroup
            # load data into pandas dataframe
            data_path = os.path.join(data_folder,data_file)
            df_RAW = dr.load_data(data_path)
            # group data
            df_RAW = dr.get_grouped_data(df_RAW,df_table)

            #save data to excel file
            dr.create_save_folder(save_folder_dr)
            save_path = dr.create_path(save_folder_dr,data_file,' Rearranged ')
            dr.save_to_excel(save_path,df_RAW)

        #append percent
            rearranged_df = ap.load_data(save_path)
            all_df , subtype_df , gp_paste_df, subtype_all_df = ap.create_dfs(rearranged_df)
            dr.create_save_folder(save_folder_ap)
            save_path = ap.create_path(save_folder_ap,data_file,' GraphPad ')
            ap.save_to_excel(save_path,all_df,rearranged_df,subtype_df,gp_paste_df, subtype_all_df)

        #subtype_sheets
            #load data into pandas dataframe
            load_path_ss = save_path
            gp_paste_df = ss.load_excel(load_path_ss,'GraphPad Paste')
            df_table = dr.load_data(table_path)

            save_path = dr.create_path(save_folder_ss_gp,data_file,' Graph Pad Transposed ')
            writer = ss.create_cell_sheets(gp_paste_df,df_table,save_path)
            dr.create_save_folder(save_folder_ss_gp)
            ss.save_to_excel(writer)

            #load data into pandas dataframe
            gp_paste_df = ss.load_excel(load_path_ss,'chimerism vs. all')
            df_table = dr.load_data(table_path)
            chimerism_vs_all_filename = 'chimerism vs. all ' + data_file
            save_path = dr.create_path(save_folder_ss_cva,chimerism_vs_all_filename,' Graph Pad Transposed ')
            writer = ss.create_cell_sheets(gp_paste_df,df_table,save_path)
            dr.create_save_folder(save_folder_ss_cva)
            ss.save_to_excel(writer)

    #time course
    folderlist = {save_folder_ss_gp : graphpad_paste_folder_ss
                 ,save_folder_ss_cva : chimerism_folder_ss}
    for folder, partial_filename in folderlist.iteritems():
        print partial_filename
        files = tc.get_files(folder)
        files = tc.remove_non_excel(files)
        file_dict = tc.files_to_dict(files)
        file_dict = tc.insert_time(file_dict,time_unit)

        #sort file dictionary by given time unit
        file_dict = tc.sort_time(file_dict,time_unit)

        # iterate through file to create sheet names
        df = tc.get_df_dict(folder,files[0])
        sheet_list = tc.get_sheet_names(file_dict,df)

        #create list that contain filtered specimen names
        df_col_r = tc.get_specimen_names(df,sheet_list)
        df_list = tc.list_of_df(len(sheet_list),df_col_r, file_dict.values())

        #create ordered dict to tie sheetnames to dataframes
        time_dict = tc.ordered_dict_from_lists(sheet_list,df_list)

        #fill time_dict with data from files
        time_dict = tc.fill_time_dict(file_dict,folder,time_dict,df_col_r)
        table_folder = dr.prepend_folder(table_folder)
        table_path = os.path.join(table_folder,table_file)

        #add the group row
        time_dict = tc.append_groups(time_dict,table_path,specimen_limit)

        #create outlier file
        outlier_path = os.path.join(table_folder,outlier_file)
        tc.create_empty_outlier_table(outlier_path)

        #save
        save_file = file_marker_tc + partial_filename + '.xlsx'
        save_path = os.path.join(save_folder_tc,save_file)
        tc.write_to_excel(time_dict,save_path)
