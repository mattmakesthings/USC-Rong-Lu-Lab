#! /usr/bin/python2.7

# script to automate the execution of converting raw data
# to prism friendly copy and paste formatting

# TODO: convert this script to module form for maintainability
# reference - https://stackoverflow.com/questions/7974849/how-can-i-make-one-python-file-run-another

import data_regroup
import append_percent
import subtype_sheets
import sys
import os

filename = sys.argv[1]

os.system("data_regroup.py " + filename)
os.system("append_percent.py " + filename)
os.system("subtype_sheets.py " + filename)

# with open("data_regroup.py") as f:
#     code = compile(f.read(), "data_regroup.py", 'exec')
#     exec(code)
#
# with open("append_percent.py") as f:
#     code = compile(f.read(), "append_percent.py", 'exec')
#     exec(code)
#
# with open("subtype_sheets.py") as f:
#     code = compile(f.read(), "subtype_sheets.py", 'exec')
#     exec(code)
# execfile('data_regroup.py')
# execfile('append_percent.py')
# execfile('subtype_sheets.py')
