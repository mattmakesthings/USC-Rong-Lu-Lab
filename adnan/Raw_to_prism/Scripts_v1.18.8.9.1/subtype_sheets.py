#! /usr/bin/python2.7
'''
Directory structure::
    root folder
        Data
        Table
        <folder created by data_regroup.py>
        <folder created by append_percent.py>
        Scripts_<version_identifier>

Primary Variables - Will be modified most often
    specimen_limit - this is the size limit of each group from the table file.
                     if set to 0, specimen_limit will be determined from table_file
    data_file - raw data file to be operated on
    table_file - Groups specimens according to column within table
    table_folder - contains table_file
Secondary Variables - Modify at user discretion,
                      mainly names of folders to be created

    sub_folder - refer to pipeline.py script for details
    load_folder - where files from append_percent.py will be loaded from.
    save_folder - folder that will be created if it doesn't exist,
                  will store all files created by this script.
'''
################################################################################
# Primary Variables
specimen_limit = 0
data_path = '/home/matt/Documents/USC-Rong-Lu-Lab/adnan/Raw_to_prism/Calculated for Prism/v1.18.8.9.1 Rearranged CLP 2.0 12d RAW.xls'
table_path = '/home/matt/Documents/USC-Rong-Lu-Lab/adnan/Raw_to_prism/Table/HSC-CLP 2.0 Table.xlsx'
################################################################################
# Secondary Variables
sub_folder = ''
save_folder = 'Transposed Calculated for Prism'
################################################################################
import pandas as pd
import numpy as np
import os
import sys

from collections import OrderedDict
from data_regroup import create_save_folder, create_path, prepend_folder,load_table

import pandas.io.formats.excel
pandas.io.formats.excel.header_style = None

load_folder, data_file = os.path.split(data_path)
table_folder, table_file = os.path.split(table_path)

def col_to_dict(df):
    d = OrderedDict()
    for col in df:
        d[col] = 0
    return d

def get_cell_type():
    cell_type = ["Granulocytes","Monocytes","B cells","CD4T cells","CD8T cells"]
    return cell_type

def transform(src_df,sheet_name,df_table):
    #sort rows by group
    dest_df = src_df[['group']].copy()

    #separate cell group into own dataframe
    for i in src_df.columns:
        if sheet_name in i:
            dest_df[i] = src_df[i]


    #check subgroups length
    cp_df = pd.DataFrame(columns=dest_df.columns)
    empty_row = pd.Series(name='')

    #create dict to count occurences of subgroups
    subgroups = col_to_dict(df_table)
    subgroups['ungrouped'] = 0

    #count difference between size limit and actual size
    for row in dest_df.itertuples():
        subgroups[row.group]+=1

    #copy over rows and insert blanks
    for k,v in subgroups.items():
        cp_df = cp_df.append(dest_df[dest_df['group']==k],ignore_index = False)

        if specimen_limit - v < 0:
            if k == 'ungrouped':
                print ("Warning: ungrouped has more values than specimen_limit ")
            else:
                print ("ERROR - specimen_limit overflow: " + k + " has too many values")
                quit()

        #add empty rows for the gap between limit and specimen_limits
        for i in range(specimen_limit - v):
            cp_df = cp_df.append(empty_row)

    #transform dataframe
    return cp_df.T

def load_excel(path,sheet):
    xls_file = pd.ExcelFile(path)
    return xls_file.parse(sheet)

def subgroups_from_table(df_table):
    subgroups = col_to_dict(df_table)
    subgroups['ungrouped'] = 0
    return subgroups

def create_cell_sheets(gp_paste_df,df_table,path):
    writer = pd.ExcelWriter(path, engine='xlsxwriter')
    subgroups = subgroups_from_table(df_table)

    cell_type = get_cell_type()
    for name in cell_type:
        gran_df = transform(gp_paste_df,name,df_table)
        gran_df.to_excel(writer,sheet_name=name)
    return writer

def get_specimen_limit(df_table,specimen_limit):
    table_length = len(df_table.index)
    if specimen_limit == 0:
        specimen_limit = table_length
    else:
        if table_length > specimen_limit:
            print "specimen limit is shorter than longest group. Continuing"
    return specimen_limit

def save_to_excel(writer):
    #cell_format excel sheets
    workbook = writer.book
    cell_format = workbook.add_format({'align':'right',
                                       'font':'Arial',
                                       'font_size' : 10})

    cell_type = get_cell_type()
    for name in cell_type:
        worksheet_gp_paste = writer.sheets[name]

        label_width = 40
        label = 'A:A'
        worksheet_gp_paste.set_column(label, label_width, cell_format)

        column_width = 14
        columns = 'B:BB'
        worksheet_gp_paste.set_column(columns, column_width, cell_format)

    writer.save()


if __name__ == "__main__":
    load_folder = prepend_folder(load_folder)
    save_folder = prepend_folder(save_folder)
    table_folder = prepend_folder(table_folder)

    save_folder = os.path.join(save_folder,sub_folder)

    load_path = create_path(load_folder,data_file,' GraphPad ')
    save_path = create_path(save_folder,data_file,' GraphPad Transposed ')


    df_res = load_excel(load_path,'GraphPad Paste')
    df_table = load_table(table_path)
    specimen_limit = get_specimen_limit(df_table,specimen_limit)
    writer = create_cell_sheets(df_res,df_table,save_path)
    create_save_folder(save_folder)
    save_to_excel(writer)
