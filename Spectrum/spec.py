import numpy as np
import math as m 
import os.path
import subprocess
import cosmolopy as cosmos

# --- Local ---
import data as spec_data
import fft as spec_fft
import fortran as spec_fort

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
        self.Type = spectrum.lower()  # power or bispec

        self.catalog = catalog      # store the catalogue/correction/spec dictionary
        if 'correction' not in catalog.keys(): 
            self.catalog['correction'] = {'name': 'default'} 
        if 'spec' not in catalog.keys(): 
            self.catalog['spec'] = {'P0': 20000, 'sscale':3600.0, 'Rbox':1800.0, 'box':3600, 'grid': 360}

        self.scale = (self.catalog['spec'])['box']
        k_fund = (2.0*m.pi)/np.float(self.scale)        # k fundamental 
        self.k_fund = k_fund 
    
        if 'file' in kwargs.keys(): 
            self.file_name = kwargs['file'] 
        else: 
            self.file_name = self.File(**kwargs)

    def File(self, **kwargs):
        ''' File name of power/bispectrum 
        '''
        # directory 
        spec_dir = ''.join(['/mount/riachuelo1/hahn/', self.Type, '/']) 

        if self.Type == 'power':                         # set flags
            spec_str = 'POWERv5_'
        elif self.Type == 'bispec': 
            spec_str = 'BISPv5_'
    
        data = spec_data.Data('data', self.catalog, **kwargs)
        self.data_file = data.file_name     # store data file 
        random = spec_data.Data('random', self.catalog, **kwargs)
        self.random_file = random.file_name # store random file 

        # data directory
        data_dir = '/'.join((self.data_file).split('/')[:-1]) + '/'
        power_dir = '/power/'.join(data_dir.split('/data/'))
    
        spec = self.catalog['spec']
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
            spec_str, (self.data_file).rsplit('/')[-1], spectrum_str]) # combine file parts 
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
            self.k1 *= self.k_fund 
            self.k2 *= self.k_fund 
            self.k3 *= self.k_fund 
            
            # some extra useful values
            self.data_columns += ['i_triange', 'avgk', 'kmax']
            self.i_triangle = range(len(self.k1))
            self.avgk = (self.k1 + self.k2 + self.k3)/3.0
            self.kmax = np.array([np.max([self.k1[i], self.k2[i], self.k3[i]]) 
                    for i in range(len(self.k1))])
        
        return self.file_name

    def calculate(self, **kwargs): 
        ''' Calculate power/bispectrum for catalog 
        '''
        
        # FFt files
        D_fft = spec_fft.FFT('data', self.catalog, **kwargs)
        D_fft_file = D_fft.file_name 
        
        R_fft = spec_fft.FFT('random', self.catalog, **kwargs)
        R_fft_file = R_fft.file_name 

        # if FFT file does not exist
        if not os.path.isfile(D_fft_file): 
            D_fft.calculate()

        if not os.path.isfile(R_fft_file): 
            R_fft.calculate()

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
    
        spec = self.catalog['spec']
        if self.Type == 'power': 
            # power spectrum code input: 
            #    random fft file, data fft file, powerspectrum file, Lbox, Nbins  
            spec_cmd = ' '.join([spec_exe, 
                R_fft_file, D_fft_file, self.file_name, str(spec['sscale']), str(spec['grid']/2)
                ]) 

        elif self.Type == 'bispec':     # bispectrum 
            # double check that the counts are there
            # hardcoded
            count_file = '/home/users/rs123/Code/Fortran/counts2quad_n360_nmax40_ncut3_s3'
            self.count_file = count_file 

            if not os.path.isfile(count_file): 
                raise NotImplementedError('Count File does not exist') 

            # bispectrum code input: 
            #   period/data, random fft file, data fft file, bispectrum file  
            spec_cmd = ' '.join([spec_exe, 
                '2', R_fft_file, D_fft_file, self.file_name]) 

        print spec_cmd  
        subprocess.call(spec_cmd.split()) 
            
        return None  

if __name__=='__main__': 
    catdict = {'catalog': {'name': 'patchy', 'n_mock': 1}} 
    spec = Spec('bispec', catdict)
    spec.Read()
    
    power_file = '/mount/riachuelo1/hahn/power/PATCHY/dr12/v6c/POWERv5_Patchy-Mocks-DR12CMASS-N-V6C-Portsmouth-mass_0001.dat.grid360.P020000.box3600'
    k, Pk = np.loadtxt(power_file, unpack=True, usecols=[0,1])

    plt.figure(1) 
    plt.scatter(spec.k1, spec.P0k1, c='b') 
    plt.plot(k, Pk, ls='--')
    print spec.k1
    print spec.P0k1
    plt.yscale('log')
    plt.xscale('log')
    plt.show()  

    #spec.calculate()
