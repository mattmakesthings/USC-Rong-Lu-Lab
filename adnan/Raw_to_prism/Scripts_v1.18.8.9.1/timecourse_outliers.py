#!/usr/bin/python2.7

# this script will filter the time course data for graphing purposes.
# Mark data for caution
'''
table_file -> used when creating the initial data

outlier_file -> Used to filter out data for graphing.

table_folder -> contains the table_file and outlier_file
'''


time_course_path = '/home/matt/Documents/USC-Rong-Lu-Lab/adnan/Raw_to_prism/Time course for Prism/Time Course Graph Pad Transposed.xlsx'
table_file = '/home/matt/Documents/USC-Rong-Lu-Lab/adnan/Raw_to_prism/Table/HSC-CLP 2.0 Table.xlsx'
outlier_path = '/home/matt/Documents/USC-Rong-Lu-Lab/adnan/Raw_to_prism/Table/Outliers and Warnings.xlsx'


import os
import pandas as pd


data_folder, time_course_file = os.path.split(time_course_path)
table_folder, outlier_file = os.path.split(outlier_path)


from data_regroup import load_data, prepend_folder,load_table
from time_course import get_df_dict, get_specimen_names


def highlight_format(workbook,color,font_color='black'):
    return workbook.add_format({'align':'right',
                                   'bg_color' : color,
                                   'font':'Arial',
                                   'font_color' : font_color,
                                   'font_size' : 10})

def clean_table(df_outlier):
    for col in df_outlier:
        df_outlier[col] = pd.to_numeric(df_outlier[col], errors='coerce')
    return df_outlier

def color_timecourse(time_course_dict, df_outlier,save_path):
    writer, workbook = initial_formatting(time_course_dict,save_path)
    red ='Outlier Specimens'
    yellow = 'Warnings'

    df_outlier = clean_table(df_outlier)

    red_col = df_outlier[red].dropna().astype(int).astype(str).values
    yellow_col = df_outlier[yellow].dropna().astype(int).astype(str).values

    red_col = convert_to_specimen_name(red_col)
    yellow_col = convert_to_specimen_name(yellow_col)

    red_format = highlight_format(workbook,'red',font_color='white')
    yellow_format = highlight_format(workbook,'yellow')
    width = 18

    for sheet, df in time_course_dict.items():
        df.to_excel(writer,sheet_name = sheet)
        names = list(df.columns)
        worksheet = writer.sheets[sheet]

        for col in names:
            if col in red_col:
                col_pos = names.index(col)
                worksheet.set_column(first_col=col_pos+1,last_col=col_pos+1, width=width, cell_format=red_format)
            if col in yellow_col:
                col_pos = names.index(col)
                worksheet.set_column(first_col=col_pos+1,last_col=col_pos+1, width=width, cell_format=yellow_format)
    writer.save()


#mimics formatting in time_course.write_to_excel
def initial_formatting(time_course_dict,save_path):
    writer = pd.ExcelWriter(save_path,engine = 'xlsxwriter')
    workbook = writer.book
    print writer
    cell_format = workbook.add_format({'align':'right',
                                       'font':'Arial',
                                       'font_size' : 10})
    label_width = 18
    label = 'A:A'
    column_width = 18
    columns = 'B:BB'

    for sheet, df in time_course_dict.items():
        df.to_excel(writer,sheet_name = sheet)
        worksheet_RAW = writer.sheets[sheet]
        worksheet_RAW.set_column(label, label_width, cell_format)
        worksheet_RAW.set_column(columns, column_width, cell_format)

    return writer, workbook

def convert_to_specimen_name(col):
    for num in range(len(col)):
        col[num] = 'M' + str(col[num])
    return col


def apply_color(color):
    return ['background-color:' + color]

if __name__ == "__main__":
    df_outlier = pd.read_excel(outlier_path)
    df_outlier = df_outlier.applymap(str)

    time_course_dict = load_data(time_course_path,sheet_name = None)

    table_path = os.path.join(table_folder,table_file)
    df_table = load_table(table_path)

    color_timecourse(time_course_dict,df_outlier,time_course_path)
