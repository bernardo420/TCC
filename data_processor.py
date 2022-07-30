#%%
import xarray as xr
from pathlib import Path
import matplotlib.pyplot as plt
import hvplot.xarray
plt.rcParams['figure.figsize'] = (25,20)
%matplotlib inline

adress=Path.cwd().joinpath("downloaded_files","01-2011-test.nc")

#%%
data_ERA5=xr.open_dataset(adress)

sst=data.sst[12,:,:]-273.15

sst.plot()
#%%
path_ERDDAP=Path.cwd().joinpath("downloaded_files","01-2011-testERDDAP.nc")

data_erddap=xr.open_dataset(path_ERDDAP)

data_erddap.SST[0,:,:].plot()
# %%
