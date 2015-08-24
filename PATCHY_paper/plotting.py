'''

Plotting for PATCHY paper bispectrum measurements


Author(s): ChangHoon Hahn 


'''


import numpy as np 
import scipy as sp
import os.path
import subprocess
import cosmolopy as cosmos
from matplotlib.collections import LineCollection

# --- Local --- 
from Spectrum import data as spec_data
from Spectrum import fft as spec_fft
from Spectrum import spec as spec_spec
from Spectrum import fortran as spec_fort

def plot_spec(x, y, type, fig=None, **kwargs): 
    ''' Plotting wrapper for powerspectrum and bispectrum 

    Parameters
    ----------
    x : k-values 
    y : P(k), P(k) ratio, B(k)
    type : pk, pk_ratio, bk, bk_ratio 

    Notes 
    -----
    * Flexible wraper that can plot powerspectrum and bispectrum

    '''
    # make figure pretty 
    prettyplot() 
    pretty_colors = prettycolors()
    
    # if fig is passed in kwargs then this function 
    # over plots 
    if fig == None: 
        fig = plt.figure(1, figsize=(7, 8)) # set up figure 

    sub = fig.add_subplot(111)
    
    if 'ls' not in kwargs.keys(): 
        lstyle = '-'
    else: 
        lstyle = kwargs['ls'] 

    if 'c' not in kwargs.keys(): 
        clr = pretty_colors[1]
    else: 
        clr = kwargs['c'] 
    
    if 'label' not in kwargs.keys(): 
        lbl = None 
    else: 
        lbl = kwargs['label'] 

    # plot P(k)
    sub.plot(x, y, color=clr, ls=lstyle, label=lbl, lw=4)

    # set axes
    # x-range 
    if 'xrange' in kwargs.keys(): 
        xlimit = kwargs['xrange']
    else: 
        if 'pk' in type: 
            xlimit = [10**-3,10**0]     # k range
        elif 'bk' in type or 'qk' in type: 
            if 'avgk' in kwargs.keys() or 'kmax' in kwargs.keys(): 
                xlimit = [10**-3,10**0]     # k range
            else: 
                xlimit = [0, 6500]          # triangle index range  
        else: 
            raise NotImplementedError('not yet implemented') 
    sub.set_xlim(xlimit)

    # y-range (DEPENDS ON TYPE)
    if 'yrange' in kwargs.keys(): 
        ylimit = kwargs['yrange'] 
    else: 
        if 'pk' in type.lower():
            if 'ratio' not in type.lower(): 
                ylimit = [10**2,10**5.5]
            else: 
                ylimit = [0.5, 2.0]
        elif 'bk' in type: 
            if 'ratio' not in type.lower(): 
                ylimit = [-0.5*10**11,2.0*10**11]
            else: 
                ylimit = [0.5, 2.0]
        elif 'qk' in type: 
            if 'ratio' not in type.lower(): 
                ylimit = [-5., 20.]
            else: 
                ylimit = [0.5, 2.0]
        else: 
            raise NotImplementedError('not yet implemented') 
    sub.set_ylim(ylimit)
    # x-label 
    sub.set_xlabel('k', fontsize=20)
    # y-label  
    if 'ylabel' in kwargs.keys(): 
        ylabel = kwargs['ylabel']
    else: 
        if 'pk' in type.lower(): 
            if 'ratio' not in type.lower(): 
                ylabel = r'$\mathtt{P_0(k)}$'
            else: 
                ylabel = r'$\mathtt{P_0(k)}$ ratio'
        elif 'bk' in type.lower(): 
            if 'ratio' not in type.lower(): 
                ylabel = r'$\mathtt{B(k)}$'
            else: 
                ylabel = r'$\mathtt{B(k)}$ ratio'
        elif 'qk' in type.lower(): 
            if 'ratio' not in type.lower(): 
                ylabel = r'$\mathtt{Q_{123}(k)}$'
            else: 
                ylabel = r'$\mathtt{Q_{123}(k)}$ ratio'
        else: 
            raise NotImplementedError('Not yet coded') 

    sub.set_ylabel(ylabel, fontsize=20)
    
    # log log plot hardcoded 
    sub.set_xscale('log')
    if 'pk' in type: 
        sub.set_yscale('log')

    sub.legend(loc='upper left', scatterpoints=1, prop={'size':14})
    return fig 

def plot_avgSpec_comp(catalog_names, n_mocks, type, **kwargs): 
    ''' Compare average P(k) for different catalogs 

    Parameters
    ----------
    catalogs_names : list of catalog names
    type : pk, pk_ratio, bk, bk_ratio, qk, qk_ratio

    Notes
    -----
    * uses plot_spec
    * currently P(k) values are from Bispectrum code output (k1, P(k1))

    '''
    if not isinstance(catalog_names, list): 
        catalog_names = [catalog_names]

    if n_mocks != None: 
        if not isinstance(n_mocks, list): 
            n_mocks = [n_mocks]

        if len(catalog_names) != len(n_mocks): 
            raise ValueError("Input list dimensions do not match!")
    else: 
        n_mocks = [None for i in range(len(catalog_names))]

    spec_fig = plt.figure(1, figsize=(7, 8)) # set up figure 

    for i_cat, catalog_name in enumerate(catalog_names): 
        # Loop through different catalogs

        # get list of catalog dictionaries 
        cat_dict_list = catalog_dict(catalog_name, n_mock=n_mocks[i_cat])

        if 'pk' in type: 
            k_arr, avg_spec = spec_spec.avg_spec(cat_dict_list, type, **kwargs)
        elif 'bk' in type or 'qk' in type: 
            k_arr, avg_spec = spec_spec.avg_spec(cat_dict_list, type, **kwargs)
        else: 
            raise NotImplementedError("Bispectrum not implemented yet")
        
        spec_fig = plot_spec(k_arr, avg_spec, type, fig=spec_fig, **kwargs)
    
    # save figure 
    fig_file = ''.join(['../figure/PATCHY_paper/', 
        'plot_avgSpec_comp_', type, '.png'])
    spec_fig.savefig(fig_file, bbox_inches='tight') 

    return None 

def catalog_dict(catalog_name, n_mock=None): 
    ''' Generate list of catalog dictionaries given catalog_name
    '''
    cat_dict_list = [] 
    if catalog_name == 'patchy': 
        # PATCHY mocks 
        if n_mock == None: 
            n_mock == 1000

        for i_mock in range(1, n_mock+1): 
            # correction and spec are left to default
            cat_dict_list.append(
                    {'catalog': {'name': 'patchy', 'n_mock': i_mock}}
                    )

    elif catalog_name == 'cmass': 
        # CMASS catalog
        raise NotImplementedError('CMASS not implemented yet')
    
    return cat_dict_list

if __name__=="__main__":
    plot_avgSpec_comp('patchy', 10, 'bk')
    plot_avgSpec_comp('patchy', 10, 'qk')

