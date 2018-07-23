this set of scripts takes data in the format of the files in the `'RAW Data/' `directory and converts them into a format that's easier to
copy and paste in to Prism

## Details:

* pipeline.py  
automates the execution of the three other scripts

* data_regroup.py  
produces an excel file in the Rearranged Data folder with an added group column.  
This group column is created with a specified table file

* append_percent.py  
produces an excel file with percentages of each cell type relative to all cells and #will add#

* subtype_sheets.py  
separates the data for each cell type into separate excel sheets


## To Run:
Place the raw data you'd like to run in a folder named 'RAW Data'
otherwise rename the data_folder variable in pipeline.py

Then run the pipeline.py script

## Notes:
**To group the data the script relies on a Table file in the Table folder.**
if this doesn't exist all entries will be classified as 'ungrouped' in the
 group column

The script will create three folders after it's
execution if they hadn't already existed:
- Rearranged Data
- Calculated for Prism
- Transposed Calculated for Prism

the last folder will contain the data in the format that's prism friendly.
