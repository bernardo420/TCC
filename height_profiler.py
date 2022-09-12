#%%
#este arquivo consome os resultados do script data_processor.py e extrapola o perfil de velocidades a partir dele

from datetime import timedelta
from pytz import UTC
import xarray as xr
import numpy as np
#from pathlib import Path
import matplotlib.pyplot as plt
import scipy #xarray calls scipy's interpolation functions

#CONSTANTES

k=0.4 #von karmann constant
z=150 #height for calculation of wind speed influence
g=9.81

#CODIGO

psi_m_address= r'C:\Users\bllet\Documents\TCC\TCC\input files\ERA5-Charnock\adaptor.mars.internal-1662689162.808587-5628-16-4d66738b-b98a-417b-92b9-7634ef9eb003.nc' #endereço netcdf de fator de correção psi_m

psi_m=xr.open_dataset(psi_m_address) 

#z0=charn*ustar**2/g

#mws_150m=u_star/k*np.log(z/z0)



# %%
