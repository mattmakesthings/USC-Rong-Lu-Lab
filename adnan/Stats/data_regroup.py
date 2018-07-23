#! /usr/bin/python2.7

#script to group specimen data given a table file
import pandas as pd
import numpy as np
import os
import sys
import re

import pandas.io.formats.excel
pandas.io.formats.excel.header_style = None

name_error_str = " not previously defined, continuing with harcoded value"

if len(sys.argv) > 1:
    filename = sys.argv[1]
else:
    try:
        filename
    except NameError:
        print "filename" +  name_error_str
        filename = 'IL10KO 1.0 2mo RAW.xls'


if len(sys.argv) > 2:
    table_file = sys.argv[2]
else:
    try:
        table_file
    except NameError:
        print "table_file" +  name_error_str
        table_file = 'IL10KO 1.0 Table 01.xlsx'

try:
    table_folder
except NameError:
    print "table_folder" +  name_error_str
    table_folder = 'Table/'

load_folder = 'RAW Data/'
if not os.path.exists('Rearranged Data/'):
    os.makedirs('Rearranged Data/')
save_folder = 'Rearranged Data/'

#match raw_data row to table column
def group_df(df_affect,df_table):
    #iterates through table excel sheet
    for i in df_table:
        for j in df_table[i]:
            s = "M" + str(j)
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

    # Drop the stats rows in the data
    df_RAW = df_RAW.drop(['Mean','SD'])


    #group the RAW data
    df_RAW = group_df(df_RAW,df_table)

    #sort by order of table columns
    order = list(df_table.columns)
    order.append('ungrouped')

    col = dict(zip(order,range(len(order))))
    df_RAW['col_from_table'] = df_RAW['group'].map(col)

    #create col to sort within groups
    temp = []
    for i in list(df_RAW.index):
        m = re.search(r"[_\s][0-9]+.fcs",i)
        temp.append(m.group())


    df_RAW['col_from_ind'] = temp
    df_RAW.sort_values(by=['col_from_table','col_from_ind'],ascending = [True,True],inplace=True)

    #drop temp columns
    df_RAW.drop('col_from_table', 1,inplace = True)
    df_RAW.drop('col_from_ind',1,inplace = True)
    #print df_RAW.head(4)


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
