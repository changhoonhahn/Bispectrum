'''


Deal with Fortran for power spectrum and bispectrum calculations


Author(s): ChangHoon Hahn 


'''



import os.path
import numpy as np
import subprocess
import cosmolopy as cosmos
import data as spec_data


def fortran_code(type, catalog, **kwargs): 
    ''' Return appropriate FORTRAN code for calculating FFT or powerspectrum

    Parameters
    ----------
    type : 'fft', 'power', 'bispec'
    catalog : catalog dictionary 
    
    Notes
    -----
    * At the moment only "default" option available

    '''

    type = type.lower()     # code type 
    
    # catalog dictionary 
    cat = catalog['catalog']
    if 'correction' in catalog.keys(): 
        corr = catalog['correction']
    else: 
        corr = {'name': 'default'} 
    spec = catalog['spec']
    
    code_dir = '/home/users/hahn/powercode/Bispectrum/fortran/'

    if type == 'fft':           # fft
        f_code = ''.join([code_dir, 
            'FFT_FKP_BOSS_cic_il4_v5.f']) 

        # add more options later 
        # add more options later 
        # add more options later 
    elif type == 'power':       # power spectrum 
        f_code = ''.join([code_dir, 
            'power_FKP_SDSS_BOSS_v5.f'])

    elif type == 'bispec':      # bispectrum 
        f_code = ''.join([code_dir, 
            'bisp_fast_bin_fftw2_quad.f']) 
    else: 
        raise NameErrors("Only fft, power, and bispec options available") 

    return f_code

def fortran_code2exe(code): 
    ''' Return .exe file for fortran code 
    '''
    code_dir = '/'.join(code.split('/')[0:-1])+'/' 
    code_file = code.split('/')[-1]

    fort_exe = ''.join([code_dir, 'exe/', 
        '.'.join(code_file.rsplit('.')[0:-1]), '.exe']) 

    return fort_exe

def compile_fortran_code(code): 
    ''' Compiles fortran code (very simple, may not work) 
    '''
    # get executable file 
    exe_file = fortran_code2exe(code) 
    
    code_file = code.split('/')[-1]

    # compile command
    if 'FFT_FKP_BOSS_cic_il4' in code_file: 
        compile_cmd = ' '.join(['ifort -fast -o', exe_file, code, '-L/usr/local/fftw_intel_s/lib -lsrfftw -lsfftw -lm'])
    elif 'power_FKP_SDSS_BOSS' in code_file:
        compile_cmd = ' '.join(['ifort -fast -o', exe_file, code])
    elif 'bisp_fast_bin_fftw2' in code_file: 
        compile_cmd = ' '.join(['ifort -fast -o', exe_file, code, '-L/usr/local/fftw_intel_s/lib -lsrfftw -lsfftw'])
    else: 
        compile_cmd = ' '.join(['ifort -O3 -o', exe_file, code, '-L/usr/local/fftw_intel_s/lib -lsfftw -lsfftw'])
    
    print 'COMPILE COMMAND' 
    print '===============' 
    print compile_cmd

    # call compile command 
    subprocess.call(compile_cmd.split())

    return compile_cmd 
