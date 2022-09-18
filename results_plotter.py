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

adress= r'C:\Users\bllet\Documents\TCC\TCC\Results\monthly_results\mws-corrected-01-01-2015-02-01-2015'

dummy=xr.open_dataset(adress) 

#z0=charn*ustar**2/g

#mws_150m=u_star/k*np.log(z/z0)



# %%
