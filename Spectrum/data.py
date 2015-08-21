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
        cat = cat_corr['catalog'] 
        if 'correction' in catalog.keys(): 
            corr = cat_corr['correction'] 

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
            self.file_name = self.file(**kwargs)           # File name of data 
    
        self.cosmo = None
        if 'cosmo' in kwargs.keys():    # set Cosmology
            self.cosmo = kwargs['cosmo']

    def file(self, **kwargs): 
        ''' Function to get file name of Data class using catalog dictionary. Only default mock 
        catalogs included. See notes.

        Parameters
        ----------
        DorR : data or random
        catalog : catalog dictionary 

        Notes 
        -----
        * If catalog dictionary is not included, returns None. 

        '''
        cat = self.catalog['catalog']
        if 'correction' in catalog.keys(): 
            corr = self.catalog['correction'] 
        else: 
            corr = {'name': 'default'} 
        DorR = self.Type
    
        if catalog['name'].lower() == 'lasdamasgeo':                # LasDamasGeo --------------
            data_dir = '/mount/riachuelo1/hahn/data/LasDamas/Geo/'

            if DorR.lower() == 'data':                          # data
                if correction['name'].lower() == 'default':
                    file_name = ''.join([data_dir, 
                        'sdssmock_gamma_lrgFull_zm_oriana', 
                        str("%02d" % catalog['n_mock']), catalog['letter'], '_no.rdcz.dat']) 
                else: 
                    return None 
            if DorR.lower() == 'random':                        # random 
                file_name = '/mount/riachuelo1/hahn/data/LasDamas/Geo/sdssmock_gamma_lrgFull.rand_200x_no.rdcz.dat'
    
        elif catalog['name'].lower() == 'tilingmock':               # Tiling Mock ---------------
            data_dir = '/mount/riachuelo1/hahn/data/tiling_mocks/'      # data directory
           
           if DorR.lower() == 'data': 
                if correction['name'].lower() == 'default': 
                    # all weights = 1 (fibercollisions *not* imposed) 
                    file_name = ''.join([data_dir,
                        'cmass-boss5003sector-icoll012.zlim.dat']) 
                else: 
                    return None
            elif DorR.lower() == 'random':      # Randoms 
                file_name = ''.join([data_dir, 
                    'randoms-boss5003-icoll012-vetoed.zlim.dat']) 

        elif catalog['name'].lower() == 'qpm':                      # QPM -------------------- 
            data_dir = '/mount/riachuelo1/hahn/data/QPM/dr12d/'              
            if DorR == 'data':                                  # data  
                if correction['name'].lower() == 'default': 
                    file_name = ''.join([data_dir, 
                        'a0.6452_', str("%04d" % catalog['n_mock']), 
                        '.dr12d_cmass_ngc.vetoed.dat']) 
                else: 
                    return None 
            elif DorR == 'random':                              # Random 
                file_name = ''.join([data_dir, 
                    'a0.6452_rand50x.dr12d_cmass_ngc.vetoed.dat']) 

        elif catalog['name'].lower() == 'patchy':               # PATHCY mocks -------------
            data_dir = '/mount/riachuelo1/hahn/data/PATCHY/dr12/v6c/'   # data directory

            if DorR.lower() == 'data':                  # Data catalogs  
                if correction['name'].lower() == 'default': 
                    # true mocks
                    file_name = ''.join([data_dir, 
                        'Patchy-Mocks-DR12CMASS-N-V6C-Portsmouth-mass_', 
                        str("%04d" % catalog['n_mock']), '.vetoed.dat']) 
                else: 
                    return None
            elif DorR == 'random':                      # Random catalog 
                file_name = ''.join([data_dir, 'Random-DR12CMASS-N-V6C-x50.vetoed.dat'])
    
        elif catalog['name'].lower() == 'nseries':              # N-series ------------------
            data_dir = '/mount/riachuelo1/hahn/data/Nseries/'
        
            if DorR == 'data':                          # mock catalogs 
                if correction['name'].lower() in ('default'): 
                    file_name = ''.join([data_dir, 
                        'CutskyN', str(catalog['n_mock']), '.dat']) 
                elif correction['name'].lower() in ('original'):    # original mock
                    file_name = ''.join([data_dir, 
                        'CutskyN', str(catalog['n_mock']), '.rdzwc']) 
                elif correction['name'].lower() in ('wcompfile'):   # wcomp file 
                    file_name = ''.join([data_dir, 
                        'CutskyN', str(catalog['n_mock']), '.mask_info']) 
                else: 
                    return None

            elif DorR == 'random':                      # random catalog 
                file_name = ''.join([data_dir, 'Nseries_cutsky_randoms_50x_redshifts_comp.dat']) 
    
        elif 'bigmd' in catalog['name'].lower():                # Big MD ---------------------
            data_dir = '/mount/riachuelo1/hahn/data/BigMD/'
        
            if DorR == 'data':  # mock catalogs 
                if correction['name'].lower() == 'default':    # true mocks
                    if catalog['name'].lower() == 'bigmd': 
                        file_name = ''.join([data_dir, 
                            'bigMD-cmass-dr12v4_vetoed.dat']) # hardcoded
                    elif catalog['name'].lower() == 'bigmd1': 
                        file_name = ''.join([data_dir, 
                            'bigMD-cmass-dr12v4-RST-standardHAM_vetoed.dat']) # hardcoded
                    elif catalog['name'].lower() == 'bigmd2': 
                        file_name = ''.join([data_dir, 
                            'bigMD-cmass-dr12v4-RST-quadru_vetoed.dat']) # hardcoded
                    elif catalog['name'].lower() == 'bigmd3':   
                        # "best" bigMD August 3, 2015 
                        file_name = ''.join([data_dir, 
                            'BigMD-cmass-dr12v4-RST-standHAM-Vpeak_vetoed.dat']) 
                    else: 
                        raise NotImplementedError('asdfkj')
                else: 
                    return None
    
            elif DorR == 'random':                  # random catalog 
                # vetomask-ed random catalog 
                if catalog['name'].lower() == 'bigmd': 
                    file_name = ''.join([data_dir, 'bigMD-cmass-dr12v4_vetoed.ran'])
                elif catalog['name'].lower() == 'bigmd1': 
                    file_name = ''.join([data_dir, 'bigMD-cmass-dr12v4-RST-standardHAM_vetoed.ran'])
                elif catalog['name'].lower() == 'bigmd2': 
                    file_name = ''.join([data_dir, 'bigMD-cmass-dr12v4-RST-quadru_vetoed.ran'])
                elif catalog['name'].lower() == 'bigmd3': 
                    file_name = ''.join([data_dir, 'BigMD-cmass-dr12v4-RST-standHAM-Vpeak_vetoed.ran']) 
                else: 
                    return None 
    
        elif catalog['name'].lower() == 'cmass':                # CMASS ---------------------
            data_dir = '/mount/riachuelo1/hahn/data/CMASS/'
        
            if DorR == 'data':                      # mock catalogs 
                if correction['name'].lower() in ('default'): 
                    file_name = ''.join([data_dir, 'cmass-dr12v4-N-Reid.dat']) # hardcoded
                else: 
                    return None
            elif DorR == 'random':                  # random catalog 
                file_name = ''.join([data_dir, 'cmass-dr12v4-N-Reid.ran.dat'])
        else: 
            return None 

        return file_name

    def Read(self, **kwargs):
        ''' Read in data file 

        '''
        DorR = self.Type        # Data or Random
        
        # Catalog dictionary 
        cat = self.catalog['catalog'] 
        if 'correction' in catalog.keys(): 
            corr = self.catalog['correction'] 
        else: 
            corr = {'name': 'default'} 
        '''
        if cat['name'].lower() == 'lasdamasgeo':    # LasDamas Geo -----------------------

            if DorR == 'data':                      # Data -------------------------
                # columns that this catalog data will have  
                catalog_columns = ['ra', 'dec', 'z', 'weight']  

                self.columns = catalog_columns

                # read data (ra, dec, z, weights) 
                file_data = np.loadtxt(file_name, unpack=True, usecols=[0,1,2,3])         

                for i_col, catalog_column in enumerate(catalog_columns): 
                    column_data = file_data[i_col]
                    setattr(self, catalog_column, column_data) 

            elif DorR.lower() == 'random':          # Random  -------------------------
                # columns of random catalog (NOTE CZ IS CONVERTED TO Z) 
                catalog_columns = ['ra', 'dec', 'z']        

                self.columns = catalog_columns
                
                if 'down_nz' in correction['name'].lower(): 
                    # true rnadom catalog downsampled by nbar(z) 
                    build_ldg_nz_down('random', **cat_corr)
                    
                    # Read data 
                    file_data = np.loadtxt(file_name, unpack=True, usecols=[0,1,2])         

                    for i_col, catalog_column in enumerate(catalog_columns): 
                        column_data = file_data[i_col]
                        # assign to class
                        setattr(self, catalog_column, column_data)

                else: 
                    # Read data 
                    file_data = np.loadtxt(file_name, unpack=True, usecols=[0,1,2])         

                    for i_col, catalog_column in enumerate(catalog_columns): 
                        if catalog_column == 'z': 
                            column_data = file_data[i_col]/299800.0
                        else: 
                            column_data = file_data[i_col]
                        # assign to class
                        setattr(self, catalog_column, column_data)
        
        elif catalog['name'].lower() == 'ldgdownnz':    # LasDamasGeo downsampled ------------ 
            if DorR == 'data':                          # Data -------------------------
                # columns that this catalog data will have  
                catalog_columns = ['ra', 'dec', 'z', 'weight']  

                self.columns = catalog_columns

                # read data (ra, dec, z, weights) 
                file_data = np.loadtxt(file_name, unpack=True, usecols=[0,1,2,3])         

                for i_col, catalog_column in enumerate(catalog_columns): 
                    column_data = file_data[i_col]
                    setattr(self, catalog_column, column_data) 

            elif DorR.lower() == 'random':          # Random Catalogs -------------------------

                # columns of random catalog (NOTE CZ IS CONVERTED TO Z) 
                catalog_columns = ['ra', 'dec', 'z']        

                self.columns = catalog_columns
                
                # Read data 
                file_data = np.loadtxt(file_name, unpack=True, usecols=[0,1,2])         

                for i_col, catalog_column in enumerate(catalog_columns): 
                    column_data = file_data[i_col]
                    # assign to class
                    setattr(self, catalog_column, column_data)

        elif catalog['name'].lower() == 'tilingmock':       # Tiling Mock ----------------------
            omega_m = 0.274         # survey cosmology 

            if DorR == 'data':              # for mocks 
                catalog_columns = ['ra', 'dec', 'z', 'weight']       # columns that this catalog data will have  
                self.columns = catalog_columns

                if (os.path.isfile(file_name) == False) or (clobber == True): # if file does not exists, make file  
                    print 'Constructing ', file_name 

                    if correction['name'].lower() == 'true':    # true mocks
                        # all weights = 1 (fibercollisions *not* imposed) 
                        build_true(**cat_corr) 
                
                    elif correction['name'].lower() in ('upweight', 'fibcol', 'shotnoise', 'floriansn', 'hectorsn'):
                        # upweighted mocks
                        build_fibercollided(**cat_corr)         # build-in fibercollisions using spherematch idl code
                
                    elif correction['name'].lower() in ('peak', 'peaknbar', 'peaktest', 'peakshot'): 
                        # Correction methods that have both peak and tail contributions   
                        # peak/peaknbar = peak + tail correction 
                        # peaktest = fpeak peak correction + remove rest 
                        # peakshot = fpeak peak correction + shot noise for rest
                        build_peakcorrected_fibcol(sanitycheck=True, **cat_corr)
                
                    elif correction['name'].lower() in ('allpeak', 'allpeakshot'):
                        # all peak corrected 
                        build_peakcorrected_fibcol(sanitycheck=True, **cat_corr)

                # Read data  
                file_data = np.loadtxt(file_name, unpack=True, usecols=[0,1,2,3])         # ra, dec, z, weight

                # assign to data columns class
                for i_col, catalog_column in enumerate(catalog_columns): 
                    column_data = file_data[i_col]
                    # assign to class
                    setattr(self, catalog_column, column_data) 

            elif DorR.lower() == 'random':              # Randoms -----------------------------------------------------

                catalog_columns = ['ra', 'dec', 'z']        # columns of catalog 
                self.columns = catalog_columns

                if (os.path.isfile(file_name) == False) or (clobber == True): # if file does not exists, make file  
                    print 'Constructing ', file_name
                    build_corrected_randoms(sanitycheck=False, **cat_corr)       # impose redshift limit

                print 'Reading ', file_name                     # just because it takes forever
                t0 = time.time() 
                file_data = np.loadtxt(file_name, unpack=True, usecols=[0,1,2])      # read random file
                print 'took ', (time.time()-t0)/60.0, ' mins'       # print time 

                for i_col, catalog_column in enumerate(catalog_columns): 
                    column_data = file_data[i_col]
                    # assign data column to class
                    setattr(self, catalog_column, column_data)
                
        elif catalog['name'].lower() == 'qpm':                      # QPM --------------------
            omega_m = 0.31  # survey cosmology 

            if DorR == 'data':                  # Data ------------------------------
                # catalog columns 
                catalog_columns = ['ra', 'dec', 'z', 'wfc', 'comp'] 
                self.columns = catalog_columns

                if (os.path.isfile(file_name) == False) or (clobber == True):
                    # File does not exist or Clobber = True!

                    print 'Constructing ', file_name 
                    if correction['name'].lower() == 'true':                    
                        # true mocks 
                        # all weights = 1 (fibercollisions *not* imposed) 
                        build_true(**cat_corr) 

                    elif correction['name'].lower() in ('upweight', 'shotnoise', 'floriansn', 'hectorsn'): 
                        # upweighted mocks
                        build_fibercollided(**cat_corr) 

                    elif correction['name'].lower() in ('peaknbar', 'peakshot'): 
                        # peak corrected mocks 
                        build_peakcorrected_fibcol(doublecheck=True, **cat_corr)  # build peak corrected file 

                    elif correction['name'].lower() in ('peakshot_dnn'):
                        # peak + dLOS env correct mocks 
                        build_peak_fpeak_dNN(NN=correction['NN'], **cat_corr) 

                    elif correction['name'].lower() in ('tailupw'):         
                        # tail upweight correction 
                        build_tailupweight_fibcol(**cat_corr)  # build peak corrected file 

                    elif correction['name'].lower() in ('noweight'): 
                        # n oweight 
                        build_noweight(**cat_corr) 
                    else: 
                        raise NotImplementedError() 

                file_data = np.loadtxt(file_name, unpack=True, usecols=[0,1,2,3,4])   # ra, dec, z, wfc, comp

                # assign to data columns class
                for i_col, catalog_column in enumerate(catalog_columns): 
                    setattr(self, catalog_column, file_data[i_col]) 
            
            elif DorR == 'random':              # Random ------------------------------------

                catalog_columns = ['ra', 'dec', 'z', 'comp']    # catalog columns 

                if (os.path.isfile(file_name) == False) or (clobber == True):
                    print 'Constructing ', file_name 
                    build_random(**cat_corr) 

                file_data = np.loadtxt(file_name, unpack=True, usecols=[0,1,2,3])   # ra, dec, z, comp 

                # assign to object data columns
                for i_col, catalog_column in enumerate(catalog_columns): 
                    setattr(self, catalog_column, file_data[i_col])
        
        elif catalog['name'].lower() == 'nseries':                  # N-series ----------------
            try: 
                if catalog['cosmology'] == 'fiducial': 
                    omega_m = 0.31 # fiducial cosmology  
                else: 
                    omega_m = 0.286  # survey cosmology 

            except KeyError: 
                omega_m = 0.31 # fiducial cosmology  

            if DorR == 'data':                          # Data ------------------------------
                # catalog columns 
                # ra, dec, z, wfc, comp
                catalog_columns = ['ra', 'dec', 'z', 'wfc', 'comp'] 
                self.columns = catalog_columns
                column_indices = [0,1,2,3,4]
                dtypes = None

                if not os.path.isfile(file_name) or clobber:
                    # File does not exist or Clobber = True!
                    print 'Constructing ', file_name 

                    if correction['name'].lower() == 'true':                    
                        # true mocks 
                        # all weights = 1 (fibercollisions *not* imposed) 
                        build_true(**cat_corr) 

                    elif correction['name'].lower() in (
                            'upweight', 'shotnoise', 'floriansn', 'hectorsn'): 
                        # upweighted mocks
                        build_fibercollided(**cat_corr) 

                    elif correction['name'].lower() in ('peaknbar', 'peakshot'): 
                        # peak corrected mocks 
                        build_peakcorrected_fibcol(doublecheck=True, **cat_corr)  # build peak corrected file 
                        #elif correction['name'].lower() in ('noweight'): 
                        #    # n oweight 
                        #    build_noweight(**cat_corr) 
                    elif 'scratch' in correction['name'].lower():           
                        # scratch pad for different methods 
                        build_nseries_scratch(**cat_corr) 
                    elif correction['name'].lower() == 'photoz': 
                        # photoz assigned fiber collided mock 
                        photoz.build_fibcol_assign_photoz(qaplot=False, **cat_corr) 
                    elif correction['name'].lower() == 'photozpeakshot': 
                        # Peak Shot correction using photometric redshift information
                        build_photoz_peakcorrected_fibcol(doublecheck=True, **cat_corr)
                    else: 
                        raise NotImplementedError() 

                if 'photoz' in correction['name'].lower(): 
                    # corrections to column assignment for methods involve photometry
                    catalog_columns = ['ra', 'dec', 'z', 'wfc', 'comp', 
                            'zupw', 'upw_index', 'z_photo'] 
                    self.columns = catalog_columns
                    column_indices = [0,1,2,3,4,5,6,7]
                    dtypes = {
                            'names': ('ra', 'dec', 'z', 
                                'wfc', 'comp', 'zupw', 'upw_index', 'z_photo'), 
                            'formats': (np.float, np.float, np.float, 
                                np.float, np.float, np.float, np.int, np.float)
                            }

                file_data = np.loadtxt(file_name, 
                        unpack=True, usecols=column_indices, dtype=dtypes)         

                # assign to data columns class
                for i_col, catalog_column in enumerate(catalog_columns): 
                    setattr(self, catalog_column, file_data[i_col]) 
            
            elif DorR == 'random':              # Random ------------------------------------

                catalog_columns = ['ra', 'dec', 'z', 'comp']    # catalog columns 
                
                if not os.path.isfile(file_name) or clobber:
                    print 'Constructing ', file_name 
                    build_random(**cat_corr) 

                file_data = np.loadtxt(file_name, unpack=True, usecols=[0,1,2,3])   # ra, dec, z, comp

                # assign to object data columns
                for i_col, catalog_column in enumerate(catalog_columns): 
                    setattr(self, catalog_column, file_data[i_col])

        elif catalog['name'].lower() == 'patchy':                   # PATCHY ------------------
            omega_m = 0.31              # survey cosmology 

            if DorR == 'data':                      
                # mocks ------------------------------------------------------

                catalog_columns = ['ra', 'dec', 'z', 'nbar', 'wfc']         # catalog columns 
                self.columns = catalog_columns

                if (os.path.isfile(file_name) == False) or (clobber == True):
                    # File does not exist or Clobber = True!
                    print 'Constructing ', file_name 

                    if correction['name'].lower() == 'true': 
                        # true mocks 
                        build_true(**cat_corr) 

                    elif correction['name'].lower() in ('upweight', 'shotnoise', 
                            'floriansn', 'hectorsn'): 
                        # upweighted mocks
                        build_fibercollided(**cat_corr) 

                    elif correction['name'].lower() in ('peaknbar', 'peakshot'): 
                        # peak corrected mocks 
                        build_peakcorrected_fibcol(**cat_corr)  # build peak corrected file 

                file_data = np.loadtxt(file_name, unpack=True, usecols=[0,1,2,3,4])

                # assign to data columns class
                for i_col, catalog_column in enumerate(catalog_columns): 
                    setattr(self, catalog_column, file_data[i_col]) 
            
            elif DorR == 'random':
                # Random ---------------------------------------------------

                catalog_columns = ['ra', 'dec', 'z', 'nbar']    # catalog columns 

                if (os.path.isfile(file_name) == False) or (clobber == True):
                    print 'Constructing ', file_name 
                    build_random(**cat_corr) 

                file_data = np.loadtxt(file_name, unpack=True, usecols=[0,1,2,3])   # ra, dec, z, nbar

                for i_col, catalog_column in enumerate(catalog_columns):    
                    # assign to object data columns
                    setattr(self, catalog_column, file_data[i_col])
    
        elif 'bigmd' in catalog['name'].lower():              # Big MultiDark ----------------
            try: 
                if catalog['cosmology'] == 'fiducial': 
                    omega_m = 0.31      # (fiducial cosmology) 
                else:
                    raise NotImplementedError('Cosmology Type is not Implemented Yet') 

            except KeyError: 
                catalog['cosmology'] = 'fiducial'
                omega_m = 0.31      # (fiducial cosmology) 

            if DorR == 'data':                          # Data ------------------------------
                # catalog columns 
                catalog_columns = ['ra', 'dec', 'z', 'nbar', 'wfc'] 
                self.columns = catalog_columns

                if not os.path.isfile(file_name) or clobber:
                    # File does not exist or Clobber = True!
                    print 'Constructing ', file_name 

                    if correction['name'].lower() == 'true':  
                        # true mocks 
                        # all weights = 1 (fibercollisions *not* imposed) 
                        build_true(**cat_corr) 

                    elif correction['name'].lower() in ('upweight'): 
                        # upweighted mocks
                        build_fibercollided(**cat_corr) 

                    elif correction['name'].lower() in ('peakshot'): 
                        # peak corrected
                        build_peakcorrected_fibcol(doublecheck=True, **cat_corr)

                    else: 
                        raise NotImplementedError() 

                # ra, dec, z, nbar, wfc
                file_data = np.loadtxt(file_name, unpack=True, usecols=[0,1,2,3,4])

                # assign to data columns class
                for i_col, catalog_column in enumerate(catalog_columns): 
                    setattr(self, catalog_column, file_data[i_col]) 
            
            elif DorR == 'random':              # Random ------------------------------------
                catalog_columns = ['ra', 'dec', 'z']    # catalog columns 
                
                if not os.path.isfile(file_name) or clobber:
                    print 'Constructing ', file_name 
                    build_random(**cat_corr) 

                file_data = np.loadtxt(file_name, unpack=True, usecols=[0,1,2])   # ra, dec, z, comp

                # assign to object data columns
                for i_col, catalog_column in enumerate(catalog_columns): 
                    setattr(self, catalog_column, file_data[i_col])

        elif catalog['name'].lower() == 'cmass':                    # CMASS -----------------
            try: 
                if catalog['cosmology'] == 'fiducial': 
                    # Firm shift in cosmology use to OmegaM = 0.31 in WG 
                    omega_m = 0.31      # (fiducial cosmology) 
                else:
                    raise NotImplementedError('You should use fiducial cosmology') 

            except KeyError: 
                catalog['cosmology'] = 'fiducial'
                omega_m = 0.31      # (fiducial cosmology) 

            if DorR == 'data':              # data --------------------
                catalog_columns = ['ra', 'dec', 'z', 'wsys', 'wnoz', 'wfc', 'comp']
                self.columns = catalog_columns
                
                if not os.path.isfile(file_name) or clobber:
                    # File does not exist or Clobber = True!
                    print 'Constructing ', file_name 
                    
                    if correction['name'].lower() in ('upweight'): 
                        # upweighted
                        build_fibercollided(**cat_corr) 
                    elif correction['name'].lower() in ('peakshot'): 
                        # peak correction  
                        build_peakcorrected_fibcol(doublecheck=True, **cat_corr) 
                    else: 
                        raise NotImplementedError('Only upweight works for now') 

                #ra,dec,z,wsys,wnoz,wfc,nbar,comp
                file_data = np.loadtxt(file_name, unpack=True, usecols=[0,1,2,3,4,5,6])   

                # assign to data columns class
                for i_col, catalog_column in enumerate(catalog_columns): 
                    setattr(self, catalog_column, file_data[i_col]) 

            elif DorR == 'random': 
                catalog_columns = ['ra', 'dec', 'z', 'comp']
                self.columns = catalog_columns
                
                if not os.path.isfile(file_name) or clobber: 
                    print 'Constructing ', file_name 
                    build_random(**cat_corr) 

                #ra,dec,z,nbar,comp
                file_data = np.loadtxt(file_name, unpack=True, usecols=[0,1,2,3])  

                # assign to data columns class
                for i_col, catalog_column in enumerate(catalog_columns): 
                    setattr(self, catalog_column, file_data[i_col]) 

        else: 
            raise NameError('not yet coded') 
        '''

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
        if cat['name'].lower() in ('lasdamasgeo', 'ldgdownnz'): 
            # LasDamas Catalog with SDSS Geometry 
            omega_m = 0.25  
        elif cat['name'].lower() in ('nseries'): 
            omega_m = 0.31 
        else: 
            raise NotImplementedError('Not yet included') 
        
        # survey cosmology  
        cosmo = {} 
        cosmo['omega_M_0'] = omega_m 
        cosmo['omega_lambda_0'] = 1.0 - omega_m 
        cosmo['h'] = 0.676
        cosmo = cosmos.distance.set_omega_k_0(cosmo) 
        self.cosmo = cosmo 
