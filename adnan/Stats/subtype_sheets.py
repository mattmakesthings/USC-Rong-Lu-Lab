#! /usr/bin/python2.7

#script to group specimen data
import pandas as pd
import numpy as np
import os

import pandas.io.formats.excel
pandas.io.formats.excel.header_style = None

filename = 'CLP 2.0 2mo RAW.xls'
load_folder = 'Calculated for Prism/'

if not os.path.exists('Transposed Calculated for Prism/'):
    os.makedirs('Transposed Calculated for Prism/')

save_folder = 'Transposed Calculated for Prism/'


subgroup_size = 6

#column names from excel sheet
col_names = ["Granulocytes","Monocytes","B cells","CD4T cells","CD8T cells"]
subtypes = [" (BLY)"," (F1)"," (B6)"]
def transform(src_df,sheet_name):
    #sort rows by group
    src_df.sort_values(by=['group'],ascending = False,inplace=True)
    dest_df = src_df[['group']].copy()

    #separate cell group into own dataframe
    for i in src_df.columns:
        if sheet_name in i:
            dest_df[i] = src_df[i]


    #check subgroups length
    cp_df = pd.DataFrame(columns=dest_df.columns)
    empty_row = pd.Series(name='')

    subgroups = {'WT HSC':0, 'WT CLP':0, 'KO HSC':0, 'KO CLP':0}
    #count difference between size limit and actual size
    for row in dest_df.itertuples():
        subgroups[row.group]+=1

    #copy over rows and insert blanks
    for k,v in subgroups.items():
        cp_df = cp_df.append(dest_df[dest_df['group']==k],ignore_index = True)

        if subgroup_size - subgroups[k] < 0:
            print ("ERROR - subgroup overflow: " + k + " has too many values")
            quit()

        for i in range(subgroup_size - subgroups[k]):
            cp_df = cp_df.append(empty_row)

    #transform dataframe
    return cp_df.T


if __name__ == "__main__":
    #load data into pandas dataframe
    xls_file = pd.ExcelFile(load_folder + 'Graph Pad '+ filename)
    gp_paste_df = xls_file.parse('GraphPad Paste')

    writer = pd.ExcelWriter(save_folder + 'Graph Pad Transposed '+ filename, engine='xlsxwriter')

    for name in col_names:
        gran_df = transform(gp_paste_df,name)
        gran_df.to_excel(writer,sheet_name=name)

    #cell_format excel sheets
    workbook = writer.book
    cell_format = workbook.add_format({'align':'right',
                                       'font':'Arial',
                                       'font_size' : 10})
    for name in col_names:
        worksheet_gp_paste = writer.sheets[name]

        label_width = 40
        label = 'A:A'
        worksheet_gp_paste.set_column(label, label_width, cell_format)

        column_width = 14
        columns = 'B:BB'
        worksheet_gp_paste.set_column(columns, column_width, cell_format)
    writer.save()
