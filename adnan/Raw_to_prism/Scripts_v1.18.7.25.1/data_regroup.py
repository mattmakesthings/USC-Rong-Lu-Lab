#! /usr/bin/python2.7
'''
Directory structure::
    root folder
        Data
        Table
        Scripts_<version_identifier>

Primary Variables - Will be modified most often
    data_file - raw data file to be operated on
    data_folder - contains the file(s) of raw data to be operated on
    table_file - Groups specimens according to column within table
    table_folder - contains table_file

Secondary Variables - Modify at user discretion,
                      mainly names of folders to be created
    sub_folder - refer to pipeline.py script for details
    save_folder - folder that will be created if it doesn't exist,
                  will store all files created by this script.
'''
################################################################################
# Primary Variables
data_file = 'IL10KO 1.0 2mo RAW.xls'
data_folder = 'Data'
table_file = 'IL10KO 1.0 Table 01.xlsx'
table_folder = 'Table'
################################################################################
# Secondary Variables
sub_folder = ''
save_folder = 'Rearranged Data'

#script to group specimen data given a table file
import pandas as pd
import numpy as np
import math
import os
import sys
import re
from itertools import cycle

import pandas.io.formats.excel
pandas.io.formats.excel.header_style = None


#prepends folder parent directory to folder name
def prepend_folder(s):
    parent_dir = os.path.dirname(os.getcwd())
    return os.path.join(parent_dir,s)

data_folder = prepend_folder(data_folder)
table_folder = prepend_folder(table_folder)
save_folder = prepend_folder(save_folder)

def load_data(path,sheet_name = 0):
    return pd.read_excel(path,sheet_name)

def load_table(path):
    df_table = load_data(path)
    df_table = df_table.apply(pd.to_numeric)
    return df_table

def add_group_col(df):
    df.insert(loc=0, column="group",value="ungrouped")
    return df

def create_save_folder(folder_name):
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

def add_group_mapping(df,order):
    col = dict(zip(order,range(len(order))))
    df['col_from_table'] = df['group'].map(col)
    return df

#extract specimen # from index and adds as row
def get_regex():
    return r"[Mm][0-9]+"

def add_specimen_mapping(df):
    temp = []
    for i in list(df.index):
        m = re.search(get_regex(),i)
        temp.append(m.group())
    df['col_from_ind'] = temp
    return df

def sort_by_group_specimen(df_RAW):
    return df_RAW.sort_values(by=['col_from_table','col_from_ind'],ascending = [True,True],inplace=False)

def drop_temp_columns(df_RAW):
    df_RAW.drop('col_from_table', 1,inplace = True)
    df_RAW.drop('col_from_ind',1,inplace = True)
    return df_RAW

def drop_nonspecimen_rows(df):
    reg = re.compile(get_regex())
    for i in list(df.index):
        if not reg.search(i):
            print "Specimen name not found, dropping : " + i
            df = df.drop(i)
    return df

def create_sort_list(df_table):
    order = list(df_table.columns)
    order.append('ungrouped')
    return order

def string_match(df,s):
    return df.index.to_series().str.contains(s)

#match raw_data row to table column
def group_df(df_affect,df_table):
    #iterates through table excel sheet
    for i in df_table:
        for j in df_table[i]:
            if not math.isnan(j):
                j = str(np.int64(j))
                s = "M" + j
                result = string_match(df_affect,s)
                #throw errors if duplicate table entries
                #are detected in data
                if sum(result) > 1:
                    print '\n'.join([k for k,v in result.iteritems() if v == True ])
                    print ("Error: duplicate entries of " + str(i) + " " + str(j) + " detected")
                    # quit()
                else:
                    df_affect.loc[string_match(df_affect,s), "group"] = str(i)
    return df_affect

def save_to_excel(path,df_RAW):
    writer = pd.ExcelWriter(path,engine = 'xlsxwriter')
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

    #insert blanks
    curr_group = df_RAW.iloc[0]['group']
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

    format_cycle = cycle(format_list)
    curr_format = next(format_cycle)

    for row in range(len(df_RAW.index)):
        if curr_group == df_RAW.iloc[row]['group']:
            worksheet_RAW.set_row(row+1,':',cell_format=curr_format)
        else:
            curr_group = df_RAW.iloc[row]['group']
            if curr_group == 'ungrouped':
                curr_format = ungrouped_format
            else:
                curr_format = next(format_cycle)
            worksheet_RAW.set_row(row+1,':',cell_format=curr_format)
    worksheet_RAW.hide_gridlines(0)
    writer.save()

def get_grouped_data(df_RAW,df_table):
    df_RAW = drop_nonspecimen_rows(df_RAW)
    df_RAW = add_group_col(df_RAW)
    df_RAW = group_df(df_RAW,df_table)
    order = create_sort_list(df_table)
    df_RAW = add_group_mapping(df_RAW,order)
    df_RAW = add_specimen_mapping(df_RAW)
    df_RAW = sort_by_group_specimen(df_RAW)
    df_RAW = drop_temp_columns(df_RAW)
    return df_RAW

#adds version and identifier to file name
def create_path(folder,data_file,identifier = ''):
    from version import get_version
    version = get_version()

    if version not in data_file and version:
        data_file = version + identifier + data_file
    return os.path.join(folder,data_file)

if __name__ == "__main__":
    # load data into pandas dataframe
    print data_file
    data_path = [data_folder,sub_folder,data_file]
    data_path = os.path.join(*data_path)
    df_RAW = load_data(data_path)

    # load table data into dataframe
    path = os.path.join(table_folder,table_file)
    df_table = load_table(path)
    df_table = df_table.apply(pd.to_numeric)
    # group data
    df_RAW = get_grouped_data(df_RAW,df_table)

    #save data to excel file
    create_save_folder(save_folder)
    path = create_path(save_folder,data_file,' Rearranged ')
    save_to_excel(path,df_RAW)
