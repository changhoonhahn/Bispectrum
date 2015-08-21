import numpy as np 
import os.path
import time 
import subprocess
import cosmolopy as cosmos

# --- Local ---
import data as spec_data
import fortran as spec_fort

class FFT: 
    def __init__(self, DorR, catalog, **kwargs): 
        ''' FFT class to manage FFT calculations for powerspectrum and bispectrum
            
        Parameters
        ----------
        DorR : data or random
        catalog : catalog dictionary 
    
        Notes
        -----
        * Version 5 of FFT code hardcoded 
        
        '''
        self.Type = DorR.lower() 
        self.catalog = catalog  

        cat = catalog['catalog'] 
        if 'correction' in catalog.keys(): 
            corr = catalog['correction']
        else: 
            corr = {'name': 'default'} 
    
        if 'spec' in catalog.keys(): 
            spec = catalog['spec']
        else: 
            spec = {'P0': 20000, 'sscale':3600.0, 'Rbox':1800.0, 'box':3600, 'grid': 360}

        if 'file' in kwargs.keys(): 
            self.file_name = kwargs['file'] 
        else: 
            self.file_name = self.file(**kwargs)

    def file(self, **kwargs): 
        ''' Return FFT file name 
        '''
        fft_dir = '/mount/riachuelo1/hahn/FFT/' # fft directory
         
        data = spec_data.Data(self.Type, self.catalog, **kwargs)
        self.data_file = data.file_name 
        data_file = data.file_name 

        FFT_str =  'FFTv5_'     # currently version 5 of the code 
    
        # FFTs from data file 
        fft_file = ''.join([fft_dir, 
            FFT_str, data_file.rsplit('/')[-1],
            '.grid', str(spec['grid']), 
            '.P0', str(spec['P0']), 
            '.box', str(spec['box'])
            ])

        return fft_file 

    def calculate(self, **kwargs): 
        ''' Calculate FFT 

        Notes 
        -----
        * bash command for version 5 FFT code is of the form : 
         FFT_FKP_BOSS_cic_il4_v5.exe idata box Ngrid interpol iflag P0  ifc icomp input_file {izbin} output_file
        
        * icomp is hardcoded 0 so that it takes into account completeness!
        '''

        FFT_code = spec_fort.fortran_code('fft', self.catalog, **kwargs)
        FFT_exe = spec_fort.fortran_code2exe(FFT_code)            # exe file 
    
        # code and exe modification time to make sure that the exe file is up to date
        FFT_code_mod_time = os.path.getmtime(FFT_code)
        if not os.path.isfile(FFT_exe): 
            FFT_exe_mod_time = 0 
        else: 
            FFT_exe_mod_time = os.path.getmtime(FFT_exe)

        # if code was changed since exe file was last compiled then compile fft code 
        if FFT_exe_mod_time < FFT_code_mod_time: 
            fc_util.compile_fortran_code(FFT_code) 
            
        fft_file = self.file_name    
        print 'CONSTRUCTING'
        print '============'
        print fft_file 

        if self.Type == 'data': 
            N_DorR = 0
        elif self.Type == 'random': 
            N_DorR = 1

        # determine "idata"
        if catalog['name'].lower() == 'cmass': 
            idata = 1 
            ifc = 0 
        elif catalog['name'].lower() == 'lasdamasgeo': 
            idata = 2
            ifc = 0 
        elif catalog['name'].lower() == 'qpm': 
            idata = 3 
            ifc = 0 
        elif catalog['name'].lower() == 'nseries': 
            idata = 10 
            ifc = 0 
        else: 
            raise NameError('Not yet included in FFT code') 
        
        # Bash command for version 5 of FFT code 
        # Bash command for version 5 of FFT code 
        # Bash command for version 5 of FFT code 
        # Bash command for version 5 of FFT code 
        # Bash command for version 5 of FFT code 
        # Bash command for version 5 of FFT code 
        # Bash command for version 5 of FFT code 
        # Bash command for version 5 of FFT code 
        # Bash command for version 5 of FFT code 
        FFT_cmd = ' '.join([
            FFT_exe, 
            str(idata), 
            str(spec['box']), str(spec['grid']), 
            "4", str(DorR_number), str(spec['P0']), 
            str(ifc), "0", data_file, fft_file]) 
        print FFT_cmd

        if  == 'data':  # don't bother checking if the file exists for mocks and run the damn thing 
            subprocess.call(FFT_cmd.split()) 

        elif DorR.lower() == 'random':      # random takes longer so check to see if it exists first
            # call FFT randomc ommand 
            if os.path.isfile(fft_file) == False: 
                print "Building ", fft_file 
                subprocess.call(FFT_cmd.split())
            else: 
                print fft_file, " already exists" 

        print 'Constructing ', 

    return fft_file  
