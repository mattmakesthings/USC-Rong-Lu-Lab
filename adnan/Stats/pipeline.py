#! /usr/bin/python2.7

# script to automate the execution of converting raw data
# to prism friendly copy and paste formatting

import data_regroup
import append_percent
import subtype_sheets

filename = 'CLP 2.0 2mo RAW.xls'

with open("data_regroup.py") as f:
    code = compile(f.read(), "data_regroup.py", 'exec')
    exec(code)

with open("append_percent.py") as f:
    code = compile(f.read(), "append_percent.py", 'exec')
    exec(code)

with open("subtype_sheets.py") as f:
    code = compile(f.read(), "subtype_sheets.py", 'exec')
    exec(code)
# execfile('data_regroup.py')
# execfile('append_percent.py')
# execfile('subtype_sheets.py')
