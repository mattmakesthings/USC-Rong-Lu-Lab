#! /usr/bin/python2.7

#script to group specimen data
import pandas as pd
import numpy as np
import os
import sys

import pandas.io.formats.excel
pandas.io.formats.excel.header_style = None

#should only be seen if running script individually, without the pipeline.py script
name_error_str = " not previously defined, continuing with harcoded value"

if len(sys.argv) > 1:
    filename = sys.argv[1]
else:
    try:
        filename
    except NameError:
        print "filename" +  name_error_str
        filename = 'IL10KO 1.0 2mo RAW.xls'

load_folder = 'Rearranged Data/'
if not os.path.exists('Calculated for Prism/'):
    os.makedirs('Calculated for Prism/')
save_folder = 'Calculated for Prism/'

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

if __name__ == "__main__":
    #load data into pandas dataframe

    rearranged_df = pd.read_excel(load_folder + 'Rearranged '+ filename)

    #create dataframe for 'all' sheet calculations
    all_df = create_all_df(rearranged_df)


    #similarly for subtype calculations
    subtype_df = create_subtype_df(rearranged_df)

    #graphpad_paste sheet
    gp_paste_df = create_gp_paste_df(all_df,subtype_df)

    #save data to excel file

    writer = pd.ExcelWriter(save_folder + 'Graph Pad '+ filename, engine='xlsxwriter')

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

