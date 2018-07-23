#! /usr/bin/python2.7

# script to automate the execution of converting raw data
# to prism friendly copy and paste formatting

import os

#iterator over all files in a directory
data_folder = 'RAW Data Test'
for filename in os.listdir(os.getcwd() + data_folder):

    print filename

    #table file
    table_file = 'IL10KO 1.0 Table 01.xlsx'
    table_folder = 'Table/'

    #variable
    subgroup_size = 10

    with open("data_regroup.py") as f:
        code = compile(f.read(), "data_regroup.py", 'exec')
        exec(code)

    with open("append_percent.py") as f:
        code = compile(f.read(), "append_percent.py", 'exec')
        exec(code)

    with open("subtype_sheets.py") as f:
        code = compile(f.read(), "subtype_sheets.py", 'exec')
        exec(code)
