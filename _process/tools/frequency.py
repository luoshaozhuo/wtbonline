# -*- coding: utf-8 -*-
"""
Created on Tue Jun 13 10:46:05 2023

@author: luosz

数字信号频域函数
"""
#%% import 
import numpy as np
import pandas as pd

#%% function
def amplitude_spectrum(y_t, sample_spacing=1):
    '''
    Sample spacing : inverse of the sampling rate. Defaults to 1. 单位秒
    >>> sampling_sapcing = 0.01
    >>> x_t = np.arange(0, 1, sampling_sapcing)
    >>> y_t = np.sin(2*np.pi*x_t)
    >>> _ = plt.plot(x_t, y_t)
    >>> plt.show()
    >>> df = amplitude_spectrum(y_t, sampling_sapcing)
    >>> _ = df.plot('freq','amp', xlim=(-5,5))
    >>> plt.show()
    '''
    y_fft = np.abs(np.fft.fft(y_t))
    x_fft = np.fft.fftfreq(len(y_fft), sample_spacing)
    df = pd.DataFrame({'freq':x_fft, 'amp':y_fft})
    df = df.sort_values('freq').reset_index()
    return df

def power_spectrum(y_t, sample_spacing=1):
    '''
    Sample spacing : inverse of the sampling rate. Defaults to 1. 单位秒
    >>> sampling_sapcing = 0.01
    >>> x_t = np.arange(0, 1, sampling_sapcing)
    >>> y_t = np.sin(2*np.pi*x_t)
    >>> df = power_spectrum(y_t, sampling_sapcing)
    >>> _ = df.plot('freq','amp', xlim=(-5,5))
    '''    
    df = amplitude_spectrum(y_t, sample_spacing)
    df['amp'] = df['amp']*df['amp']/df.shape[0]
    return df

#%% test
if __name__ == "__main__":
    import doctest
    doctest.testmod()