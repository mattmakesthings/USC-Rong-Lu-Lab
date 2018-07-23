this set of scripts takes data in the format of the files in the `'RAW Data/' `directory and converts them into a format that's easier to
copy and paste in to Prism

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
