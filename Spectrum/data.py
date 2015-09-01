'''

Code to handle galaxy data for 
powerspectrum and bispectrum calculations

Author(s): ChangHoon Hahn 


'''

import numpy as np
import scipy as sp 
import time 
import random
import os.path
import subprocess
import cosmolopy as cosmos
import warnings 
import matplotlib.pyplot as plt

# --- Local ----
from utility.fitstables import mrdfits

class Data: 
    def __init__(self, DorR, catalog, **kwargs): 
        ''' Data class for calculation powerspectrum and bispectrum 

        Parameters
        ----------
        DorR : 'data' or 'random'
        catalog :  Catalog Dictionary 

        '''
        self.catalog = catalog                    # save catalog metadata
        cat = catalog['catalog'] 
        if 'correction' in catalog.keys(): 
            corr = catalog['correction'] 
        if DorR.lower() not in ('data', 'random'): 
            raise ValueError("DorR can only be 'data' or 'random'")

        self.Type = DorR.lower()        # Data or Random file 
        self.columns = None             # Data columns 
        self.ra = None                  # RA
        self.dec = None                 # Dec
        self.z = None                   # Redshift (z)
        self.weight = None
        self.wfc = None
        self.comp = None 

        if 'file' in kwargs.keys():     # if file name is specified
            self.file_name = kwargs['file']
        else:                           # otherwise 
            self.file_name = self.File(**kwargs)           # File name of data 
    
        self.cosmo = None
        if 'cosmo' in kwargs.keys():    # set Cosmology
            self.cosmo = kwargs['cosmo']

    def File(self, **kwargs): 
        ''' Function to get file name of Data class using catalog dictionary. Only default mock 
        catalogs included. See notes.

        Parameters
        ----------
        DorR : data or random
        catalog : catalog dictionary 

        Notes 
        -----
        * If catalog dictionary is not included, returns None. 
        * 'default' mocks are the original mocks in which they were downloaded

        '''
        cat = self.catalog['catalog']
        if 'correction' in (self.catalog).keys(): 
            corr = self.catalog['correction'] 
        else: 
            corr = {'name': 'default'} 
        DorR = self.Type

        if cat['name'].lower() == 'patchy':               # PATHCY mocks -------------
            data_dir = '/mount/riachuelo1/hahn/data/PATCHY/dr12/v6c/'   # data directory

            if DorR.lower() == 'data':                  # Data catalogs  
                if corr['name'].lower() == 'default': 
                    file_name = ''.join([data_dir, 
                        'Patchy-Mocks-DR12CMASS-N-V6C-Portsmouth-mass_', 
                        str("%04d" % cat['n_mock']), '.dat']) 
                else: 
                    return None
            elif DorR == 'random':                      # Random catalog 
                file_name = ''.join([data_dir, 'Random-DR12CMASS-N-V6C-x50.vetoed.dat'])
    
        elif 'cmass' in cat['name'].lower():                # CMASS ---------------------
            data_dir = '/mount/riachuelo1/hahn/data/CMASS/'
        
            cosmo_str = ''
            if 'fid' in cat['name'].lower():  
                cosmo_str = '_fidcomso'

            if DorR == 'data':                      # mock catalogs 
                if corr['name'].lower() in ('default'): 
                    file_name = ''.join([data_dir, 
                        'cmass-dr12v4-N-Reid', cosmo_str, '.dat']) 
                else: 
                    return None
            elif DorR == 'random':                  # random catalog 
                file_name = ''.join([data_dir, 
                    'cmass-dr12v4-N-Reid', cosmo_str, '.ran.dat'])
        elif 'nseries' in cat['name'].lower():              # Nseries ---------------------
            data_dir = '/mount/riachuelo1/hahn/data/Nseries/'

            if DorR == 'data': 
                if corr['name'].lower() in ('default'): 
                    file_name = ''.join([data_dir, 
                        'CutskyN', str(cat['n_mock']), '.dat'])
                elif 'zbin' in corr['name'].lower():
                    # Redshift binning of mocks (e.g. zbin1of5)
                    file_name = ''.join([data_dir, 
                        'CutskyN', str(cat['n_mock']), '.', corr['name'].lower(), '.dat'])
                else: 
                    raise NotImplementedError('Not yet implemented')
            elif DorR == 'random':      # random catalog
                # regardless of how it's corrected
                file_name = ''.join([data_dir, 
                    'Nseries_cutsky_randoms_50x_redshifts_comp.dat']) 

        else: 
            return None 

        return file_name

    def Read(self, **kwargs):
        ''' Read in data file 

        '''
        DorR = self.Type        # Data or Random
        
        # Catalog dictionary 
        cat = self.catalog['catalog'] 
        if 'correction' in self.catalog.keys(): 
            corr = self.catalog['correction'] 
        else: 
            corr = {'name': 'default'} 
        
        catalog_cols, col_index, col_fmt = self.Columns()    # get columns and indices
        
        # read in data or random file 
        dr_data = np.loadtxt(self.file_name, unpack=True, usecols=col_index)

        # catalog columns 
        for i_col, catalog_col in enumerate(catalog_cols): 
            setattr(self, catalog_col, dr_data[i_col]) 

        return None

    def Write(self, **kwargs): 
        ''' Write out data 

        '''
        catalog_cols, col_index, col_fmt = self.Columns()    # get columns and indices

        col_list = [] 
        for col in catalog_cols: 
            col_data = getattr(self, col)
            try: 
                if not isinstance(col_data, col_type): 
                    raise ValueError("Data columns are not the same data type")
                else: 
                    pass
            except NameError: 
                col_type = type(col_data)
            
            col_list.append(col_data) 

        header_str = ' '.join(['Columns :']+catalog_cols)
        np.savetxt(self.file_name, (np.vstack(np.array(col_list))).T, fmt=col_fmt, delimiter='\t', header=header_str)
    
        return None

    def Columns(self): 
        ''' Assign column names and column indices for data file. 
        Main function for interfacing with order of columns in data files  

        Notes 
        -----
        * Clunky and hardcoded at the moment. 
        * Or of catalog_columns and column_index have to be the same!
        '''
        DorR = self.Type    # data or random 
        cat = self.catalog['catalog']

        if cat['name'].lower() == 'patchy':                   # PATCHY ------------------
            if DorR == 'data':      # data
                catalog_columns = ['ra', 'dec', 'z', 'nbar', 'wfc'] # columns 
                catalog_col_fmt = ['%10.5f', '%10.5f', '%10.5f', '%.5e', '%10.5f'] 
            else:                   # random 
                catalog_columns = ['ra', 'dec', 'z', 'nbar']        # columns 
                catalog_col_fmt = ['%10.5f', '%10.5f', '%10.5f', '%.5e']
        elif 'cmass' in cat['name'].lower():                    # CMASS -----------------
            if DorR == 'data':      # data
                catalog_columns = ['ra', 'dec', 'z', 'nbar', 'wsys', 'wnoz', 'wfc', 'comp']
                catalog_col_fmt = ['%10.5f', '%10.5f', '%10.5f', '%.5e', '%10.5f', '%10.5f', '%10.5f', '%10.5f'] 
            else:                   # random 
                catalog_columns = ['ra', 'dec', 'z', 'nbar', 'comp']
                catalog_col_fmt = ['%10.5f', '%10.5f', '%10.5f', '%.5e', '%10.5f'] 
        elif 'nseries' in cat['name'].lower():                  # Nseries -----------------
            if DorR == 'data':      # data
                catalog_columns = ['ra', 'dec', 'z', 'wfc', 'comp']
                catalog_col_fmt = ['%10.5f', '%10.5f', '%10.5f', '%10.5f', '%10.5f'] 
            else:                   # random 
                catalog_columns = ['ra', 'dec', 'z', 'comp']
                catalog_col_fmt = ['%10.5f', '%10.5f', '%10.5f', '%10.5f'] 
        else: 
            raise NotImplementedError("Not Yet Coded")
            
        self.columns = catalog_columns
        self.col_index = range(len(catalog_columns)) 
        self.col_fmt = catalog_col_fmt
        
        return [self.columns, self.col_index, self.col_fmt]

    def Cosmo(self): 
        ''' Set cosmology of catalog 

        '''
        cat = self.catalog['catalog'] 
        """
          if (idata.eq.1) then !CMASS sample
             Om0=0.274
          elseif (idata.eq.2) then !LasDamas
             Om0=0.25
          elseif (idata.eq.3) then !QPM north
            !         Om0=0.29 !dr12c mocks
             Om0=0.31 !dr12d mocks
          elseif (idata.eq.4) then !QPM south
    !         Om0=0.29 !dr12c mocks
             Om0=0.31 !dr12d mocks
          elseif (idata.eq.5) then !LOWZ sample
             Om0=0.3
          elseif (idata.eq.6) then !PATCHY
             Om0=0.307115
          elseif (idata.eq.7) then !PTHALOS CMASS north
             Om0=0.274
          elseif (idata.eq.8) then !PTHALOS CMASS south
             Om0=0.274
          else
             write(*,*)'specify which dataset you want!'
        """
        # Omega Matter
        if cat['name'].lower() in ('lasdamasgeo'): 
            # LasDamas Catalog with SDSS Geometry 
            omega_m = 0.25  
        elif cat['name'].lower() in ('nseries'): 
            omega_m = 0.31 
        elif cat['name'].lower() in ('patchy'): 
            omega_m = 0.307115
        elif 'cmass' in cat['name'].lower(): 
            # CMASS
            if 'fid' in cat['name'].lower(): 
                omega_m = 0.31
            else: 
                omega_m = 0.274
        else: 
            raise NotImplementedError('Not yet included') 
        
        # survey cosmology  
        cosmo = {} 
        cosmo['omega_M_0'] = omega_m 
        cosmo['omega_lambda_0'] = 1.0 - omega_m 
        cosmo['h'] = 0.676
        cosmo = cosmos.distance.set_omega_k_0(cosmo) 
        self.cosmo = cosmo 

        return cosmo 

