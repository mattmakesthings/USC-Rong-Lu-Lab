#! /bin/bash

#converts all .txt files in folder to .xlsx

for i in *.txt;
do
  output=$(eval "basename $i .txt");
  ssconvert $output.txt 0-$output.xlsx;
done
