import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go

import os
import re
from collections import OrderedDict
import pandas as pd
import time_course as tc

app = dash.Dash()

#load data before processing
print 'loading time course data'
data_folder = tc.save_folder
if data_folder is None:
    data_folder = 'Time course for Prism'
    if not os.direxists(os.path.join(os.getcwd(), data_folder)):
        raise TypeError("data_folder var has been changed in time course script and hardcoded value doesn't match anything in directory.")

data_folder = os.path.join(os.getcwd(),data_folder)

for filename in os.listdir(data_folder):
    if 'Time Course Graph Pad Transposed.xlsx' in filename and '.~lock' not in filename:
        xl = pd.ExcelFile(os.path.join(data_folder,filename))
        all_df = pd.read_excel(xl, None)

def drop_unnamed_cols(df):
    return df.drop(df.columns[df.columns.str.contains('unnamed',case = False)],axis = 1)

def get_group_names(df):
    return df.loc[-1].unique()
#take dataframe return dictionary of 3 arrays
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

type_list = get_group_names(all_df['Granulocytes'])
list_of_dict = []

for t in type_list:
    list_of_dict.append({'label' : str(t), 'value' : str(t)})

all_pts = dict.fromkeys(all_df)
for k in all_df.keys():
    x_list, y_dict, err_dict = generate_data_pts(all_df[k])
    all_pts[k] = {'y':y_dict,'err':err_dict}



app.layout = html.Div(children = [

    #sheet dropdown
    dcc.Dropdown(
        options=[
            {'label': 'New York City', 'value': 'NYC'},
            {'label': 'Montreal', 'value': 'MTL'},
            {'label': 'San Francisco', 'value': 'SF'}
        ],
        multi=True,
        value=["MTL","SF"]
    ),

    #group dropdown
    dcc.Dropdown(
        id = 'group dropdown',
        options=list_of_dict,
        multi=True,
        value=type_list
    ),


    dcc.Graph(
        id = 'scatter1',
        figure = go.Figure(
            data = [
                       go.Scatter(x=x_list,
                                  y=y_dict['KO'],
                                  error_y=dict(
                                        type='data',
                                        array=err_dict['KO'],
                                        visible=True
                                        )
                                 )
                     ]
                 )
        )
])

@app.callback(
    dash.dependencies.Output('scatter1','figure'),
    [dash.dependencies.Input('group dropdown','value')])
def update_scatter(groups):
    hold_val = 'Granulocytes'
    traces = []
    for g in groups:
        print all_pts[hold_val]['y']
        traces.append(
            go.Scatter(x=x_list,
                       y=all_pts[hold_val]['y'][g],
                       error_y=dict(
                             type='data',
                             array=all_pts[hold_val]['err'],
                             visible=True
                             ),
                        name = g

                      )
        )


    return {
        'data' : traces
    }



if __name__ == '__main__':
    app.run_server(debug=True)
