#!/usr/bin/python2.7

# this script combines multiple files to compare
# specimens over time
# IMPORTANT:
#      1 relies on results of either the pipeline script or the subtype_sheets script
#      2 set the specimen_limit var to be equal to the value of the script used above


'''
Primary Variables - Will be modified most often
    specimen_limit - this is the size limit of each group from the table file,
                make larger if an error is thrown.
    time unit -> time unit used in input file names

    load_folder -> this is the folder in which the load folder is contained

    table_path -> used when creating the initial data

Secondary Variables - Modify at user discretion,
                      mainly names of folders to be created

    sub_folder -> refer to pipeline.py

    save_file -> the name of the resulting file once the script has finished

    save_folder -> this will contain the save_file and wil be created if it
    does not already exist

    outlier_file -> created with this script. Used to filter out
                    data for graphing.
'''
##################################################################
# Primary Variables
specimen_limit = 0
time_unit = "d"
load_folder = '/home/matt/Documents/USC-Rong-Lu-Lab/adnan/Raw_to_prism/Transposed Calculated for Prism'
table_path = '/home/matt/Documents/USC-Rong-Lu-Lab/adnan/Raw_to_prism/Table/HSC-CLP 2.0 Table.xlsx'
##################################################################
# Secondary Variables
sub_folder = ''
save_file = 'Time Course.xlsx'
save_folder = 'Time course for Prism'
outlier_file = 'Outliers and Warnings.xlsx'
##################################################################
import pandas as pd
import os
import re
from data_regroup import load_data,load_table, prepend_folder, create_path, create_save_folder, get_regex
from subtype_sheets import get_specimen_limit
from collections import OrderedDict
import operator
import xlsxwriter

table_folder, table_file = os.path.split(table_path)

#load_folder = prepend_folder(load_folder)
save_folder = prepend_folder(save_folder)
#oad_folder = os.path.join(load_folder,sub_folder)

def get_files(folder_):
    file_list = os.listdir(folder_)
    def atoi(text):
        return int(text) if text.isdigit() else text

    def natural_keys(text):
        return [ atoi(c) for c in re.split('(\d+)', text) ]
    file_list.sort(key=natural_keys)

    return file_list

def files_to_dict(files):
    return OrderedDict(zip(files,[0]*len(files)))

def ordered_dict_from_lists(l1,l2):
    return OrderedDict(zip(l1,l2))

def remove_non_excel(files):
    ret = []
    for f in files:
        if f.endswith('.xls') or f.endswith('.xlsx'):
            ret.append(f)
    return ret

def insert_time(file_dict,time_unit_loc):
    for k,v in file_dict.items():
        m = re.search(r"[0-9]+" + re.escape(time_unit_loc), k)
        if m == None:
            raise AttributeError('var time_unit doesn\'t match files')

        s = m.group(0).replace(time_unit_loc,'')
        file_dict[k] = int(s)
    return file_dict

def get_df_dict(load_folder,data_file):
    load_path = create_path(load_folder,data_file, '')
    df = load_data(load_path,sheet_name = None)
    return df

def get_sheet_names(file_dict,df):
    sheet_list = []
    sheet_names = list(df)
    for data_file, ind in file_dict.items():
        #iterate through sheets in file
        for sheet in sheet_names:
            for name in df[sheet].index:
                if name != 'group':
                    sheet_list.append(name)
        break
    return sheet_list

def get_specimen_names(df_table):
    ret = []
    for col in df_table:
        ret = ret + list(df_table[col].dropna().astype(int).astype(str).values)

    for i in range(len(ret)):
        ret[i] = "M" + str(ret[i])
    return ret

def list_of_df(length,col,ind):
    df_list = []
    for i in range(length):
        df_list.append(pd.DataFrame(columns=col,index =ind))
    return df_list

def sort_time(file_dict,time_unit):
    sorted_dict = OrderedDict(sorted(file_dict.items(), key=operator.itemgetter(1)))
    for key, value in sorted_dict.items():
        sorted_dict[key] = str(value) + time_unit
    return sorted_dict

def grp(pat,txt):
    r = re.search(pat,txt)
    return r.group(0) if r else '&'


def sort_files(file_list,time_unit):
    file_list.sort(key= lambda l: grp("[0-9]" + time_unit,l))
    #file_list.sort(key= lambda l: grp("[0-9].[0-9]" ,l))
    return file_list

