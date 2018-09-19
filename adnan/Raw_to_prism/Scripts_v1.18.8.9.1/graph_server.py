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
file_path = '/home/matt/Documents/USC-Rong-Lu-Lab/adnan/Raw_to_prism/Time course for Prism/Time Course Graph Pad Transposed.xlsx'
outlier_path = '/home/matt/Documents/USC-Rong-Lu-Lab/adnan/Raw_to_prism/Table/Outliers and Warnings.xlsx'
################################################################################

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import plotly.figure_factory as ff

import os
import re
from collections import OrderedDict
import pandas as pd

data_folder , filename = os.path.split(file_path)

from data_regroup import prepend_folder, load_table
from timecourse_outliers import clean_spec_list

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
    specimens = clean_spec_list(specimens)
    drop_cols = [str(first_chars) + str(specimen) for specimen in specimens]
    df = df.drop(drop_cols, axis=1, errors='ignore')
    return df

def get_time_unit(df):
    # get x values
    x = list(df.index)
    #remove group index
    reg = re.sub('[\d]+',"",str(x[0]))
    return reg

def get_time(df):
    time_pts = list(df.index)
    time_pts = [t for t in time_pts if t!= -1]
    return time_pts

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

def generate_table(dataframe, max_rows=10):
    return html.Table(
        # Header
        [html.Tr([html.Th(col) for col in dataframe.columns])] +

        # Body
        [html.Tr([
            html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
        ]) for i in range(min(len(dataframe), max_rows))]
    )


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


#create dataframes for graphs and remove specimens
all_pts = dict.fromkeys(all_df)
for k in all_df.keys():
    all_df[k] = remove_outliers(all_df[k],outlier_path)
    x_list, y_dict, err_dict = generate_data_pts(all_df[k])
    all_pts[k] = {'y':y_dict,'err':err_dict}

unit_time = get_time_unit(all_df['Granulocytes'])

colors = {
    'background': '#111111',
    'text': '#052E63'
}

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

    dcc.Dropdown(
        id = 'table dropdown',
        options=[
                {'label' : 'Show data table', 'value' : True},
                {'label' :'no table', 'value' : False}
                 ],
        multi=False,
        value=True,
    ),


    dcc.Graph(id = 'scatter1'),
    html.H2(
        children='Graph Data',
        style={
            'textAlign': 'left',
            'color': colors['text']
        }
    ),
    dcc.Graph(id='table-container',style={'width' : '100%','display': 'inline-block', 'padding': '0 20'})
    # html.Div(html.Div(id='table-container'),style={'width': '49%', 'display': 'inline-block', 'padding': '0 20'})
])

@app.callback(
    dash.dependencies.Output('scatter1','figure'),
    [dash.dependencies.Input('group dropdown','value'),
     dash.dependencies.Input('sheet dropdown', 'value')])
def update_scatter(groups,sheet):
    traces = []
    for g in groups:
        traces.append(
            go.Scatter(x=x_list,
                       y=all_pts[sheet]['y'][g],
                       error_y=dict(
                             type='data',
                             array=all_pts[sheet]['err'][g],
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


@app.callback(
    dash.dependencies.Output('table-container','figure'),
    [dash.dependencies.Input('group dropdown','value'),
     dash.dependencies.Input('sheet dropdown', 'value'),
     dash.dependencies.Input('table dropdown', 'value')])
def update_table(groups,sheet,show_table):
    if show_table == False:
        return ff.create_table(pd.DataFrame())
    else:
        y_pts = all_pts[sheet]['y']
        err_range = all_pts[sheet]['err']
        time_pts = get_time(all_df[sheet])



        ret_df = pd.DataFrame(index=time_pts)
        for g in groups:
            ret_df[g] = pd.Series(y_pts[g],index = ret_df.index)
            ret_df[str(g) + " - err"] = pd.Series(err_range[g],index = ret_df.index)
        new_table_figure = ff.create_table(ret_df,index=True)
        return new_table_figure
        # return generate_table(ret_df)

# @app.callback(
#     dash.dependencies.Output('table-container','hidden'),
#     [dash.dependencies.Input('table dropdown', 'value')])
# def update_table(show_table):
#     if show_table:
#         return True
#     return False

if __name__ == '__main__':
    app.run_server(debug=True)
