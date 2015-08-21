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
    type : 'fft', 'power', 'bisp'
    catalog : catalog dictionary 

    '''
    cat = catalog['catalog']
    corr = 
    spec = 
    catalog = cat_corr['catalog']
    correction = cat_corr['correction']
    spec = cat_corr['spec']
    
    if catalog['name'].lower() == 'lasdamasgeo':            # LasDamasGeo ----------------------
        ldg_code_dir = '/home/users/hahn/powercode/FiberCollisions/LasDamas/Geo/' 
       
        if fft_power.lower() == 'fft':                      # FFT -----------------
    
            if correction['name'].lower() == 'floriansn':     # Beutler+2014
                f_code = ldg_code_dir+'FFT_ldg_fkp_w_florian_'+str(spec['grid'])+'grid.f'
            elif correction['name'].lower() == 'hectorsn':  # Gil-Marin+2014
                f_code = ldg_code_dir+'FFT_ldg_fkp_w_hector_'+str(spec['grid'])+'grid.f'
            else: 
                f_code = ldg_code_dir+'FFT_ldg_fkp_w_'+str(spec['grid'])+'grid.f'

        elif fft_power.lower() == 'power':                  # power ----------------

            if correction['name'].lower() in ('true', 'upweight', 'peaknbar', 'bigfc'):  
                # FKP estimator
                if spec['grid'] == 360: 
                    f_code = ldg_code_dir+'power_ldg_fkp_360grid_180bin.f'
                elif spec['grid'] == 960: 
                    f_code = ldg_code_dir+'power_ldg_fkp_960grid_480bin.f'

            elif correction['name'].lower() in ('peakshot', 'allpeakshot', 'noweight', 
                    'shotnoise', 'vlospeakshot', 'floriansn', 'hectorsn', 'peakshot_dnn', 
                    'bigfc_peakshot'): 
                # Igal+Irand shot noise incorporated
                if spec['grid'] == 360: 
                    f_code = ldg_code_dir+'power_ldg_fkp_Igal_Iran_360grid_180bin.f'
                elif spec['grid'] == 960: 
                    f_code = ldg_code_dir+'power_ldg_fkp_Igal_Iran_960grid_480bin.f'
            else: 
                raise NameError('what?')
    
        # quadrupole codes ------------------------------------------------
        elif fft_power.lower() == 'quadfft': 
            code_dir = '/home/users/hahn/powercode/FiberCollisions/' 
            f_code = code_dir+'FFT_FKP_BOSS_cic_il4_v3.f' 
        elif fft_power.lower() == 'quadpower': 
            
            code_dir = '/home/users/hahn/powercode/FiberCollisions/' 
            f_code = code_dir+'power_FKP_SDSS_BOSS_v3.f'
        else: 
            raise NameError('asdflkajsdf') 
    
    elif catalog['name'].lower() == 'ldgdownnz':            # LasDamasGeo downsampled ---------
        ldg_code_dir = '/home/users/hahn/powercode/FiberCollisions/LasDamas/Geo/' 
       
        if fft_power.lower() == 'fft':      # FFT -----------------
            # only one implemented so far 
            f_code = ldg_code_dir+'FFT_ldg_fkp_w_down_nz_'+str(spec['grid'])+'grid.f'

        elif fft_power.lower() == 'power':  # power ----------------

            if correction['name'].lower() in ('true', 'upweight', 'peaknbar', 'bigfc'):  
                # Original FKP estimator
                if spec['grid'] == 360: 
                    f_code = ldg_code_dir+'power_ldg_fkp_360grid_180bin.f'
                elif spec['grid'] == 960: 
                    f_code = ldg_code_dir+'power_ldg_fkp_960grid_480bin.f'

            elif correction['name'].lower() in ('peakshot', 'bigfc_peakshot'): 
                # Igal+Irand shot noise incorporated
                if spec['grid'] == 360: 
                    f_code = ldg_code_dir+'power_ldg_fkp_Igal_Iran_360grid_180bin.f'
                elif spec['grid'] == 960: 
                    f_code = ldg_code_dir+'power_ldg_fkp_Igal_Iran_960grid_480bin.f'

            else: 
                raise NotImplementedError('what?')

        elif fft_power.lower() == 'quadfft':  # Quadrupole FFT
            code_dir = '/home/users/hahn/powercode/FiberCollisions/' 
            f_code = code_dir+'FFT_FKP_BOSS_cic_il4_v3.f' 

        elif fft_power.lower() == 'quadpower': # Quadrupole power
            code_dir = '/home/users/hahn/powercode/FiberCollisions/' 
            f_code = code_dir+'power_FKP_SDSS_BOSS_v3.f'

        else: 
            raise NameError('asdflkajsdf') 
    
    elif catalog['name'].lower() == 'tilingmock':               # Tiling Mock ----------------
        code_dir = '/home/users/hahn/powercode/FiberCollisions/TilingMock/'
    
        if fft_power.lower() == 'fft':
            if correction['name'].lower() == 'floriansn': 
                f_code = code_dir+'FFT-fkp-tm-w-nbar-florian-'+str(spec['grid'])+'grid.f'
            elif correction['name'].lower() == 'hectorsn': 
                f_code = code_dir+'FFT-fkp-tm-w-nbar-hector-'+str(spec['grid'])+'grid.f'
            else: 
                f_code = code_dir+'FFT-fkp-tm-w-nbar-'+str(spec['grid'])+'grid.f'

        elif fft_power.lower() == 'power': 
            if correction['name'].lower() in ('peakshot', 'allpeakshot', 'shotnoise', 'floriansn', 'hectorsn', 'vlospeakshot', 'peakshot_dnn'):
                if spec['grid'] == 360: 
                    f_code = code_dir+'power-fkp-tm-w-nbar-Igal-Irand-360grid-180bin.f'
                elif spec['grid'] == 960: 
                    f_code = code_dir+'power-fkp-tm-w-nbar-Igal-Irand-960grid-480bin.f'
            else: 
                if spec['grid'] ==360: 
                    f_code = code_dir+'power-fkp-tm-w-nbar-360grid-180bin.f'
                elif spec['grid'] == 960:
                    f_code = code_dir+'power-fkp-tm-w-nbar-960grid-480bin.f'

        elif fft_power.lower() == 'quadfft': 
            code_dir = '/home/users/hahn/powercode/FiberCollisions/' 
            f_code = code_dir+'FFT_FKP_BOSS_cic_il4_v3.f' 
        elif fft_power.lower() == 'quadpower': 
            code_dir = '/home/users/hahn/powercode/FiberCollisions/' 
            f_code = code_dir+'power_FKP_SDSS_BOSS_v3.f'
        else: 
            raise NameError('asdlkfjalksdjfklasjf')

    elif catalog['name'].lower() == 'qpm':                  # QPM -----------------------
        code_dir = '/home/users/hahn/powercode/FiberCollisions/QPM/dr12d/'
        
        if fft_power.lower() == 'fft': 
            # FFT code
            if correction['name'].lower() == 'floriansn': 
                f_code = code_dir+'FFT-qpm-fkp-w-nbar-florian-'+str(spec['grid'])+'grid.f'
            elif correction['name'].lower() == 'hectorsn': 
                f_code = code_dir+'FFT-qpm-fkp-w-nbar-hector-'+str(spec['grid'])+'grid.f'
            else: 
                f_code = code_dir+'FFT-qpm-fkp-w-nbar-'+str(spec['grid'])+'grid.f'
    
        elif fft_power.lower() == 'power': 
            if correction['name'].lower() in ('true', 'upweight', 'peaknbar'):
                # normal FKP shot noise correction
                if spec['grid'] == 360: 
                    f_code = code_dir+'power-qpm-fkp-w-nbar-360grid-180bin.f'
                elif spec['grid'] == 960: 
                    f_code = code_dir+'power-qpm-fkp-w-nbar-960grid-480bin.f'

            elif correction['name'].lower() in \
                    ('peakshot', 'shotnoise', 'floriansn', 'noweight', 
                            'hectorsn', 'vlospeakshot', 'peakshot_dnn'): 
                if spec['grid'] == 360: 
                    # Igal Irand shot noise correction 
                    f_code = code_dir+'power-qpm-fkp-w-nbar-Igal-Irand-360grid-180bin.f'
                elif spec['grid'] == 960: 
                    # Igal Irand shot noise correction 
                    f_code = code_dir+'power-qpm-fkp-w-nbar-Igal-Irand-960grid-480bin.f'

        # quadrupole codes --------------------------------------------
        # regardess of catalog or correction TEMPORARILY HARDCODED HERE FOR TEST RUN 
        elif fft_power.lower() == 'quadfft': 
            code_dir = '/home/users/hahn/powercode/FiberCollisions/' 
            f_code = code_dir+'FFT_FKP_BOSS_cic_il4_v3.f' 
        elif fft_power.lower() == 'quadpower': 
            code_dir = '/home/users/hahn/powercode/FiberCollisions/' 
            f_code = code_dir+'power_FKP_SDSS_BOSS_v3.f'
        else: 
            raise NameError("not Yet coded") 
    
    elif catalog['name'].lower() == 'nseries':              # N series ------------------
        code_dir = 'Nseries/'   # directory
        
        if fft_power.lower() == 'fft':          # FFT code
            if correction['name'].lower() == 'floriansn': 
                code_file = 'FFT-nseries-fkp-w-nbar-florian-'+str(spec['grid'])+'grid.f'
            elif correction['name'].lower() == 'hectorsn': 
                code_file = 'FFT-nseries-fkp-w-nbar-hector-'+str(spec['grid'])+'grid.f'
            else: 
                code_file = 'FFT-nseries-fkp-w-nbar-'+str(spec['grid'])+'grid.f'
    
        elif fft_power.lower() == 'power':      # power code
            if correction['name'].lower() in ('true', 'upweight', 'peaknbar'):
                # normal FKP shot noise correction
                if spec['grid'] == 360: 
                    code_file = 'power-nseries-fkp-w-nbar-360grid-180bin.f'
                elif spec['grid'] == 960: 
                    code_file = 'power-nseries-fkp-w-nbar-960grid-480bin.f'
            elif correction['name'].lower() in \
                    ('peakshot', 'photozpeakshot', 'shotnoise', 'floriansn', 
                            'noweight', 'hectorsn', 'peakshot_dnn'): 
                # FKP with Igal Irand shot noise correction 
                if spec['grid'] == 360: 
                    code_file = 'power-nseries-fkp-w-nbar-Igal-Irand-360grid-180bin.f'
                elif spec['grid'] == 960: 
                    code_file = 'power-nseries-fkp-w-nbar-Igal-Irand-960grid-480bin.f'
            elif 'scratch' in correction['name'].lower(): 
                # FKP with Igal Irand shot noise correction (for scratch pad corrections) 
                if spec['grid'] == 360: 
                    code_file = 'power-nseries-fkp-w-nbar-Igal-Irand-360grid-180bin.f'
                elif spec['grid'] == 960: 
                    code_file = 'power-nseries-fkp-w-nbar-Igal-Irand-960grid-480bin.f'
            else: 
                raise NameError('asldkfjasdf') 

        # quadrupole codes --------------------------------------------
        # regardess of catalog or correction TEMPORARILY HARDCODED HERE FOR TEST RUN 
        elif fft_power.lower() == 'quadfft': 
            code_dir = '/home/users/hahn/powercode/FiberCollisions/' 
            code_file = 'FFT_FKP_BOSS_cic_il4_v3.f' 
        elif fft_power.lower() == 'quadpower': 
            code_dir = '/home/users/hahn/powercode/FiberCollisions/' 
            code_file = 'power_FKP_SDSS_BOSS_v3.f'
        else: 
            raise NameError("not Yet coded") 
        
        f_code = ''.join([code_dir, code_file]) 

    elif catalog['name'].lower() == 'patchy':               # PATCHY --------------------
        code_dir = '/home/users/hahn/powercode/FiberCollisions/PATCHY/dr12/v6c/'
        
        if fft_power.lower() == 'fft': 
            # FFT code
            if correction['name'].lower() == 'floriansn': 
                f_code = code_dir+'FFT-patchy-fkp-w-nbar-florian-'+str(spec['grid'])+'grid.f'
            elif correction['name'].lower() == 'hectorsn': 
                f_code = code_dir+'FFT-patchy-fkp-w-nbar-hector-'+str(spec['grid'])+'grid.f'
            else: 
                f_code = code_dir+'FFT-patchy-fkp-w-nbar-'+str(spec['grid'])+'grid.f'
    
        elif fft_power.lower() == 'power': 
            if correction['name'].lower() in ('true', 'upweight', 'peaknbar'):
                # normal FKP shot noise correction
                if spec['grid'] == 360: 
                    f_code = code_dir+'power-patchy-fkp-w-nbar-360grid-180bin.f'
                elif spec['grid'] == 960: 
                    pass
                    f_code = code_dir+'power-patchy-fkp-w-nbar-960grid-480bin.f'
            else:
                raise NotImplementedError('not yet implemented')

        # quadrupole codes --------------------------------------------
        # regardess of catalog or correction TEMPORARILY HARDCODED HERE FOR TEST RUN 
        '''
        elif fft_power.lower() == 'quadfft': 
            code_dir = '/home/users/hahn/powercode/FiberCollisions/' 
            f_code = code_dir+'FFT_FKP_BOSS_cic_il4_v3.f' 
        elif fft_power.lower() == 'quadpower': 
            code_dir = '/home/users/hahn/powercode/FiberCollisions/' 
            f_code = code_dir+'power_FKP_SDSS_BOSS_v3.f'
        else: 
            raise NameError("not Yet coded") 
        '''
    
    elif 'bigmd' in catalog['name'].lower():                # Big MD ------------------------
        code_dir = 'BigMD/'
        
        if fft_power.lower() == 'fft':  # FFT
            if correction['name'].lower() == 'floriansn': 
                raise NotImplementedError('asdfklj')
            elif correction['name'].lower() == 'hectorsn': 
                raise NotImplementedError('asdfklj')
            else: 
                f_code = code_dir+'FFT-bigmd-fkp-w-nbar-'+str(spec['grid'])+'grid.f'
    
        elif fft_power.lower() == 'power': 
            if correction['name'].lower() in ('true', 'upweight'):
                # normal FKP shot noise correction
                if spec['grid'] == 360: 
                    f_code = code_dir+'power-bigmd-fkp-w-nbar-360grid-180bin.f'
                elif spec['grid'] == 960: 
                    f_code = code_dir+'power-bigmd-fkp-w-nbar-960grid-480bin.f'
                elif spec['grid'] == 1920: 
                    f_code = code_dir+'power-bigmd-fkp-w-nbar-1920grid-960bin.f'
                else: 
                    raise NotImplementedError('asdfklj')
            else: 
                raise NotImplementedError('asdfklj')

        # quadrupole codes --------------------------------------------
        elif fft_power.lower() == 'quadfft': 
            code_dir = '/home/users/hahn/powercode/FiberCollisions/' 
            f_code = code_dir+'FFT_FKP_BOSS_cic_il4_v3.f' 
        elif fft_power.lower() == 'quadpower': 
            code_dir = '/home/users/hahn/powercode/FiberCollisions/' 
            f_code = code_dir+'power_FKP_SDSS_BOSS_v3.f'
        else: 
            raise NameError("not Yet coded") 
    
    elif catalog['name'].lower() == 'cmass':                # CMASS -------------------------
        code_dir = 'CMASS/'
        
        if fft_power.lower() == 'fft':  # FFT
            if correction['name'].lower() == 'floriansn': 
                raise NotImplementedError('asdfklj')
            elif correction['name'].lower() == 'hectorsn': 
                raise NotImplementedError('asdfklj')
            else: 
                if catalog['cosmology'].lower() == 'fiducial': 
                    f_code = ''.join([code_dir,
                        'FFT-cmass-', str(spec['grid']), 'grid.f']) 
                else: 
                    raise NotImplementedError('just dont do it') 
    
        elif fft_power.lower() == 'power': 
            if correction['name'].lower() in ('upweight'):  
                # normal FKP shot noise correction
                if spec['grid'] == 360: 
                    f_code = ''.join([code_dir, 
                        'power-cmass-360grid-180bin.f'])
                    #'power_cmass_fkp_Igal_360grid_180bin.f'])

                elif spec['grid'] == 960: 
                    f_code = ''.join([code_dir, 
                        'power-cmass-960grid-480bin.f'])
                
                elif spec['grid'] == 1920: 
                    f_code = ''.join([code_dir, 
                        'power-cmass-1920grid-960bin.f'])

                else: 
                    raise NotImplementedError('asdfklj')

            elif correction['name'].lower() in ('peakshot'): 
                # corrected Igal-alpha*Irand FKP shot noise correction
                if spec['grid'] == 360: 
                    f_code = ''.join([code_dir, 
                        'power-cmass-Igal-360grid-180bin.f'])
                    #'power_cmass_fkp_Igal_360grid_180bin.f'])

                elif spec['grid'] == 960: 
                    f_code = ''.join([code_dir, 
                        'power-cmass-Igal-960grid-480bin.f'])
            else: 
                raise NotImplementedError('asdfklj')

        # quadrupole codes --------------------------------------------
        elif fft_power.lower() == 'quadfft': 
            code_dir = '/home/users/hahn/powercode/FiberCollisions/' 
            f_code = code_dir+'FFT_FKP_BOSS_cic_il4_v3.f' 

        elif fft_power.lower() == 'quadpower': 
            code_dir = '/home/users/hahn/powercode/FiberCollisions/' 
            f_code = code_dir+'power_FKP_SDSS_BOSS_v3.f'

        else: 
            raise NameError("not Yet coded") 
    
    else: 
        raise NaemError('Not coded!') 

    return f_code

def fortran_code2exe(code): 
    '''
    get .exe file based on fortran code file name  
    '''
    code_dir = '/'.join(code.split('/')[0:-1])+'/' 
    code_file = code.split('/')[-1]

    fort_exe = code_dir+'exe/'+'.'.join(code_file.rsplit('.')[0:-1])+'.exe'

    return fort_exe

def compile_fortran_code(code): 
    '''
    compiles fortran code (very simple, may not work) 
    '''
    # get executable file 
    fort_exe = fortran_code2exe(code) 

    # compile command
    if code == '/home/users/hahn/powercode/FiberCollisions/FFT_FKP_BOSS_cic_il4_v3.f': 
        compile_cmd = ' '.join(['ifort -fast -o', fort_exe, code, '-L/usr/local/fftw_intel_s/lib -lsrfftw -lsfftw -lm'])
    elif code == '/home/users/hahn/powercode/FiberCollisions/power_FKP_SDSS_BOSS_v3.f': 
        compile_cmd = ' '.join(['ifort -fast -o', fort_exe, code])
    else: 
        compile_cmd = ' '.join(['ifort -O3 -o', fort_exe, code, '-L/usr/local/fftw_intel_s/lib -lsfftw -lsfftw'])
    print compile_cmd

    # call compile command 
    subprocess.call(compile_cmd.split())

def get_fibcoll_dir(file_type, **cat_corr): 
    '''
    get data/FFT/power directories given catalog
    '''
    catalog = cat_corr['catalog']
    correction = cat_corr['correction']

    if file_type.lower() not in ('data', 'fft', 'power'): 
        raise NameError('either data, fft, or power') 

    else: 
        if catalog['name'].lower() in ('lasdamasgeo', 'ldgdownnz'): 
            # Lasdamasgeo -----------------------------------------
            
            if file_type.lower() == 'data': 
                file_dir = '/mount/riachuelo1/hahn/data/LasDamas/Geo/'
            elif file_type.lower() == 'fft': 
                file_dir = '/mount/riachuelo1/hahn/FFT/LasDamas/Geo/'
            else:
                file_dir = '/mount/riachuelo1/hahn/power/LasDamas/Geo/'

        elif catalog['name'].lower() == 'tilingmock': 
            # Tiling mock -------------------------------------------

            if file_type.lower() == 'data': 
                file_dir = '/mount/riachuelo1/hahn/data/tiling_mocks/'
            elif file_type.lower() == 'fft': 
                file_dir = '/mount/riachuelo1/hahn/FFT/tiling_mocks/'
            else:
                file_dir = '/mount/riachuelo1/hahn/power/tiling_mocks/'

        elif catalog['name'].lower() == 'qpm':                          # QPM ---------------------------------------------

            if file_type.lower() == 'data': 
                file_dir = '/mount/riachuelo1/hahn/data/QPM/dr12d/'
            elif file_type.lower() == 'fft': 
                file_dir = '/mount/riachuelo1/hahn/FFT/QPM/dr12d/'
            else:
                file_dir = '/mount/riachuelo1/hahn/power/QPM/dr12d/'

        elif catalog['name'].lower() == 'nseries':                          # N series ---------------------------------------

            if file_type.lower() == 'data': 
                file_dir = '/mount/riachuelo1/hahn/data/Nseries/'
            elif file_type.lower() == 'fft': 
                file_dir = '/mount/riachuelo1/hahn/FFT/Nseries/'
            else:
                file_dir = '/mount/riachuelo1/hahn/power/Nseries/'

        elif catalog['name'].lower() == 'patchy':                       # PATCHY ----------------------------------------
            
            if file_type.lower() == 'data': 
                file_dir = '/mount/riachuelo1/hahn/data/PATCHY/dr12/v6c/'
            elif file_type.lower() == 'fft': 
                file_dir = '/mount/riachuelo1/hahn/FFT/PATCHY/dr12/v6c/'
            else:
                file_dir = '/mount/riachuelo1/hahn/power/PATCHY/dr12/v6c/'

        elif 'bigmd' in catalog['name'].lower():                # Big MD --------------------
            if file_type.lower() == 'data': 
                file_dir = '/mount/riachuelo1/hahn/data/BigMD/'
            elif file_type.lower() == 'fft': 
                file_dir = '/mount/riachuelo1/hahn/FFT/BigMD/'
            else:
                file_dir = '/mount/riachuelo1/hahn/power/BigMD/'

        elif catalog['name'].lower() == 'cmass':                # CMASS ----------------------
            if file_type.lower() == 'data': 
                file_dir = '/mount/riachuelo1/hahn/data/CMASS/'
            elif file_type.lower() == 'fft': 
                file_dir = '/mount/riachuelo1/hahn/FFT/CMASS/'
            else:
                file_dir = '/mount/riachuelo1/hahn/power/CMASS/'
        else: 
            raise NameError('not yet coded')
    return file_dir 
