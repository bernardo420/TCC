import xarray as xr
from pathlib import Path


adress=Path.cwd().joinpath("downloaded_files","download.nc")

data=xr.open_dataset(adress)

data.variables