def fill_time_dict(file_dict,load_folder,time_dict,df_col_r):
    # iterate through files to create dataframe
    for data_file, ind in file_dict.items():
        #print 'operations on ' + data_file
        load_path = create_path(load_folder,data_file, '')

        #gets dict of dataframes
        file_dfs = load_data(load_path,sheet_name = None)
        sheet_names = list(file_dfs)

        #iterate through sheets in file
        for sheet, df in file_dfs.items():
            #convert columns of file to regexd strings
            src_col_r = []
            for i in df.columns:
                m = re.search(get_regex(),i)
                if m != None:
                    src_col_r.append(m.group())
                else:
                    src_col_r.append('')

            #iterate over rows to copy into new dataframes
            for index, row in df.iterrows():
                for sheet, time_df in time_dict.items():
                    if index == sheet:
                        for spec_name in src_col_r:
                            if spec_name in df_col_r:
                                val = row[src_col_r.index(spec_name)]
                                time_df.loc[ind][spec_name] = val
    return time_dict

def append_groups(time_dict,table_path,specimen_limit):
    #insert row with group names
    df_table = load_data(table_path)
    group_row = []
    for col_name in df_table.columns:
        group_row.extend([col_name]*len(df_table[col_name].dropna()))


    for sheet, time_df in time_dict.items():
        offset = -(len(group_row)- len(time_df.columns))
        if offset == 0:
            offset = None

        group_row_cp = group_row[:offset]
        time_df.loc[-1] = pd.Series(group_row_cp,index = time_df.columns)
        # time_df = time.sort_index
        # time_df.index = time_df['temp_ind']
    return time_dict

def create_empty_outlier_table(save_path):
    if not os.path.isfile(save_path):
        workbook = xlsxwriter.Workbook(save_path)
        worksheet = workbook.add_worksheet()
        cell_format = workbook.add_format({'align':'right',
                                            'bold' : 'True',
                                           'font':'Arial',
                                           'font_size' : 10})
        label = 'A:AA'
        column_width = 18
        row = 0
        col = 0
        worksheet.write(row,col,'Outlier Specimens')
        worksheet.write(row,col+1,'Warnings')
        worksheet.set_column(label,column_width,cell_format)
        workbook.close()


def write_to_excel(time_dict,save_path):
    #save data to file
    create_save_folder(save_folder)
    writer = pd.ExcelWriter(save_path,engine='xlsxwriter')
    workbook = writer.book
    cell_format = workbook.add_format({'align':'right',
                                       'font':'Arial',
                                       'font_size' : 10})

    label_width = 18
    label = 'A:A'
    column_width = 18
    columns = 'B:BB'

    for sheet, time_df in time_dict.items():
        time_df.to_excel(writer,sheet_name = sheet)
        #formatting excel file
        worksheet_RAW = writer.sheets[sheet]
        worksheet_RAW.set_column(label, label_width, cell_format)
        worksheet_RAW.set_column(columns, column_width, cell_format)
    writer.save()


if __name__ == "__main__":

    files = get_files(load_folder)
    files = remove_non_excel(files)
    file_dict = files_to_dict(files)
    file_dict = insert_time(file_dict,time_unit)

    #sort file dictionary by given time unit
    file_dict = sort_time(file_dict,time_unit)

    # iterate through file to create sheet names
    df = get_df_dict(load_folder,files[0])
    sheet_list = get_sheet_names(file_dict,df)


    #create list that contain filtered specimen names
    df_table = load_table(table_path)
    specimen_limit = get_specimen_limit(df_table,specimen_limit)
    df_col_r = get_specimen_names(df_table)
    df_list = list_of_df(len(sheet_list),df_col_r, file_dict.values())

    #create ordered dict to tie sheetnames to dataframes
    time_dict = ordered_dict_from_lists(sheet_list,df_list)

    #fill time_dict with data from files
    time_dict = fill_time_dict(file_dict,load_folder,time_dict,df_col_r)
    table_folder = prepend_folder(table_folder)
    table_path = os.path.join(table_folder,table_file)

    #create outlier file
    outlier_path = os.path.join(table_folder,outlier_file)
    create_empty_outlier_table(outlier_path)

    #add the group row
    time_dict = append_groups(time_dict,table_path,specimen_limit)
    save_path = os.path.join(save_folder,save_file)
    write_to_excel(time_dict,save_path)
