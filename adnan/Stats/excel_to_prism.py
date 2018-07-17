#! /usr/bin/python2.7

#script to group specimen data
import pandas as pd
import numpy as np

#match raw_data row to table column
# def sort_df(df_affect,df_table):s
#     #iterates through table excel sheet
#     for i in df_table:
#         for j in df_table[i]:
#             s = "Specimen_M" + str(j)
#             df_affect.loc[df_affect.index.to_series().str.contains(s), "group"] = str(i)


col_names = ["Granulocytes","Monocytes","B cells","CD4T cells","CD8T cells"]
def combine(df_src,df_dest):
    for i in col_names:
        df_dest[i] = df_src.iloc[:,df_src.columns.str.contains(i)].sum(1)
        df_dest["% " + i] = (df_src[i] * 100.0)/ df_src["Alive"]
    return df_dest

# def attach_percentage(df_src,df_dest):
#     for i in col_names:
#         df_dest["%% " + i] = df_src[i] / df_src["Alive"]
#     return df_dest

if __name__ == "__main__":
    #load data into pandas dataframe
    filename = 'CLP 2.0 2mo RAW.xls'
    df_rearranged = pd.read_excel('Rearranged Data/' + 'Rearranged '+ filename)

    #create dataframe for 'all' sheet calculations
    all_df = df_rearranged[['group','Alive']].copy()
    all_df = combine(df_rearranged,all_df)

    #rearrange order of columns
    #subtype_df = df_rearranged[[]]

    #save data to excel file
    save_folder = 'Calculated for Prism/'
    writer = pd.ExcelWriter(save_folder + 'Graph Pad '+ filename)
    all_df.to_excel(writer,sheet_name='All')
    writer.save()
