import csv
import os
import scipy.io
import cPickle as pickle

data_folder = 'mm10'
matrix_file = 'matrix.mtx'
genes_file = 'genes.tsv'
barcodes_file = 'barcodes.tsv'

matrix_path = os.path.join(data_folder,matrix_file)
genes_path = os.path.join(data_folder,genes_file)
barcodes_path = os.path.join(data_folder,barcodes_file)

mat_p = 'mat.p'
gene_p = 'genes.p'
barcode_p = 'barcodes.p'

files = [mat_p,gene_p,barcode_p]

pickle_dir = 'pickled'
#check if pickled objects exist

if __name__ == "__main__":
    #check if pickle directory exists
    mat_path = os.path.join(pickle_dir,mat_p)

    if not os.path.isdir(pickle_dir):
        os.makedirs(pickle_dir)
        #pickle the objects

    else:
        #check if pickled objects exist
        if not os.path.isfile(mat_path):
            #pickle
            mat = scipy.io.mmread(matrix_path)

            pickle.dump( mat, open( mat_path, "wb" ))
        mat = pickle.load( open (mat_path, "rb"))

    print type(mat)






#otherwise read in
mat = scipy.io.mmread(matrix_file)

genes_path = os.path.join(data_folder, "genes.tsv")
gene_ids = [row[0] for row in csv.reader(open(genes_path), delimiter="\t")]
gene_names = [row[1] for row in csv.reader(open(genes_path), delimiter="\t")]

barcodes_path = os.path.join(data_folder, "barcodes.tsv")
barcodes = [row[0] for row in csv.reader(open(barcodes_path), delimiter="\t")]
