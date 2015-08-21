import numpy as np
import os.path
import subprocess
import cosmolopy as cosmos

# --- Local ---
import data as spec_data
import fft as spec_fft

class Spec: 
    def __init__(self, spectrum, catalog, **kwargs):
        ''' Class for power/bispectrum measurements 
        
        specify catalog, version, mock file number, file specifications (e.g. Nrandom), 
        fiber collision correction method, correction specifications (e.g. sigma, fpeak)

        Parameters 
        ----------
        spectrum : 'power' or 'bispec'
        catalog : catalog dictionary 

        '''
        self.Type = spectrum  # power or bispec

        cat = catalog['catalog'] 
        if 'correction' in catalog.keys(): 
            corr = catalog['correction'] 
        else: 
            corr = {'name': 'default'} 
        if 'spec' in catalog.keys(): 
            spec = catalog['spec']
        else: 
            spec = {'P0': 20000, 'sscale':3600.0, 'Rbox':1800.0, 'box':3600, 'grid': 360}
        self.catalog = catalog      # store the catalogue/correction/spec dictionary
        self.scale = kwargs['box']
        k_fund = (2.0*m.pi)/np.float(self.scale)        # k fundamental 
        self.kfund = k_fund 
    
        if 'file' in kwargs.keys(): 
            self.file_name = kwargs['file'] 
        else: 
            self.file_name = self.File(**kwargs)

    def File(self, **kwargs):
        ''' File name of power/bispectrum 
        '''
        # directory 
        spec_dir = ''.join(['/mount/riachuelo1/hahn/', spectrum.lower(), '/']) 

        if spectrum.lower() == 'power':                         # set flags
            spec_str = 'POWERv5_'
        elif spectrum.lower() == 'bispec': 
            spec_spec = 'BISPv5_'
    
        data = spec_data.Data('data', self.catalog, **kwargs)
        self.data_file = data.file_name     # store data file 
        random = spec_data.Data('random', self.catalog, **kwargs)
        self.random_file = random.file_name # store random file 

        # data directory
        data_dir = '/'.join(data_file.split('/')[:-1]) + '/'
        power_dir = '/power/'.join(data_dir.split('/data/'))

        if self.Type == 'power':    
            # power spectrum (Ngrid, P0, Lbox) 
            spectrum_str = ''.join([
                '.grid', str(spec['grid']), 
                '.P0', str(spec['P0']), 
                '.box', str(spec['box'])])
        elif self.Type == 'bispec': 
            # bispectrum (Ngrid, Nmax, Ncut, s, P0, Lbox)
            # hardcoded
            spectrum_str = '.grid360.nmax40.ncut3.s3.P020000.box3600'
        
        file_name = ''.join([power_dir, 
            spec_str, data_file.rsplit('/')[-1], spectrum_str]) # combine file parts 
        self.file_name = file_name
    
        return file_name 

    def Read(self, **kwargs): 
        ''' Read power/bi-spectrum file and read values of interest  

        Notes
        -----
        * Data columns are hardcoded for version 5 of fortran codes 

        '''
        if self.Type == 'power': 
            # power spectrum v5 columns k, P0, P2, P4fast, P4slow, P0old, P0R, P2R, Re(W), Im(W), dum, dum, dum, dum 
            spec_cols = [0, 1, 2, 4] 
            data_cols = ['k', 'P0k', 'P2k', 'P4k']
        elif self.Type == 'bispec': 
            # bispectrum v5 columns k1, k2, k3, P0(k1), P0(k2), P0(k3), B0, Q0, P2(k1), P2(k2), P2(k3), B2, Q2, dum, dum 
            spec_cols = [0, 1, 2, 3, 4, 5, 6, 7]
            data_cols = ['k1', 'k2', 'k3', 
                    'P0k1', 'P0k2', 'P0k3', 'Bk', 'Qk']
        if not len(spec_cols) == len(data_cols): 
            raise ValueError("column lenghts dont' match") 

        self.data_columns = data_cols 

        if not os.path.isfile(self.file_name): 
            self.calculate(**kwargs)

        # read spectrum file 
        spec_data = np.loadtxt(self.file_name, unpack=True, usecols=spec_cols) 
    
        for i_col, col in enumerate(data_cols): 
            # import data columns 
            setattr(self, col, spec_data[i_col]) 
    
        # multiply k fund to triangle sides
        if self.Type == 'bispec': 
            self.k1 *= k_fund 
            self.k2 *= k_fund 
            self.k3 *= k_fund 
            
            # some extra useful values
            (self.data_columns).append('i_triange', 'avgk', 'kmax')
            self.i_triangle = range(len(self.k1))
            self.avgk = np.mean(self.k1, self.k2, self.k3) 
            self.kmax = np.max(self.k1, self.k2, self.k3) 
        
        return self.file_name

    def calculate(self, **kwargs): 
        ''' Calculate power/bispectrum for catalog 
        '''
        
        # FFt files
        D_fft = spec.FFT('data', self.catalog, **kwargs)
        D_fft_file = D_fft.file_name 
        
        R_fft = spec.FFT('random', self.catalog, **kwargs)
        R_fft_file = R_fft.file_name 

        spec_code = spec_fort.fortran_code(self.Type, self.catalog, **kwargs)
        spec_exe = spec_fort.fortran_code2exe(spec_code)
    
        # code and exe modification time 
        spec_code_mod_time = os.path.getmtime(spec_code)
        if not os.path.isfile(spec_exe): 
            spec_exe_mod_time = 0 
        else: 
            spec_exe_mod_time = os.path.getmtime(spec_exe)

        # if code was changed since exe file was last compiled then 
        # compile spec code 
        if spec_exe_mod_time < spec_code_mod_time: 
            spec_fort.compile_fortran_code(spec_code) 
    
        if self.Type == 'power': 
            # power spectrum code input: 
            #    random fft file, data fft file, powerspectrum file, Lbox, Nbins  
            spec_cmd = ' '.join([power_exe, 
                R_fft_file, D_fft_file, self.file_name, str(spec['sscale']), str(spec['grid']/2)
                ]) 

        elif self.Type == 'bispec': 
            # bispectrum code input: 
            #   period/data, random fft file, data fft file, bispectrum file  
            spec_cmd = ' '.join([power_exe, 
                '2', R_fft_file, D_fft_file, self.file_name]) 

        print spec_cmd  
        subprocess.call(spec_cmd.split()) 
            
        return None  
