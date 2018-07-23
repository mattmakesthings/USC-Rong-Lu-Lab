#! /usr/bin/python2.7

# script to automate the execution of converting raw data
# to prism friendly copy and paste formatting

#name of file in RAW Data folder
filename = 'IL10KO 1.0 2mo RAW.xls'

#table file 
table_file = 'IL10KO 1.0 Table 01.xlsx'
table_folder = 'Table/'

with open("data_regroup.py") as f:
    code = compile(f.read(), "data_regroup.py", 'exec')
    exec(code)

with open("append_percent.py") as f:
    code = compile(f.read(), "append_percent.py", 'exec')
    exec(code)

subgroup_size = 3

with open("subtype_sheets.py") as f:
    code = compile(f.read(), "subtype_sheets.py", 'exec')
    exec(code)
