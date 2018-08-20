#! /usr/bin/python2.7

#this script launches a web server to display the output of the time_course script
'''
data_folder - Contains the output from the time_course script
table_folder - contains our outlier table, among other things
outlier_file - this file contains outliers that should be ignored
               for graphing purposes
filename - the specific file to be displayed
'''

### NEED TO FIX
'''
    If the outlier file contains an entire group,
    the graph will not load until that group is removed from the dropdown menu
'''

################################################################################
# Primary Variables
data_folder = 'Time course for Prism'
table_folder = 'Table'
outlier_file = 'Outliers and Warnings.xlsx'
filename = 'Time Course Graph Pad Transposed.xlsx'
################################################################################

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go

import os
import re
from collections import OrderedDict
import pandas as pd

from data_regroup import prepend_folder, load_table

def drop_unnamed_cols(df):
    return df.drop(df.columns[df.columns.str.contains('unnamed',case = False)],axis = 1)

def get_group_names(df):
    return df.loc[-1].unique()

def remove_outliers(df,outlier_path):
    df_table = load_table(outlier_path)
    col = df.columns
    pattern = re.compile("\d+")
    first_chars = pattern.sub("", col[0])
    first_chars = first_chars[0]
    specimens = df_table.T.values[0]
    drop_cols = [str(first_chars) + str(specimen) for specimen in specimens]
    df = df.drop(drop_cols, axis=1, errors='ignore')
    return df

def get_time_unit(df):
    # get x values
    x = list(df.index)
    #remove group index
    reg = re.sub('[\d]+',"",str(x[0]))
    return reg

def get_x_pts(df):
    # get x values
    x = list(df.index)
    #remove group index
    x.remove(-1)
    reg = re.compile('[\d]+')
    for ind in x:
        obj = reg.match(str(ind))
        x[x.index(ind)] = obj.group()

    return x

def get_y_pts(df):

    #drop unnamed columns in local df
    df = drop_unnamed_cols(df)
    # get WKO, RKO, etc.
    type_list = get_group_names(df)

    df_t = df.T
    ret_dict = {}
    for t in type_list:
        columns = df_t[df_t[-1] == t].index
        df_temp = df[list(columns)]

        mean_list = []
        for index, row in df_temp.iterrows():
            if not unicode(index) == '-1':
                mean_list.append(row.mean())
        ret_dict[t] = mean_list

    return ret_dict

def get_err(df):

    #drop unnamed columns in local df
    df = drop_unnamed_cols(df)
    # get WKO, RKO, etc.
    type_list = get_group_names(df)

    df_t = df.T
    ret_dict = {}
    for t in type_list:
        columns = df_t[df_t[-1] == t].index
        df_temp = df[list(columns)]

        err_list = []
        for index, row in df_temp.iterrows():
            if not unicode(index) == '-1':
                err_list.append(row.sem())
        ret_dict[t] = err_list
    return ret_dict

def generate_data_pts(df):
    x = get_x_pts(df)
    y = get_y_pts(df)
    err = get_err(df)
    return x,y,err

app = dash.Dash()

#load data before processing
print 'loading time course data'
data_folder = prepend_folder(data_folder)
if not os.path.exists(data_folder):
    raise TypeError("data_folder var doesn't match anything in directory.")

#load datafile
for filen in os.listdir(data_folder):
    if filename in filen and '.~lock' not in filen:
        xl = pd.ExcelFile(os.path.join(data_folder,filen))
        all_df = pd.read_excel(xl, None)

#load dictionary of excel sheet names
dict_of_sheets = OrderedDict()
for sheet in all_df.keys():
    dict_of_sheets[sheet] = {'label' : sheet, 'value' : sheet}

#load dictionary of group names
type_list = get_group_names(all_df['Granulocytes'])
dict_of_groups = OrderedDict()
for t in type_list:
    dict_of_groups[t] = {'label' : str(t), 'value' : str(t)}

table_folder = prepend_folder(table_folder)
outlier_path = os.path.join(table_folder,outlier_file)

#create dataframes for graphs and remove specimens
all_pts = dict.fromkeys(all_df)
for k in all_df.keys():
    all_df[k] = remove_outliers(all_df[k],outlier_path)
    x_list, y_dict, err_dict = generate_data_pts(all_df[k])
    all_pts[k] = {'y':y_dict,'err':err_dict}

unit_time = get_time_unit(all_df['Granulocytes'])

app.layout = html.Div(children = [

    #sheet dropdown
    dcc.Dropdown(
        id = "sheet dropdown",
        options=dict_of_sheets.values(),
        multi=False,
        value = dict_of_sheets.keys()[0],
        clearable = False

    ),

    #group dropdown
    dcc.Dropdown(
        id = 'group dropdown',
        options=dict_of_groups.values(),
        multi=True,
        value=dict_of_groups.keys(),
        clearable = False
    ),


    dcc.Graph(
        id = 'scatter1',
        )
])

@app.callback(
    dash.dependencies.Output('scatter1','figure'),
    [dash.dependencies.Input('group dropdown','value'),
     dash.dependencies.Input('sheet dropdown', 'value')])
def update_scatter(groups,sheet):
    hold_val = sheet
    traces = []
    for g in groups:
        traces.append(
            go.Scatter(x=x_list,
                       y=all_pts[hold_val]['y'][g],
                       error_y=dict(
                             type='data',
                             array=all_pts[hold_val]['err'][g],
                             visible=True
                             ),
                        name = g
                      )
        )


    return {
        'data' : traces,
        'layout' : go.Layout(
            xaxis = {
                'title' : 'Time (' + unit_time + ')'
            },
            yaxis = {
                'title' : 'to be added'
            }
        )
    }



if __name__ == '__main__':
    app.run_server(debug=True)
