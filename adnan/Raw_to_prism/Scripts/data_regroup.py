#! /usr/bin/python2.7

#script to group specimen data given a table file
import pandas as pd
import numpy as np
import os
import sys
import re

import pandas.io.formats.excel
pandas.io.formats.excel.header_style = None

data_file = 'CLP 2.0 2mo RAW.xls'
data_folder = 'RAW Data/'
table_file = 'HSC-CLP 2.0 Table.xlsx'
table_folder = 'Table/'

save_folder = 'Rearranged Data/'

#parent_dir = os.path.dirname(os.getcwd())

def prepend_folder(s):
    parent_dir = os.path.dirname(os.getcwd())
    return parent_dir + "/" + s

data_folder = prepend_folder(data_folder)
table_folder = prepend_folder(table_folder)
save_folder = prepend_folder(save_folder)

def load_data(path):
    return pd.read_excel(path)

def load_table(path):
    return pd.read_excel(table_folder + table_file)

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
def add_specimen_mapping(df):
    temp = []
    for i in list(df.index):
        m = re.search(r"[_\s][0-9]+.fcs",i)
        temp.append(m.group())
    df['col_from_ind'] = temp
    return df

def sort_by_group_specimen(df_RAW):
    return df_RAW.sort_values(by=['col_from_table','col_from_ind'],ascending = [True,True],inplace=False)

def drop_temp_columns(df_RAW):
    df_RAW.drop('col_from_table', 1,inplace = True)
    df_RAW.drop('col_from_ind',1,inplace = True)
    return df_RAW

def drop_stats_rows(df):
    df = df.drop(['Mean','SD'],inplace=False)
    return df

def create_sort_list(df_table):
    order = list(df_table.columns)
    order.append('ungrouped')
    return order

def string_match(df,str):
    return df.index.to_series().str.contains(str)

#match raw_data row to table column
def group_df(df_affect,df_table):
    #iterates through table excel sheet
    for i in df_table:
        for j in df_table[i]:
            s = "M" + str(j)
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

    writer.save()

def get_grouped_data(df_RAW,df_table):
    df_RAW = drop_stats_rows(df_RAW)
    df_RAW = group_df(df_RAW,df_table)
    order = create_sort_list(df_table)
    df_RAW = add_group_mapping(df_RAW,order)
    df_RAW = add_specimen_mapping(df_RAW)
    df_RAW = sort_by_group_specimen(df_RAW)
    df_RAW = drop_temp_columns(df_RAW)
    return df_RAW

#adds version and identifier to file name
def create_path(folder,data_file,identifier):
    from version import get_version
    version = get_version()

    if version not in data_file:
        data_file = version + identifier + data_file
    return folder + data_file

if __name__ == "__main__":
    # load data into pandas dataframe
    df_RAW = load_data(data_folder + data_file)
    # load table data into dataframe
    df_table = load_table(table_folder + table_file)

    # group data
    df_RAW = get_grouped_data(df_RAW,df_table)

    #save data to excel file

    create_save_folder(save_folder)
    path = create_path(save_folder,data_file,' Rearranged ')
    save_to_excel(path,df_RAW)
