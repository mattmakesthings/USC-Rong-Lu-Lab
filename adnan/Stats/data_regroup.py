#! /usr/bin/python2.7

#script to group specimen data given a table file
import pandas as pd
import numpy as np
import os
import sys

import pandas.io.formats.excel
pandas.io.formats.excel.header_style = None

# test file 'CLP 2.0 2mo RAW.xls'
filename = sys.argv[1]

table_file = 'HSC-CLP 2.0 Table.xlsx'
table_folder = 'Table/'
#load_folder = 'RAW Data/'
if not os.path.exists('Rearranged Data/'):
    os.makedirs('Rearranged Data/')
save_folder = 'Rearranged Data/'

#match raw_data row to table column
def sort_df(df_affect,df_table):
    #iterates through table excel sheet
    for i in df_table:
        for j in df_table[i]:
            s = "Specimen_M" + str(j)
            df_affect.loc[df_affect.index.to_series().str.contains(s), "group"] = str(i)
    return df_affect
if __name__ == "__main__":
    #load data into pandas dataframe


    df_RAW = pd.read_excel(load_folder + filename)
    df_RAW.index = df_RAW.index.map(str)

    #add grouping column
    df_RAW.insert(loc=0, column="group",value="ungrouped")

    #read in table data

    df_table = pd.read_excel(table_folder + table_file)
    df_table.columns = df_table.columns.map(str)

    #sort the RAW data by group
    df_RAW = sort_df(df_RAW,df_table)
    df_RAW.sort_values(by=['group'],ascending = False,inplace=True)

    # Drop the stats rows in the data
    df_RAW = df_RAW.drop(['Mean','SD'])

    #save data to excel file

    writer = pd.ExcelWriter(save_folder + 'Rearranged '+ filename,engine = 'xlsxwriter')
    df_RAW.to_excel(writer,sheet_name='Sheet1')

    #formatting excel file
    workbook = writer.book
    worksheet_RAW = writer.sheets['Sheet1']

    cell_format = workbook.add_format({'align':'right',

                                       'font':'Arial',
                                       'font_size' : 10})



    label_width = 40
    label = 'A:A'
    worksheet_RAW.set_column(label, label_width, cell_format)

    column_width = 18
    columns = 'B:BB'
    worksheet_RAW.set_column(columns, column_width, cell_format)

    writer.save()
