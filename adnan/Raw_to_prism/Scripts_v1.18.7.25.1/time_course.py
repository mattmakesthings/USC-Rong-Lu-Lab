# this script combines multiple files to compare
# specimens over time
# IMPORTANT:
#       relies on results of either the pipeline script or the subtype_sheets script
#       set the chimerism var to be equal to the value of the script used above

'''
time unit -> time unit used in input file names

sub_folder -> this is the folder in the load folder that contains the data
to be used

load_folder -> this is the folder in which the load folder is contained

save_file -> the name of the resulting file once the script has finished

save_folder -> this will contain the save_file and wil be created if it
does not already exist

table_file -> used when creating the initial data

table_folder -> contains the table_file
'''
##################################################################
chimerism = 10
time_unit = "mo"
sub_folder = ''
load_folder = 'Transposed Calculated for Prism'
save_file = 'Time Course.xlsx'
save_folder = 'Time course for Prism'
table_file = 'IL10KO 1.0 Table 01.xlsx'
table_folder = 'Table'
##################################################################

import pandas as pd
import os
import re
from data_regroup import load_data, prepend_folder, create_path, create_save_folder, get_regex
from collections import OrderedDict
import operator

load_folder = prepend_folder(load_folder)
save_folder = prepend_folder(save_folder)
load_folder = os.path.join(load_folder,sub_folder)

def get_files(folder_):
    return os.listdir(folder_)

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

def insert_time(file_dict,time_unit):
    for k,v in file_dict.items():
        m = re.search(r"[0-9]+" + re.escape(time_unit), k)
        if m == None:
            raise AttributeError('var time_unit doesn\'t match files')

        s = m.group(0).replace(time_unit,'')
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


def get_specimen_names(df,sheet_list):
    print sheet_list[0]
    sheet =  sheet_list[0]
    df_col = df[sheet].columns
    df_col_r = []
    for i in df_col:
        m = re.search(get_regex(),i)
        if m != None:
            df_col_r.append(m.group())
        else:
            df_col_r.append('')

    return df_col_r

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

def append_groups(time_dict,table_path,chimerism):
    #insert row with group names
    df_table = load_data(table_path)
    group_row = []
    for col_name in df_table.columns:
        group_row.append(col_name)
        for x in range(chimerism - 1):
            group_row.append('')

    group_row = group_row[:-(len(group_row)- len(df_col_r))]
    # group_df = pd.DataFrame()
    # group_df = group_df.append(pd.Series(group_row,index = df_col_r), ignore_index = True)

    for sheet, time_df in time_dict.items():
        time_df.loc[-1] = pd.Series(group_row,index = df_col_r)
        # time_df = time.sort_index
        # time_df.index = time_df['temp_ind']
    return time_dict

def write_to_excel(time_dict,save_path):
    #save data to file
    create_save_folder(save_folder)
    save_path = create_path(save_folder,save_file,'')
    writer = pd.ExcelWriter(save_path,engine='xlsxwriter')

    for sheet, time_df in time_dict.items():
        time_df.to_excel(writer,sheet_name = sheet)
        #formatting excel file
        workbook = writer.book
        worksheet_RAW = writer.sheets[sheet]

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
    df_col_r = get_specimen_names(df,sheet_list)
    df_list = list_of_df(len(sheet_list),df_col_r, file_dict.values())

    #create ordered dict to tie sheetnames to dataframes
    time_dict = ordered_dict_from_lists(sheet_list,df_list)

    #fill time_dict with data from files
    time_dict = fill_time_dict(file_dict,load_folder,time_dict,df_col_r)
    table_folder = prepend_folder(table_folder)
    table_path = os.path.join(table_folder,table_file)

    #add the group row
    time_dict = append_groups(time_dict,table_path,chimerism)
    save_path = os.path.join(save_folder,save_file)
    write_to_excel(time_dict,save_path)
