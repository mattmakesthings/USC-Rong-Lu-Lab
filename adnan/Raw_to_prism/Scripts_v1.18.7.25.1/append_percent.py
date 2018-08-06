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
sub_folder = 'IL10KO'
load_folder = 'Rearranged Data'
save_folder = 'Calculated for Prism'

#script to group specimen data
import pandas as pd
import numpy as np
import os
import sys

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
    return df_dest

def create_subtype_df(df_src):
    df_dest = df_src[['group','Alive']].copy()
    for i in cell_type:
        df_dest[i] = df_src[i]
        for j in subtypes:
            df_dest[i + j] =  df_src[i+j]
            df_dest["% " + i + j] =  (df_src[i+j] * 100.0) / df_dest[i]
    return df_dest

def create_gp_paste_df(all_df, subtype_df):
    df_dest = all_df[['group']].copy()
    for i in cell_type:
        df_dest[i] = all_df["% " + i]
        for j in subtypes:
            df_dest[i+j] = subtype_df["% " + i + j]
    return df_dest

def create_dfs(df):
    df = df[df.group != 'ungrouped']
    all_df = create_all_df(df)
    st_df = create_subtype_df(df)
    return all_df , st_df ,create_gp_paste_df(all_df,st_df)

def save_to_excel(path,all_df,rearranged_df,subtype_df,gp_paste_df):
    #save data to excel file
    writer = pd.ExcelWriter(path, engine='xlsxwriter')

    all_df.to_excel(writer,sheet_name='All')
    rearranged_df.to_excel(writer,sheet_name='RAW')
    subtype_df.to_excel(writer,sheet_name='GraphPad')
    gp_paste_df.to_excel(writer,sheet_name='GraphPad Paste')

    #cell_format excel sheets
    workbook = writer.book
    worksheet_all = writer.sheets['All']
    worksheet_subtype = writer.sheets['GraphPad']
    worksheet_gp_paste = writer.sheets['GraphPad Paste']

    cell_format = workbook.add_format({'align':'right',
                                       'font':'Arial',
                                       'font_size' : 10})

    label_width = 40
    label = 'A:A'
    worksheet_all.set_column(label, label_width, cell_format)
    worksheet_subtype.set_column(label, label_width, cell_format)
    worksheet_gp_paste.set_column(label, label_width, cell_format)

    column_width = 14
    columns = 'B:BB'
    worksheet_all.set_column(columns, column_width, cell_format)
    worksheet_subtype.set_column(columns, column_width, cell_format)
    worksheet_gp_paste.set_column(columns, column_width, cell_format)
    writer.save()

if __name__ == "__main__":
    load_path = [load_folder,sub_folder]
    load_path = os.path.join(*load_path)
    load_path = create_path(load_path,data_file,' Rearranged ')
    rearranged_df = load_data(load_path)
    all_df , subtype_df , gp_paste_df = create_dfs(rearranged_df)

    save_folder = os.path.join(save_folder,sub_folder)
    create_save_folder(save_folder)
    path = create_path(save_folder,data_file,' GraphPad ')
    save_to_excel(path,all_df,rearranged_df,subtype_df,gp_paste_df)
