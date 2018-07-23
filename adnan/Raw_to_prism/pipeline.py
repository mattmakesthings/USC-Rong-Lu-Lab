#! /usr/bin/python2.7

# script to automate the execution of converting raw data
# to prism friendly copy and paste formatting

import os

#iterator over all files in a directory
data_folder = 'RAW Data/'

#table file
table_file = 'HSC-CLP 2.0 Table.xlsx'
table_folder = 'Table/'

#max length of subgroups
chimerism = 10

for filename in os.listdir(os.getcwd() + '/' + data_folder):
    print filename

    with open("data_regroup.py") as f:
        code = compile(f.read(), "data_regroup.py", 'exec')
        exec(code)

    with open("append_percent.py") as f:
        code = compile(f.read(), "append_percent.py", 'exec')
        exec(code)

    with open("subtype_sheets.py") as f:
        code = compile(f.read(), "subtype_sheets.py", 'exec')
        exec(code)
