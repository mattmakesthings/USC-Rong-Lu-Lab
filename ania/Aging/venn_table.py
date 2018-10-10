#! /usr/bin/python2.7
from __future__ import division
'''
This file creates a table that shows the percentage of a population of cells
over different and overlapping timepoints relative to the sum of the cells over
the entire time period.

'''

################################################################################
data_folder = '/home/matt/Documents/USC-Rong-Lu-Lab/ania/Aging/'
cell_types = ['Cgr','Cb']
time_unit = 'D'
threshold = 0.0
ext = '.txt'
################################################################################
default_output_name = 'venn_table thresh:'+ str(threshold)+ '.xlsx'

import os
import pandas as pd
import re
from collections import OrderedDict
import matplotlib.pyplot as plt
from matplotlib_venn import venn3
import itertools


import venn


# %matplotlib notebook


# taken from venn.py
# https://github.com/tctianchi/pyvenn
################################################################################################
def get_labels(data, fill=["number"]):
    """
    get a dict of labels for groups in data

    @type data: list[Iterable]
    @rtype: dict[str, str]

    input
      data: data to get label for
      fill: ["number"|"logic"|"percent"]

    return
      labels: a dict of labels for different sets

    example:
    In [12]: get_labels([range(10), range(5,15), range(3,8)], fill=["number"])
    Out[12]:
    {'001': '0',
     '010': '5',
     '011': '0',
     '100': '3',
     '101': '2',
     '110': '2',
     '111': '3'}
    """

    N = len(data)

    sets_data = [set(data[i]) for i in range(N)]  # sets for separate groups
    s_all = set(chain(*data))                             # union of all sets

    # bin(3) --> '0b11', so bin(3).split('0b')[-1] will remove "0b"
    set_collections = {}
    for n in range(1, 2**N):
        key = bin(n).split('0b')[-1].zfill(N)
        value = s_all
        sets_for_intersection = [sets_data[i] for i in range(N) if  key[i] == '1']
        sets_for_difference = [sets_data[i] for i in range(N) if  key[i] == '0']
        for s in sets_for_intersection:
            value = value & s
        for s in sets_for_difference:
            value = value - s
        set_collections[key] = value

    labels = {k: "" for k in set_collections}
    if "logic" in fill:
        for k in set_collections:
            labels[k] = k + ": "
    if "number" in fill:
        for k in set_collections:
            labels[k] += str(len(set_collections[k]))
    if "percent" in fill:
        data_size = len(s_all)
        for k in set_collections:
            labels[k] += "(%.1f%%)" % (100.0 * len(set_collections[k]) / data_size)

    return labels

################################################################################################

def cell_type_dict(df,cell_type):
    #key is time_pt, val is non_zero rows
    cell_dict = OrderedDict()
    for col_name in df.columns:
        if cell_type in col_name:
            m = re.search(time_unit + "[0-9]+",col_name)
            s = m.group(0)
            if threshold == 0:
                cell_dict[s] = df[col_name][df[col_name] > threshold]
                # print s," ",cell_type, " " ,len(cell_dict[s])
            else:
                cell_dict[s] = df[col_name][df[col_name] >= threshold]
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

def get_data(cell_dict,cell,time_pt):
    return cell_dict[cell][time_pt]

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

def column_names_to_label_keys(time_points):
    comb = []
    comb_names = time_point_permutations(time_points)
    for n in comb_names:
        if "\n" in n:
            comb.append(n)

    label_key_dict = OrderedDict()

    #create set names for single time points ('0001','0010', etc.)
    val = 0
    for t in list(reversed(time_points)):
        label_key_dict[t] = int(bin(2**val).replace("0b",""))
        val += 1

    #create set names for multiple time points ('0110','1001', etc.)
    for c in comb:
         combination_list = c.split("\n")
         new_label = 0
         for n in combination_list:
             new_label += label_key_dict[n]
         label_key_dict[c] = str(new_label).zfill(len(time_points))

    for t in time_points:
        hold = label_key_dict[t]
        label_key_dict[t] = str(hold).zfill(len(time_points))

    return label_key_dict


