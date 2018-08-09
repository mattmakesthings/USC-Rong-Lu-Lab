#! /usr/bin/python2.7
'''
Directory structure::
    root folder
        Data
        Table
        <folder created by data_regroup.py>
        Scripts_<version_identifier>

Primary Variables - Will be modified most often
    data_file - raw data file to be operated on

Secondary Variables - Modify at user discretion,
                      mainly names of folders to be created

    sub_folder - refer to pipeline.py script for details
    load_folder - where files from data_regroup will be loaded from.
    save_folder - folder that will be created if it doesn't exist,
                  will store all files created by this script.
'''
################################################################################
# Primary Variables
data_file = 'IL10KO 1.0 4mo RAW.xls'
################################################################################
# Secondary Variables
sub_folder = ''
load_folder = 'Rearranged Data'
save_folder = 'Calculated for Prism'
################################################################################
import pandas as pd
import numpy as np
import os
import sys
from itertools import cycle

from version import get_version
from data_regroup import create_save_folder, create_path, load_data, prepend_folder
version = get_version()

import pandas.io.formats.excel
pandas.io.formats.excel.header_style = None

load_folder = prepend_folder(load_folder)
save_folder = prepend_folder(save_folder)

#column names from excel sheet
cell_type = ["Granulocytes","Monocytes","B cells","CD4T cells","CD8T cells"]
subtypes = [" (BLY)"," (F1)"," (B6)"]
def create_all_df(df_src):
    df_dest = df_src[['group','Alive']].copy()
    for i in cell_type:
        df_dest[i] = df_src[i]
        df_dest["% " + i] = (df_src[i] * 100.0)/ df_src["Alive"]
        df_dest["% " + i].fillna(0,inplace = True)
    return df_dest

def create_subtype_df(df_src):
    df_dest = df_src[['group','Alive']].copy()
    for i in cell_type:
        df_dest[i] = df_src[i]
        for j in subtypes:
            df_dest[i + j] =  df_src[i+j]
            df_dest["% " + i + j] =  (df_src[i+j] * 100.0) / df_dest[i]
            df_dest["% " + i + j].fillna(0,inplace = True)
    return df_dest

def create_gp_paste_df(all_df, subtype_df):
    df_dest = all_df[['group']].copy()
    for i in cell_type:
        df_dest[i] = all_df["% " + i]
        for j in subtypes:
            df_dest[i + j] = subtype_df["% " + i + j]
            df_dest[i + j].fillna(0, inplace = True)
    return df_dest

def create_chimerism_df(rearranged_df):
    df_dest = rearranged_df[['group','Alive']].copy()
    for i in cell_type:
        for j in subtypes:
            df_dest[i + j] = rearranged_df[i + j] / rearranged_df['Alive']
            df_dest[i + j].fillna(0, inplace = True)
    df_dest = df_dest.drop(['Alive'], axis = 1)
    return df_dest

def create_dfs(df):
    df = df[df.group != 'ungrouped']
    all_df = create_all_df(df)
    subtype_df = create_subtype_df(df)
    gp_paste_df = create_gp_paste_df(all_df,subtype_df)
    subtype_all_df = create_chimerism_df(df)
    return all_df , subtype_df ,gp_paste_df, subtype_all_df

def save_to_excel(path,all_df,rearranged_df,subtype_df,gp_paste_df,subtype_all_df):
    #save data to excel file
    writer = pd.ExcelWriter(path, engine='xlsxwriter')

    all_df.to_excel(writer,sheet_name='All')
    rearranged_df.to_excel(writer,sheet_name='RAW')
    subtype_df.to_excel(writer,sheet_name='GraphPad')
    gp_paste_df.to_excel(writer,sheet_name='GraphPad Paste')
    subtype_all_df.to_excel(writer,sheet_name= 'chimerism vs. all')

    #cell_format excel sheets
    workbook = writer.book
    worksheet_all = writer.sheets['All']
    worksheet_subtype = writer.sheets['GraphPad']
    worksheet_gp_paste = writer.sheets['GraphPad Paste']
    worksheet_subtype_all = writer.sheets['chimerism vs. all']

    worksheet_list = [worksheet_all,
                      worksheet_subtype,
                      worksheet_gp_paste,
                      worksheet_subtype_all]

    cell_format = workbook.add_format({'align':'right',
                                       'font':'Arial',
                                       'font_size' : 10})

    label_width = 40
    label = 'A:A'
    for worksheet in worksheet_list:
        worksheet.set_column(label, label_width, cell_format)

    column_width = 14
    columns = 'B:BB'
    for worksheet in worksheet_list:
        worksheet.set_column(columns, column_width, cell_format)

    curr_group = gp_paste_df.iloc[0]['group']
    colors = ['#AED6F1','#A3E4D7','#F9E79F','#D7BDE2','#B1F5CA']
    color_cycle = cycle(colors)
    curr_color = next(color_cycle)

    ungrouped_format = workbook.add_format({'align':'right',
                                            'font':'Arial',
                                            'font_size' : 10,
                                            'font_color' : 'white',
                                            'fg_color' : '#FA1900'})
    format_list = []
    for i in colors:
        format_list.append(workbook.add_format({'align':'right',
                                            'font':'Arial',
                                            'font_size' : 10,
                                            # 'pattern' : 2,
                                            'fg_color' : curr_color}))
        curr_color = next(color_cycle)

    for worksheet in worksheet_list:
        format_cycle = cycle(format_list)
        curr_format = next(format_cycle)

        for row in range(len(gp_paste_df.index)):
            if curr_group == gp_paste_df.iloc[row]['group']:
                worksheet.set_row(row+1,':',cell_format=curr_format)
            else:
                curr_group = gp_paste_df.iloc[row]['group']
                if curr_group == 'ungrouped':
                    curr_format = ungrouped_format
                else:
                    curr_format = next(format_cycle)

                worksheet.set_row(row+1,':',cell_format=curr_format)





    writer.save()

if __name__ == "__main__":
    load_path = [load_folder,sub_folder]
    load_path = os.path.join(*load_path)
    load_path = create_path(load_path,data_file,' Rearranged ')
    rearranged_df = load_data(load_path)
    all_df , subtype_df , gp_paste_df, subtype_all_df = create_dfs(rearranged_df)

    save_folder = os.path.join(save_folder,sub_folder)
    create_save_folder(save_folder)
    path = create_path(save_folder,data_file,' GraphPad ')
    save_to_excel(path,all_df,rearranged_df,subtype_df,gp_paste_df,subtype_all_df)
