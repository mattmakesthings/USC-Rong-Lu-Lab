#! /usr/bin/python2.7

#script to group specimen data
import pandas as pd
import numpy as np
import os
import sys

import pandas.io.formats.excel
pandas.io.formats.excel.header_style = None

filename_ = 'IL10KO 1.0 2mo RAW.xls'
table_file_ = 'IL10KO 1.0 Table 01.xlsx'
table_folder_ = 'Table/'

load_folder = 'Calculated for Prism/'
save_folder = 'Transposed Calculated for Prism/'

chimerism_ = 10

#should only be seen if running script individually, without the pipeline.py script
name_error_str = " not previously defined, continuing with harcoded value"

if len(sys.argv) > 1:
    filename = sys.argv[1]
else:
    try:
        filename
    except NameError:
        print "filename" +  name_error_str
        filename = filename_

if len(sys.argv) > 2:
    table_file = sys.argv[2]
else:
    try:
        table_file
    except NameError:
        print "table_file" + name_error_str
        table_file = table_file_

try:
    table_folder
except NameError:
    print "table_folder" + name_error_str
    table_folder = table_folder_

try:
    chimerism
except NameError:
    print "chimerism" + name_error_str
    chimerism = chimerism_


if not os.path.exists('Transposed Calculated for Prism/'):
    os.makedirs('Transposed Calculated for Prism/')

#column names from excel sheet
cell_type = ["Granulocytes","Monocytes","B cells","CD4T cells","CD8T cells"]
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

        for i in range(chimerism - subgroups[k]):
            cp_df = cp_df.append(empty_row)

    #transform dataframe
    return cp_df.T


if __name__ == "__main__":
    #load data into pandas dataframe
    xls_file = pd.ExcelFile(load_folder + 'Graph Pad '+ filename)
    gp_paste_df = xls_file.parse('GraphPad Paste')

    writer = pd.ExcelWriter(save_folder + 'Graph Pad Transposed '+ filename, engine='xlsxwriter')

    for name in cell_type:
        gran_df = transform(gp_paste_df,name)
        gran_df.to_excel(writer,sheet_name=name)

    #cell_format excel sheets
    workbook = writer.book
    cell_format = workbook.add_format({'align':'right',
                                       'font':'Arial',
                                       'font_size' : 10})
    for name in cell_type:
        worksheet_gp_paste = writer.sheets[name]

        label_width = 40
        label = 'A:A'
        worksheet_gp_paste.set_column(label, label_width, cell_format)

        column_width = 14
        columns = 'B:BB'
        worksheet_gp_paste.set_column(columns, column_width, cell_format)
    writer.save()