def get_percent_labels(labels):
    #gets label values over sum of all label values
    total = 0.0
    for k,v in labels.items():
        num = (int)(v.split(": ")[1])
        total += num
    # print total

    for k,v in labels.items():
        if total == 0:
            labels[k] = 0
        else:
            num = (int)(v.split(": ")[1])
            labels[k] = (num / total) * 100
            # print k, " ",labels[k]

    return labels

def create_row(df,column_names,cell_type,specimen):
    cell_dict = OrderedDict()
    for i in cell_types:
         cell_dict[i] = cell_type_dict(df,i)

    # get time points for cell type
    time_points = get_times(df,cell_type = cell_type)
    # print "create_row "+ str(time_points)

    # get indices of nonzero rows for cell_type
    cell_dat = []
    for time in time_points:
        cell_dat.append(get_data(cell_dict,cell_type,time))

    # get the dictionary of set values
    cell_inds = []
    for dat in cell_dat:
        cell_inds.append(list(dat.index))

    labels = get_labels(cell_inds, fill=['number', 'logic'])
    labels = get_percent_labels(labels)

    # create a translator between the set names and column names
    translator = column_names_to_label_keys(time_points)

    # finally fill row values according to translation
    row_vals = []
    for col in column_names:
        if col in translator.keys():
            row_vals.append(labels[translator[col]])
        else:
            row_vals.append(0)
    return row_vals

def create_row_combined(df,column_names,cell_types,specimen):
    cell_dict = OrderedDict()
    for i in cell_types:
         cell_dict[i] = cell_type_dict(df,i)

    time_points = []
    for cell in cell_types:
        time_points = time_points + get_times(df,cell_type = cell)

    time_points = list(sorted(set(time_points)))

    # get indices of nonzero rows for cell_type
    cell_dat = [pd.Series()]*len(time_points)
    for cell in cell_types:
        time_points_cell = get_times(df,cell_type = cell)
        for time in time_points_cell:
            ind = time_points.index(time)
            cell_dat[ind] = cell_dat[ind].add(get_data(cell_dict,cell,time),fill_value = 0)
        print len(cell_dat[0].index)
    exit()

    # get the dictionary of set values
    cell_inds = []
    for dat in cell_dat:
        cell_inds.append(list(dat.index))

    labels = get_percent_labels(labels)
    labels = get_labels(cell_inds, fill=['number', 'logic'])

    print time_points
    # create a translator between the set names and column names
    translator = column_names_to_label_keys(time_points)
    print translator
    print column_names

    print labels

    exit()
    row_vals = []
    for col in column_names:
        if col in translator.keys():
            print col
            print ""
            row_vals.append(labels[translator[col]])
        else:
            row_vals.append(0)
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
    df = pd.read_csv(list(fname_spec_dict.keys())[0],delimiter = "\t")
    time_points = get_times(df)
    column_names = time_point_permutations(time_points)

    df_dict = OrderedDict()
    for cell in cell_types:
        df_dict[cell] = pd.DataFrame(columns = column_names)

        for fname, specimen in fname_spec_dict.items():
            print fname, "\t", cell
            df = pd.read_csv(fname,delimiter = "\t")
            df_dict[cell].loc[specimen] = create_row(df,column_names,cell,specimen)


    cell_comb = ""
    for cell in cell_types:
        cell_comb += cell + " "

    df_dict[cell_comb] = pd.DataFrame(columns = column_names)

    for fname, specimen in fname_spec_dict.items():
        print fname, "\t", cell_comb
        df = pd.read_csv(fname,delimiter = "\t")
        df_dict[cell_comb].loc[specimen] = create_row_combined(df,column_names,cell_types,specimen)

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
        s = s.strip("_")
        fn = "venn table " + s + " thresh:" + str(threshold) + ".xlsx"
        return fn
    else:
        print "date not found"
        return None



# def get_barcode_cell_dict(df,)

if __name__ == "__main__":
    df_dict = create_dfs_from_dir(data_folder)

    fn = get_output_filename(os.listdir(data_folder)[0])
    if fn == None:
        fn = default_output_name
    save_df(df_dict,os.path.join(data_folder,fn))
