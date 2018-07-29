import csv
import os
import scipy.io
import time
import cPickle as pickle
from scipy.sparse import csr_matrix
import numpy as np

def save_sparse_csr(filename, array):
    # note that .npz extension is added automatically
    np.savez(filename, data=array.data, indices=array.indices,
             indptr=array.indptr, shape=array.shape)

def load_sparse_csr(filename):
    # here we need to add .npz extension manually
    loader = np.load(filename + '.npz')
    return csr_matrix((loader['data'], loader['indices'], loader['indptr']),
                      shape=loader['shape'])


data_folder = 'mm10'
matrix_file = 'matrix.mtx'
genes_file = 'genes.tsv'
barcodes_file = 'barcodes.tsv'

matrix_file_path = os.path.join(data_folder,matrix_file)
genes_file_path = os.path.join(data_folder,genes_file)
barcodes_file_path = os.path.join(data_folder,barcodes_file)

mat_p = 'mat_csr.p'
gene_p = 'genes.p'
barcode_p = 'barcodes.p'

pickle_dir = 'pickled'
#check if pickled objects exist

if __name__ == "__main__":
    #check if pickle directory exists
    mat_path = os.path.join(pickle_dir,mat_p)

    if not os.path.isdir(pickle_dir):
        os.makedirs(pickle_dir)
        #pickle the objects

    else:
        # #check if pickled objects exist
        # if not os.path.isfile(mat_path):
        #     #pickle
        #     print 'pickling matrix'
        #     start = time.time()
        #     mat = scipy.io.mmread(matrix_path)
        #     end = time.time()
        #     print (end - start)
        #     pickle.dump( mat, open( mat_path, "wb" ))
        # mat = pickle.load( open (mat_path, "rb"))

        #check if pickled objects exist
        if not os.path.isfile(mat_path):
            #pickle
            print 'pickling matrix'
            start = time.time()
            print start
            mat = scipy.io.mmread(matrix_file_path)
            save_sparse_csr(mat_p,mat)
            end = time.time()
            print end
            print (end - start)
        mat = load_sparse_csr(mat_p)

    print type(mat)






#otherwise read in
# mat = scipy.io.mmread(matrix_file)
#
# genes_path = os.path.join(data_folder, "genes.tsv")
# gene_ids = [row[0] for row in csv.reader(open(genes_path), delimiter="\t")]
# gene_names = [row[1] for row in csv.reader(open(genes_path), delimiter="\t")]
#
# barcodes_path = os.path.join(data_folder, "barcodes.tsv")
# barcodes = [row[0] for row in csv.reader(open(barcodes_path), delimiter="\t")]
