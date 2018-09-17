#! /usr/bin/python2.7

#script to make venn diagrams

################################################################################
data_folder = '/home/matt/Documents/USC-Rong-Lu-Lab/ania/Aging/'
cell_types = ['Cgr','Cb']
#output folder will be created in data_folder
file_tag = '0-Ania'
output_folder = 'venn diagrams'
time_unit = 'D'
################################################################################

import os
import pandas as pd
import re
from collections import OrderedDict
import matplotlib.pyplot as plt
from matplotlib_venn import venn3
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
    if time_pt in cell_dict[cell].keys():
        return list(cell_dict[cell][time_pt].index)
    else:
        return None

def get_intersection(cell_dict,cells,time_point):
    all_indices = []
    for cell in cells:
        lst = get_data_indices(cell_dict,cell,time_point)
        if lst != None:
            all_indices.append(set(lst))
    # return list(set(get_data_indices(cell_dict,cells[0],time_point))
    # .intersection(set(get_data_indices(cell_dict,cells[1],time_point))))

    return list(set.intersection(*all_indices))

def get_barcodes(df):
    return df['code']

def get_file_names(folder,ext):
    files = []
    for (dirpath, dirnames, filenames) in os.walk(folder):
        files.extend(filenames)
        break

    ret_files = []

    for f in files:
        if f.endswith(ext) and file_tag in f:
            ret_files.append(f)

    return sorted(ret_files)

def get_venn_func(time_points):
    venn_dict = {
        '2' : venn.venn2,
        '3' : venn.venn3,
        '4' : venn.venn4,
        '5' : venn.venn5,
        '6' : venn.venn6
    }
    time_len = len(time_points)
    if time_len < 2:
        return None
    elif time_len > 6:
        print "\tover 6 time points not supported"
        return
    else:
        return venn_dict[str(time_len)]

def create_individual_venn(cell_dict,time_points,output_path):
    if not os.path.exists(os.path.join(output_path,specimen_name)):
        this_path = os.mkdir(os.path.join(output_path,specimen_name))

    this_path = os.path.join(output_path,specimen_name)

    for cell_name in cell_types:
        cell_dat = []
        for time in time_points:
            lst = get_data_indices(cell_dict,cell_name,time)
            if lst != None:
                cell_dat.append(lst)

        labels = venn.get_labels(cell_dat, fill=['number', 'logic'])

        if get_venn_func(time_points) != None:
            fig, ax = get_venn_func(time_points)(labels, names=time_points)

            plt.savefig(os.path.join(this_path,specimen_name + " " + cell_name + " " + date +'.png'))
            plt.gcf().clear()
        else:
            print "\t",specimen_name," ",cell_name," contains only one time point, No venn diagram will be created"

def create_combined_venn(cell_dict,time_points,output_path):
    if not os.path.exists(os.path.join(output_path,specimen_name)):
        this_path = os.mkdir(os.path.join(output_path,specimen_name))

    this_path = os.path.join(output_path,specimen_name)

    combined = []
    for time in time_points:
        combined.append(get_intersection(cell_dict,[cell_types[0],cell_types[1]],time))

    labels = venn.get_labels(combined, fill=['number', 'logic'])

    if get_venn_func(time_points) != None:
        fig, ax = get_venn_func(time_points)(labels, names=time_points)

        plt.savefig(os.path.join(this_path,specimen_name + " " + cell_types[0] + ' + ' + cell_types[1] + " " + date + '.png'))
        plt.gcf().clear()
    else:
        print "\t",specimen_name," "," + ".join(cell_types)," contains only one time point, No venn diagram will be created"


def get_specimen_name(filename):
    m = re.search("M[0-9]+",filename)
    if m is not None:
        s = m.group(0)
        return s
    return None

def get_date(filename):
    m = re.search("_[0-9]+",filename)
    if m is not None:
        s = m.group(0)
        s = s.replace("_","")
        return s
    return None

# def get_barcode_cell_dict(df,)

if __name__ == "__main__":
    output_path = os.path.join(data_folder,output_folder)

    if not os.path.exists(output_path):
        os.mkdir(output_path)

    files = get_file_names(data_folder,'.xlsx')
    for data_file in files:
        print data_file
        specimen_name = get_specimen_name(data_file)
        date = get_date(data_file)

        df = pd.read_excel(data_file)
        cell_dict = OrderedDict()
        for i in cell_types:
             cell_dict[i] = cell_type_dict(df,i)
        time_points =  get_times(df)

        create_individual_venn(cell_dict,time_points,output_path)
        create_combined_venn(cell_dict,time_points,output_path)
