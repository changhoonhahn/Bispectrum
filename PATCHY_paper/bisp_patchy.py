import numpy as np
import math as m
import os.path
import subprocess
import cosmolopy as cosmos
import multiprocessing as mp

# --- Local ---
from Spectrum import data as spec_data
from Spectrum import fft as spec_fft
from Spectrum import spec as spec_spec
from Spectrum import fortran as spec_fort

def bisp_wrapper(i_mock): 
    ''' Bispectrum calculation wrapper
    '''
    # catalog dictionary 
    catdict = {'catalog': {'name': 'patchy', 'n_mock': i_mock}} 

    spec = spec_spec.Spec('bispec', catdict)
    spec.calculate()

    return None 

def build_bisp_patchy(Nthreads): 
    ''' Calculate bispectrum for PATCHY mocks parallel for Nthreads 
    '''

    pool = mp.Pool(processes=Nthreads)
    mapfn = pool.map

    arglist = range(1, 1001)

    mapfn(bisp_wrapper, [arg for arg in arglist]) 

    pool.close()
    pool.terminate()
    pool.join()
    return 

if __name__=='__main__':
    build_bisp_patchy(10)
