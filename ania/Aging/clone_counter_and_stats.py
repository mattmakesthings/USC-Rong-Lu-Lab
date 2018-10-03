#! /usr/bin/python2.7
from __future__ import division
'''
This file creates a table that shows the percentage of a population of cells
over different and overlapping timepoints relative to the sum of the cells over
the entire time period.

How it works:
    copy and paste the absolute path of ONE of the files in the directory containing all
    the files of interest.

    The script will look for a date in the filename and use that to name the output filename


'''

################################################################################
data_file = '/home/matt/Documents/USC-Rong-Lu-Lab/ania/Aging/0-Ania_M3000_percent-engraftment_070318.xlsx'
cell_types = ['Cgr','Cb','Chsc']
threshold_list = [0,0.05,0.10,0.15,0.20]
time_unit = 'D'
ext = '.xlsx'
################################################################################
default_output_name = 'percent engraftment summary.xlsx'

import os
import pandas as pd
import re
from collections import OrderedDict
import matplotlib.pyplot as plt
from matplotlib_venn import venn3
import itertools
import venn
from scipy import stats
import numpy as np
# %matplotlib notebook

def cell_type_dict(df,cell_type):
    #key is time_pt, val is non_zero rows
    cell_dict = OrderedDict()
    for col_name in df.columns:
        if cell_type in col_name:
            m = re.search(time_unit + "[0-9]+",col_name)
            s = m.group(0)
            cell_dict[s] = df[col_name][df[col_name]!= 0]
    return cell_dict


def get_times(df,cell_type = None):
    time_list = []
    for col_name in df.columns:
        if cell_type != None:
            if cell_type in col_name:
                m = re.search(time_unit + "[0-9]+",col_name)
                if m is not None:
                    s = m.group(0)
                    time_list.append(s)
        else:
            m = re.search(time_unit + "[0-9]+",col_name)
            if m is not None:
                s = m.group(0)
                time_list.append(s)
    return sorted(set(time_list))

def get_full_timelist(folder):
    time_list = []
    for f in get_file_names(folder,ext):
        df = pd.read_excel(f)
        curr_times = get_times(df)
        if len(curr_times) > len(time_list):
            time_list = curr_times
            ret_df = df
    return time_list, ret_df

def get_barcodes(df):
    return df['code']

def get_file_names(folder,ext):
    files = []
    for (dirpath, dirnames, filenames) in os.walk(folder):
        files.extend(filenames)
        break

    ret_files = []

    for f in files:
        if f.endswith(ext):
            ret_files.append(f)

    return sorted(ret_files)

def get_specimen_names(folder):
    files = get_file_names(folder,ext)
    specimen_names = OrderedDict()
    for f in files:
        m = re.search("M[0-9]+",f)
        if m is not None:
            s = m.group(0)
            specimen_names[f] = s
    return specimen_names

def all_substring_in_string(lst,str):
    all_found = True
    for substr in lst:
        if substr not in str:
            all_found = False
            break
    return all_found

def get_matching_col_name(column_names,output_column_names):
    out_dict = OrderedDict()
    for out_col in output_column_names:
        col_piece = out_col.split()
        for col in column_names:
            if all_substring_in_string(col_piece, col):
                out_dict[out_col] = col
                break
    return out_dict

def get_entries_over_threshold(df,column,threshold=0):
    if column in df.columns:
        return df[column][df[column] > threshold]
    return []

def create_row(filename,output_column_names,time_list,threshold):
    count_dict = {}
    df = pd.read_excel(filename)
    col_match = get_matching_col_name(df.columns,output_column_names)
    for out_col, orig_col in col_match.items():
        val = get_entries_over_threshold(df,orig_col,threshold)
        count_dict[out_col] = len(val)

    row_vals = []
    for col in output_column_names:
        if col not in count_dict.keys():
            row_vals.append(0)
        else:
            row_vals.append(count_dict[col])

    return row_vals

def final_column_names(df,time_points):
    col_names = []
    for col in df.columns:
        for time in time_points:
            for cell in cell_types:
                if time in col and cell in col:
                    col_names.append(cell + " " + time)
    return col_names

def create_dfs_from_dir(folder):
    fname_spec_dict = get_specimen_names(folder)
    time_points, df = get_full_timelist(folder)
    column_names = final_column_names(df,time_points)
    fname_list = get_file_names(folder,ext)

    df_dict = OrderedDict()
    for thresh in threshold_list:
        print thresh
        first_df_iter = True
        for filename,specimen in fname_spec_dict.items():
            if first_df_iter == True:
                first_df_iter = False
                df_dict[thresh] = pd.DataFrame(columns = column_names)

            df_dict[thresh].loc[specimen] = create_row(filename,column_names,time_points,thresh)
    return df_dict

def add_stats_df_dict(df_dict):
    for thresh, df in df_dict.items():
        add_stats(df)

def add_stats(df):
    specimen = get_specimen_index(df)
    add_blank(df)
    add_count(df)
    add_average(df,specimen)
    add_std_dev(df,specimen)
    add_SEM(df,specimen)

def get_specimen_index(df):
    return df.index

def add_blank(df):
    df.loc[""] = [""] * len(df.columns)

def add_count(df):
    row_vals = []
    for col in df.columns:
        row_vals.append(len(df[col][df[col] > 0]))
    df.loc["count"] = row_vals

def add_average(df,specimen):
    row_vals = []
    val = 0
    for col in df.columns:
        for n in specimen:
            val += df[col][n]
        row_vals.append(round(val / len(specimen),3))
        val = 0
    df.loc["average"] = row_vals

def add_std_dev(df,specimen):
    row_vals = []
    for col in df.columns:
        row_vals.append(round(np.std(df[col][0:len(specimen)]),3))
    df.loc["std_dev"] = row_vals

def add_SEM(df,specimen):
    row_vals = []
    for col in df.columns:
        row_vals.append(round(stats.sem(df[col][0:len(specimen)]),3))
    df.loc["SEM"] = row_vals

def save_df(df,filename):
    writer = pd.ExcelWriter(filename, engine = 'xlsxwriter')
    workbook = writer.book
    wrap_format = workbook.add_format({'text_wrap':True,
                                       'align':'right'
                                        })

    for threshold, df in df_dict.items():
        df.to_excel(writer,sheet_name = str(threshold))

    for sheet in writer.sheets:
        worksheet = writer.sheets[sheet]
        worksheet.set_column('A:AA',10,wrap_format)

    writer.save()

def get_output_filename(filename):
    m = re.search("_[0-9]+",filename)
    if m is not None:
        s = m.group(0)
        fn = "clone counts of " + s + ".xlsx"
        return fn
    else:
        print "date not found"
        return None

if __name__ == "__main__":
    df_dict = create_dfs_from_dir(os.path.dirname(data_file))
    add_stats_df_dict(df_dict)

    fn = get_output_filename(data_file)
    if fn == None:
        fn = default_output_name
    save_df(df_dict,os.path.join(os.path.dirname(data_file),fn))