def build_data(DorR, catalog): 
    ''' Construct default data for powerspectrum/bispectrum calculation 
    
    Parameters
    ----------
    DorR : data or random  
    catalog : catalog dictionary 

    Notes
    -----
    * Everything is very hardcoded. 
    * This function should be used as a reference for data columns
    
    '''
    if DorR not in ('data', 'random'): 
        return False
    cat = catalog['catalog']     
    
    DorR_data = Data(DorR, catalog) 
    final_file = DorR_data.file_name
    
    if 'cmass' in cat['name'].lower():                          # CMASS -------------------------------

        data_dir = '/mount/riachuelo1/hahn/data/CMASS/' # directory
        if 'fid' in cat['name'].lower(): 
            # note these are .fits files 
            if DorR.lower() == 'data': 
                data_file = 'cmass-dr12v4-N-Reid.dat.fits'
            else: 
                data_file = 'cmass-dr12v4-N-Reid.ran.fits'
        else: 
            raise NotImplementedError('Consider using fiducial cosmology for comparisons to mocks')
        file_name = ''.join([data_dir, data_file])
        data = mrdfits(file_name)   # import data 

        if DorR == 'random': 
            # for random, mask file has to be imported for completeness
            mask_file = ''.join([data_dir, 'mask-cmass-dr12v4-N-Reid.fits']) 
            mask = mrdfits(mask_file) 
            comp = mask.weight[data.ipoly]
            
        zlim = np.where((data.z >= 0.43) & (data.z < 0.75))    # redshift limit
        
        if DorR == 'data': 
            # column order : 'ra', 'dec', 'z', 'nbar', 'wsys', 'wnoz', 'wfc', 'comp'
            np.savetxt(final_file, 
                    np.c_[(data.ra)[zlim], (data.dec)[zlim], (data.z)[zlim], (data.nz)[zlim], 
                        (data.weight_systot)[zlim], (data.weight_noz)[zlim], (data.weight_cp)[zlim], 
                        (data.comp)[zlim]
                        ], 
                    fmt=['%10.5f', '%10.5f', '%10.5f', '%.5e', 
                        '%10.5f', '%10.5f', '%10.5f', '%10.5f'], 
                    delimiter='\t', 
                    header="column order : ra, dec, z, nbar, wsys, wnoz, wfc, comp") 
        else: 
            # column order : 'ra', 'dec', 'z', 'nbar', 'comp'
            np.savetxt(final_file, 
                    np.c_[
                        (data.ra)[zlim], (data.dec)[zlim], (data.z)[zlim], (data.nz)[zlim], comp[zlim]
                        ],
                    fmt=['%10.5f', '%10.5f', '%10.5f', '%.5e', '%10.5f'], 
                    delimiter='\t', 
                    header="column order : ra, dec, z, nbar, comp") 

    elif cat['name'].lower() == 'patchy': 
        pass

    return None 
