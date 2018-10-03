#! /usr/bin/python2.7

################################################################################
# Primary Variables
data_folder = '/home/matt/Documents/USC-Rong-Lu-Lab/ania/Aging'
threshold_list = [0,0.05,0.10,0.15,0.20]
cell_types = ['Cgr','Cb','Chsc']
time_unit = 'D'
ext = '.xlsx'
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


def drop_unnamed_cols(df):
    return df.drop(df.columns[df.columns.str.contains('unnamed',case = False)],axis = 1)

def get_group_names(df):
    return df.loc[-1].unique()

def get_times(df,cell_type = None):
    time_list = []
    for col_name in df.columns:
        if cell_type != None:
            if cell_type in col_name:
                m = re.search(time_unit + "[0-9]+",col_name)
                if m is not None:
                    s = m.group(0)
                    s = s[len(time_unit):]
                    time_list.append(int(s))
        else:
            m = re.search(time_unit + "[0-9]+",col_name)
            if m is not None:
                s = m.group(0)
                s = s[len(time_unit):]
                time_list.append(int(s))
    return sorted(set(time_list))

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

def get_entries_over_threshold(df,column,threshold=0):
    if column in df.columns:
        return df[column][df[column] > threshold].sort_values(ascending=False)
    return []

def get_specimen_names(folder):
    files = get_file_names(folder,ext)
    specimen_names = OrderedDict()
    for f in files:
        m = re.search("M[0-9]+",f)
        if m is not None:
            s = m.group(0)
            specimen_names[f] = s
    return specimen_names

def get_file_names(folder,ext):
    files = []
    for (dirpath, dirnames, filenames) in os.walk(folder):
        files.extend(filenames)
        break

    ret_files = []

    for f in files:
        if f.endswith(ext):
            ret_files.append(f)

    return sorted(ret_files)

def get_file_dropdown(spec_dict):
    dropdown = []
    for fn, spec in spec_dict.items():
        entry = {'label' : spec, 'value' : fn}
        dropdown.append(entry)
    return dropdown

def get_threshold_dropdown(threshold_list):
    dropdown = []
    for thresh in threshold_list:
        entry = {'label' : thresh, 'value' : thresh}
        dropdown.append(entry)
    return dropdown

def get_cell_dropdown(cell_types):
    dropdown = []
    for cell in cell_types:
        entry = {'label' : cell, 'value' : cell}
        dropdown.append(entry)
    return dropdown

if not os.path.exists(data_folder):
    raise TypeError("data_folder var doesn't match anything in directory.")

# #load datafile
# for filen in os.listdir(data_folder):
#     if filename in filen and '.~lock' not in filen:
#         xl = pd.ExcelFile(os.path.join(data_folder,filen))
#         all_df = pd.read_excel(xl, None)
#
# #load dictionary of excel sheet names
# dict_of_sheets = OrderedDict()
# for sheet in all_df.keys():
#     dict_of_sheets[sheet] = {'label' : sheet, 'value' : sheet}
#
# #load dictionary of group names
# type_list = get_group_names(all_df['Granulocytes'])
# dict_of_groups = OrderedDict()
# for t in type_list:
#     dict_of_groups[t] = {'label' : str(t), 'value' : str(t)}
#
#
# #create dataframes for graphs and remove specimens
# all_pts = dict.fromkeys(all_df)
# for k in all_df.keys():
#     x_list, y_dict, err_dict = generate_data_pts(all_df[k])
#     all_pts[k] = {'y':y_dict,'err':err_dict}
#
# unit_time = get_time_unit(all_df['Granulocytes'])

colors = {
    'background': '#111111',
    'text': '#052E63'
}

# init_barcodes = update_barcodes(os.listdir(data_folder)[0],threshold[-1])
spec_dict = get_specimen_names(data_folder)
file_list = get_file_names(data_folder,ext)

file_dropdown = get_file_dropdown(spec_dict)
threshold_dropdown = get_threshold_dropdown(threshold_list)
cell_dropdown = get_cell_dropdown(cell_types)

app = dash.Dash()

