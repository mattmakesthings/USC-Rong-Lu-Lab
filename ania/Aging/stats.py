#! /usr/bin/python2.7
'''
This file creates a table that shows the percentage of a population of cells
over different and overlapping timepoints relative to the sum of the cells over
the entire time period.

How it works:
    copy and paste the absolute path of one of the files in the directory containing all
    the files.

    The script will look for a date in the filename and use that to name the output filename


'''

################################################################################
data_file = '/home/matt/Documents/USC-Rong-Lu-Lab/ania/Aging/0-Ania_M3000_percent-engraftment_070318.xlsx'
cell_types = ['Cgr','Cb']
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


# %matplotlib notebook

def cell_type_dict(df,cell_type):
    cell_dict = OrderedDict()
    for col_name in df.columns:
        if cell_type in col_name:
            m = re.search(time_unit + "[0-9]+",col_name)
            s = m.group(0)
            cell_dict[s] = df[col_name][df[col_name]!= 0]
    return cell_dict


def get_times(df):
    time_list = []
    for col_name in df.columns:
        m = re.search(time_unit + "[0-9]+",col_name)
        if m is not None:
            s = m.group(0)
            time_list.append(s)
    return sorted(set(time_list))

def get_data_indices(cell_dict,cell,time_pt):
    return list(cell_dict[cell][time_pt].index)

def get_intersection(cell_dict,cells,time_point):
    return list(set(get_data_indices(cell_dict,cells[0],time_point)).intersection(set(get_data_indices(cell_dict,cells[1],time_point))))

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

def get_sum(df,cell_type):
    total = 0
    for col_name in df.columns:
        if cell_type in col_name:
            total += df[col_name].sum()
    return total


def create_row(df,colum_names,cell_type,specimen):
    #remove specimen later
    time_pts = get_times(df)
    total = get_sum(df,cell_type)

    col_sums = OrderedDict()
    for time in time_pts:
        for df_col in df.columns:
            if cell_type in df_col and time in df_col:
                 col_sums[time] = df[df_col].sum()
    row_vals=[]
    for comb in colum_names:
        combination_list = comb.split("\n")
        if len(combination_list) != 0:
            combination_sum = 0
            for time in combination_list:
                if time in col_sums.keys():
                    combination_sum += col_sums[time]
            row_vals.append((combination_sum/total) * 100)
    return row_vals


def time_point_permutations(time_points):
    perms = []
    for L in range(0,len(time_points)+1):
        for subset in itertools.combinations(time_points,L):
            sset = list(subset)
            if len(sset) != 0:
                s = sset[0]
                if len(sset) == 1:
                    perms.append(s)
                else:
                    for time_pt in sset:
                        if time_pt != sset[0]:
                            s += "\n" + time_pt
                    perms.append(s)

    return perms

def create_dfs_from_dir(folder):
    fname_spec_dict = get_specimen_names(folder)
    df = pd.read_excel(list(fname_spec_dict.keys())[0])
    time_points = get_times(df)
    colum_names = time_point_permutations(time_points)

    df_dict = {}
    for cell in cell_types:
        df_dict[cell] = pd.DataFrame(columns = colum_names)

        for fname, specimen in fname_spec_dict.items():
            df = pd.read_excel(fname)
            df_dict[cell].loc[specimen] = create_row(df,colum_names,cell,specimen)

    return df_dict

def save_df(df_dict,filename):
    writer = pd.ExcelWriter(filename, engine = 'xlsxwriter')
    workbook = writer.book
    wrap_format = workbook.add_format({'text_wrap':True,
                                       'align':'left'
                                        })

    for cell, df in df_dict.items():
        df.to_excel(writer,sheet_name = cell)

    for sheet in writer.sheets:
        worksheet = writer.sheets[sheet]
        worksheet.set_column('A:AA',20,wrap_format)

    writer.save()

def get_output_filename(filename):
    m = re.search("_[0-9]+",filename)
    if m is not None:
        s = m.group(0)
        fn = "summary of " + s + ".xlsx"
        return fn
    else:
        print "date not found"
        return None



# def get_barcode_cell_dict(df,)

if __name__ == "__main__":
    df = pd.read_excel(data_file)
    cell_dict = OrderedDict()
    for i in cell_types:
         cell_dict[i] = cell_type_dict(df,i)
    time_points =  get_times(df)

    #for cell in cell_types:
    cell_name = cell_types[0]
    cell_dat = []
    for time in time_points:
        cell_dat.append(get_data_indices(cell_dict,cell_name,time))


    combined = []
    for time in time_points:
        combined.append(get_intersection(cell_dict,[cell_types[0],cell_types[1]],time))

    # labels = venn.get_labels(cell_dat, fill=['number', 'logic'])
    # fig, ax = venn.venn4(labels, names=time_points)

    # plt.savefig(cell_types[0]+ "+" +cell_types[1] +'.png')
    #plt.gcf().clear()

    # print get_specimen_names(os.path.dirname(data_file))
    df_dict = create_dfs_from_dir(os.path.dirname(data_file))
    fn = get_output_filename(data_file)
    if fn == None:
        fn = default_output_name
    save_df(df_dict,os.path.join(os.path.dirname(data_file),fn))
