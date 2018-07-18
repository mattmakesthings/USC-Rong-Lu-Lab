#! /usr/bin/python2.7

#script to group specimen data
import pandas as pd
import numpy as np

#match raw_data row to table column
def sort_df(df_affect,df_table):
    #iterates through table excel sheet
    for i in df_table:
        for j in df_table[i]:
            s = "Specimen_M" + str(j)
            df_affect.loc[df_affect.index.to_series().str.contains(s), "group"] = str(i)
    return df_affect
if __name__ == "__main__":
    #load data into pandas dataframe
    filename = 'CLP 2.0 2mo RAW.xls'
    load_folder = 'RAW Data/'
    df_RAW = pd.read_excel(load_folder + filename)
    df_RAW.index = df_RAW.index.map(str)

    #add grouping column
    df_RAW.insert(loc=0, column="group",value="ungrouped")

    #read in table data
    table_file = 'HSC-CLP 2.0 Table.xlsx'
    df_table = pd.read_excel('Table/' + table_file)
    df_table.columns = df_table.columns.map(str)

    #sort the RAW data by group
    df_RAW = sort_df(df_RAW,df_table)

    # Drop the stats rows in the data
    df_RAW = df_RAW.drop(['Mean','SD'])

    #save data to excel file
    save_folder = 'Rearranged Data/'
    writer = pd.ExcelWriter(save_folder + 'Rearranged '+ filename)
    df_RAW.to_excel(writer,sheet_name='Sheet1')
    writer.save()