app.layout = html.Div(children = [

    dcc.Dropdown(
        id = "file dropdown",
        options= file_dropdown,
        multi= False,
        value = file_list[0],
        clearable = False

    ),

    dcc.Dropdown(
        id = 'threshold dropdown',
        options=threshold_dropdown,
        multi=False,
        value=threshold_list[-1],
        clearable = False
    ),

    dcc.Dropdown(
        id = 'cell type dropdown',
        options=cell_dropdown,
        multi=True,
        value=cell_types[0],
        clearable = False
    ),

    dcc.Dropdown(
        id = 'barcode dropdown',
        # options=init_barcodes,
        multi=True,
        # value=init_barcodes,
        clearable = False
    ),



    dcc.Graph(id = 'scatter1'),
    # html.H2(
    #     children='Graph Data',
    #     style={
    #         'textAlign': 'left',
    #         'color': colors['text']
    #     }
    # )
    # dcc.Graph(id='table-container',style={'width' : '100%','display': 'inline-block', 'padding': '0 20'})
])

@app.callback(
        dash.dependencies.Output('barcode dropdown','options'),
        [dash.dependencies.Input('file dropdown', 'value'),
         dash.dependencies.Input('threshold dropdown', 'value'),
         dash.dependencies.Input('cell type dropdown', 'value')])
def update_barcode_options(file_name,threshold,cell_type):
    df = pd.read_excel(file_name)
    barcodes = []
    for col in df.columns:
        if cell_type in col:
            temp_bc = get_entries_over_threshold(df,col,threshold).index
            temp_bc = temp_bc[0:10]
            for bc in temp_bc:
                barcodes.append(df["code"].iloc[bc])
    barcodes = list(set(barcodes))

    dropdown = []
    for bc in barcodes:
        entry = {'label' : bc, 'value' : bc}
        dropdown.append(entry)
    return dropdown

@app.callback(
        dash.dependencies.Output('barcode dropdown','value'),
        [dash.dependencies.Input('file dropdown', 'value'),
         dash.dependencies.Input('threshold dropdown', 'value'),
         dash.dependencies.Input('cell type dropdown', 'value')])
def update_barcode_value(file_name,threshold,cell_type):
    df = pd.read_excel(file_name)
    barcodes = []
    for col in df.columns:
        if cell_type in col:
            temp_bc = get_entries_over_threshold(df,col,threshold)
            for bc in temp_bc.iloc[:5].index:
                barcodes.append(df["code"].iloc[bc])
    barcodes = list(set(barcodes))
    return barcodes

@app.callback(
    dash.dependencies.Output('scatter1','figure'),
    [dash.dependencies.Input('barcode dropdown','value'),
     dash.dependencies.Input('file dropdown', 'value'),
     dash.dependencies.Input('cell type dropdown','value')])
def update_scatter(barcodes,file_name,cell_type):
    traces = []

    df = pd.read_excel(file_name)
    time_list = get_times(df,cell_type)

    print time_list
    y_val = {}

    df_cell_cols = []
    for col in df.columns:
        if cell_type in col:
            df_cell_cols.append(col)

    for bc in barcodes:
        val_list = []
        for t in time_list:
            col_name = ''
            for col in df_cell_cols:
                if str(t) in col and cell_type in col:
                    col_name = col
                    break

        # print df[col_name][df['code'].isin(barcodes)]
            val_list.append(df[col_name][df['code'] == bc].values[0])

        y_val[bc] = val_list


    for bc in barcodes:
        traces.append(
            go.Scatter(x=time_list,
                       y=y_val[bc],
                       name=bc
                      )
        )


    return {
        'data' : traces,
        'layout' : go.Layout(
            xaxis = {
                'title' : ''
            },
            yaxis = {
                'title' : 'to be added'
            }
        )
    }

#
# @app.callback(
#     dash.dependencies.Output('table-container','figure'),
#     [dash.dependencies.Input('group dropdown','value'),
#      dash.dependencies.Input('file dropdown', 'value'),
#      dash.dependencies.Input('table dropdown', 'value')])
# def update_table(groups,sheet,show_table):
#     if show_table == False:
#         return ff.create_table(pd.DataFrame())
#     else:
#         y_pts = all_pts[sheet]['y']
#         err_range = all_pts[sheet]['err']
#         time_pts = get_time(all_df[sheet])
#
#
#
#         ret_df = pd.DataFrame(index=time_pts)
#         for g in groups:
#             ret_df[g] = pd.Series(y_pts[g],index = ret_df.index)
#             ret_df[str(g) + " - err"] = pd.Series(err_range[g],index = ret_df.index)
#         new_table_figure = ff.create_table(ret_df,index=True)
#         return new_table_figure
#         # return generate_table(ret_df)

# @app.callback(
#     dash.dependencies.Output('table-container','hidden'),
#     [dash.dependencies.Input('table dropdown', 'value')])
# def update_table(show_table):
#     if show_table:
#         return True
#     return False

if __name__ == '__main__':
    app.run_server(debug=True)
