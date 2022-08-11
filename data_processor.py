#%%
from datetime import timedelta
from pytz import UTC
import xarray as xr
from pathlib import Path
import matplotlib.pyplot as plt
import hvplot.xarray
plt.rcParams['figure.figsize'] = (25,20)
%matplotlib inline
import scipy #xarray calls scipy's interpolation functions

UTC_OFFSET=timedelta(hours=-3) #time offset
CD=0.0015 #Coeff of drag. Coeff of heat too
CP= 1004.67 #cp, in J/kg/K
RELATIVE_HUMIDITY_SEAS=0.8 #from  Laine et al, 2014.
R_0=287.05 #gas constant, dry air, inJ/kg/K
R_W=461.5 #gas constant,water vapour, in J/kg/K
e=2.71828182845904523536028747135266249775724709369995 #euler/napier's number

adress=Path.cwd().joinpath("downloaded_files","01-2011-testERA5.nc")
path_ERDDAP=Path.cwd().joinpath("downloaded_files","jplG1SST_7310_fefb_f1a5.nc")


#%%
#carregar dados

data_ERA5=xr.open_dataset(adress) 

data_erddap=xr.open_dataset(path_ERDDAP)

#%%
t2m=data_ERA5.t2m-273.15 #Kelvin to C
sst_era5=data_ERA5.sst-273.15

t2m[20,:,:].plot()

data_erddap.SST[20,:,:].plot()
# %%
t2m_era5_daily=t2m.resample(time='1D').mean()# daily averages

interpolated=t2m_era5_daily.interp_like(data_erddap.SST,method= 'nearest') #extrapolate=scipy 1d extrapolation

delta_T=interpolated-data_erddap.SST
delta_T[20,:,:].plot()

#%%
#calculo da velocide

mws_100=(data_ERA5.u100**2+data_ERA5.v100**2)**0.5 #componentes u e v para a total

mws_100[1,:,:].plot()
#%%
#temperatures

theta_r= t2m*(10**5/data_ERA5.msl)**0.286 #potential temperature, from Felipe M. Pimenta

press=data_ERA5.msl.interp_like(data_erddap.SST,method='nearest')

theta_0=data_erddap.SST*(10**5/press)**0.286

pw=(0.0000205*e**(0.0631846*(data_ERA5.sst)))#.resample(time='1D').mean() #vapour pressure, in Pa
#%%
#air_density=(1/data_ERA5.sst)*((press/R_0)-RELATIVE_HUMIDITY_SEAS*pw*(1/R_0-1/R_W))

h_0=-1*data_ERA5.p140209*CD*mws_100*(theta_r-theta_0)




# %%
#calculo de Tau0 e H0

tau_0=data_ERA5.p140209*CD*(mws_100)**2
tau_0[0,:,:].plot()

#%%


# %%
