#! /usr/bin/python2.7

#script to group specimen data
import pandas as pd
import numpy as np
import os
import sys

from data_regroup import create_save_folder, create_path, prepend_folder

import pandas.io.formats.excel
pandas.io.formats.excel.header_style = None

data_file = 'CLP 2.0 2mo RAW.xls'

table_file  = 'HSC-CLP 2.0 Table.xlsx'
table_folder = 'Table/'

load_folder = 'Calculated for Prism/'
save_folder = 'Transposed Calculated for Prism/'

load_folder = prepend_folder(load_folder)
save_folder = prepend_folder(save_folder)
table_folder = prepend_folder(table_folder)

load_path = create_path(load_folder,data_file,' GraphPad ')
save_path = create_path(save_folder,data_file,' GraphPad Transposed ')

chimerism = 10

#column names from excel sheet
subtypes = [" (BLY)"," (F1)"," (B6)"]

def col_to_dict(df):
    d = {}
    for col in df:
        d[col] = 0
    return d

def transform(src_df,sheet_name):
    #sort rows by group
    #src_df.sort_values(by=['group'],ascending = False,inplace=True)
    dest_df = src_df[['group']].copy()

    #separate cell group into own dataframe
    for i in src_df.columns:
        if sheet_name in i:
            dest_df[i] = src_df[i]


    #check subgroups length
    cp_df = pd.DataFrame(columns=dest_df.columns)
    empty_row = pd.Series(name='')

    #create dict to count occurences of subgroups
    df_table = pd.read_excel(table_folder + table_file)
    subgroups = col_to_dict(df_table)
    subgroups['ungrouped'] = 0

    #count difference between size limit and actual size
    for row in dest_df.itertuples():
        subgroups[row.group]+=1

    #copy over rows and insert blanks
    for k,v in subgroups.items():
        cp_df = cp_df.append(dest_df[dest_df['group']==k],ignore_index = True)

        if chimerism - v < 0:
            if k == 'ungrouped':
                print ("Warning: ungrouped has more values than chimerism ")
            else:
                print ("ERROR - chimerism overflow: " + k + " has too many values")
                quit()

        #add empty rows for the gap between limit and chimerisms
        for i in range(chimerism - subgroups[k]):
            cp_df = cp_df.append(empty_row)

    #transform dataframe
    return cp_df.T

def load_excel(path):
    xls_file = pd.ExcelFile(path)
    return xls_file.parse('GraphPad Paste')

def get_cell_type():
    cell_type = ["Granulocytes","Monocytes","B cells","CD4T cells","CD8T cells"]
    return cell_type

def create_cell_sheets(gp_paste_df,path):
    writer = pd.ExcelWriter(path, engine='xlsxwriter')

    cell_type = get_cell_type()
    for name in cell_type:
        gran_df = transform(gp_paste_df,name)
        gran_df.to_excel(writer,sheet_name=name)
    return writer

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
    #load data into pandas dataframe
    gp_paste_df = load_excel(load_path)
    writer = create_cell_sheets(gp_paste_df,save_path)
    create_save_folder(save_folder)
    save_to_excel(writer)
