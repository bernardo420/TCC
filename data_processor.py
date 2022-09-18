#%%
from datetime import timedelta
from pytz import UTC
import xarray as xr
import numpy as np
#from pathlib import Path
import matplotlib.pyplot as plt
import scipy #xarray calls scipy's interpolation functions
#import metpy.calc as mpcalc

#global options setup
xr.set_options(keep_attrs=True)
plt.rcParams['figure.figsize'] = (25,20)
%matplotlib inline

#%%
#Constantes

#UTC_OFFSET=timedelta(hours=-3) #time offset
CD=0.0015 #Coeff of drag. Coeff of heat too
CP= 1004.67 #cp, in J/kg/K
#RELATIVE_HUMIDITY_SEAS=0.8 #from  Laine et al, 2014.
#R_0=287.05 #gas constant, dry air, inJ/kg/K
#R_W=461.5 #gas constant,water vapour, in J/kg/K
e=2.71828182845904523536028747135266249775724709369995 #euler/napier's number
k=0.4 #von karmann constant
g=9.81 #gravity
z=150 #height for calculation of wind speed influence
ni=1.5*10**-5 #kinematic viscosity
#coordenadas de pontos de análise
pnt_1_stable=[-23, -41.2] 
pnt_2_stable=[-23.470929, -43.882854]
pnt_3_normal=[-24.421367, -39.161394]


path_era5=r'C:\Users\bllet\Documents\TCC\TCC\input files\ERA5-Charnock\2012-ERA5.nc' #Path.cwd().joinpath("downloaded_files","01-2013-testERA5.nc")
path_ERDDAP= r'C:\Users\bllet\Documents\TCC\TCC\input files\2012-2013-erddap-old.nc' #Path.cwd().joinpath("downloaded_files","2011-2012-ERDDAP-old_dataset.nc")

init_date='01-01-2012' #input importante
end_date='04-01-2012' #input importante

#%%
#carregar dados

data_ERA5=xr.open_dataset(path_era5) 

data_erddap=xr.open_dataset(path_ERDDAP)

#restringir dados às datas limites

data_ERA5=data_ERA5.sel(time=slice(init_date,end_date))
data_erddap=data_erddap.sel(time=slice(init_date,end_date))

#%%
t2m=data_ERA5.t2m-273.15 #Kelvin to C
#sst_era5=data_ERA5.sst-273.15

#t2m[20,:,:].plot()

#data_erddap.SST[20,:,:].plot()
# %%
t2m_era5_daily=t2m.resample(time='1D').mean()# daily averages

t2m_era_5_interp=t2m_era5_daily.interp_like(data_erddap.SST,method= 'linear') #extrapolate=scipy 1d extrapolation

delta_T=t2m_era_5_interp-data_erddap.SST
delta_T=delta_T.assign_attrs(units='C', long_name='Air-sea Temp diff')
#delta_T[5,:,:].plot()

#%%
#calculo da velocidade

mws_100=(data_ERA5.u100**2+data_ERA5.v100**2)**0.5 #componentes u e v para a total

mws_100=mws_100.resample(time='1D').mean()
#mws_100[1,:,:].plot()

#%%
#potential temperatures

surf_press=data_ERA5.sp.resample(time='1D').mean()

theta_r= t2m*(10**5/surf_press)**0.286 #potential temperature, from Felipe M. Pimenta
theta_r=theta_r.resample(time='1D').mean()
#theta_r.latitude=np.round(theta_r['latitude'],2)
theta_r.assign_attrs(units='C', long_name='Potential temperature, at 100m')
#theta_0_era5= data_ERA5.sst*(10**5/data_ERA5.msl)**0.286

#%%
#usando ERDDAP

press=data_ERA5.sp.interp_like(data_erddap.SST,method='nearest') #interpola pressao para coordenadas erddap
#pw=(0.0000205*e**(0.0631846*(data_erddap.SST))).resample(time='1D').mean() #vapour pressure, in Pa

theta_0=(data_erddap.SST*(10**5/press)**0.286)
theta_0=theta_0.assign_attrs(units="C",long_name="potential temperature Theta_0")

#%%
#theta_0['latitude']=np.round(theta_0['latitude'],2)
theta_r=theta_r.interp_like(theta_0,method='linear')

#%%
#air_density=(1/data_ERA5.sst)*((press/R_0)-RELATIVE_HUMIDITY_SEAS*pw*(1/R_0-1/R_W))

#temp_dewpt=data_ERA5.d2m
#specific_humidity=mpcalc.specific_humidity_from_dewpoint(press, temp_dewpt)
air_density=data_ERA5.p140209.mean()
air_density

#%%
#calculo de H0

mws_100=mws_100.interp_like(theta_0)
#xr.align(delta_T,mws_100,join='exact')
h_0=(-CD*air_density*CP*mws_100)*(theta_r-theta_0)
h_0=h_0.assign_attrs(units='W m**-1', long_name='Mean surface heat flux')
#h_0[5,:,:].plot()


# %%
#calculo de Tau0 e ustar

tau_0=air_density*CD*(mws_100)**2

#ustar

u_star=(tau_0/air_density)**0.5
u_star=u_star.assign_attrs(units='m/s',long_name='Friction velocity')
#u_star[5,:,:].plot()

# %%
#Comprimento de obukhov

xr.align(u_star,data_erddap.SST,h_0,join='exact') #check para ver se coordenadas estao alinhadas

l_obk=-(u_star**3)/(k*g/(data_erddap.SST+273.15)*h_0/(air_density*CP))
l_obk=l_obk.assign_attrs(units='m',long_name='Obukhov length')
#l_obk[5,:,:].plot(robust=True) #robust=True plota o 2ndo e o 98vo percentis dos dados, para fugir de outliers

# %%
#calculo dos fatores de correcao de estabilidade de momento

x=(1-15*z/l_obk)**0.25 
psi_m=xr.where((z/l_obk)>0,(-5*z/l_obk), (np.log(((1+x**2)/2)*((1+x)**2)/2)-2*np.arctan(x)+np.pi/2))
psi_m=psi_m.assign_attrs(units='',long_name='Fator de correção de estabilidade Psi_m')
#psi_m[5,:,:].plot(robust=True)

#%%
#rugosidade superficial

charn=data_ERA5.chnk.interp_like(u_star,method='nearest')
z0=charn*u_star**2/g+ni/u_star
z0=z0.assign_attrs(units='m',long_name='rugosidade superficial')

#%%
mws_150m_neutral=u_star/k*np.log(z/z0)
mws_150m_neutral=mws_150m_neutral.assign_attrs(units='m/s',long_name='velocidade-150m-neutra')

mws_150m_corrected=u_star/k*(np.log(z/z0)-psi_m)
mws_150m_corrected=mws_150m_corrected.assign_attrs(units='m/s',long_name='velocidade-150m-corrigida')

#z0[5,:,:].plot()

#%%
#% differences, with and without stability

diff_mws_150=mws_150m_neutral-mws_150m_corrected
diff_mws_150=diff_mws_150.assign_attrs(units='m/s',long_name='diferença neutro-estabilidade')

diff_mws_150_perc=(mws_150m_neutral-mws_150m_corrected)/mws_150m_neutral*100
diff_mws_150_perc=diff_mws_150_perc.assign_attrs(units='%',long_name='diferença percentual neutro-estabilidade')

#diff_mws_150_perc[5,:,:].plot()
# %%
#Salvando medias mensais
results_folder=r"C:\Users\bllet\Documents\TCC\TCC\Results\monthly_results"

#l_obk.to_netcdf(fr"C:\Users\bllet\Documents\TCC\TCC\Results\lobk-{init_date}-{end_date}")
psi_m.resample(time="1M").mean().to_netcdf(results_folder+fr"\psi_m-{init_date}-{end_date}.nc")
mws_150m_neutral.resample(time="1M").mean().to_netcdf(results_folder+fr"\mws-neutral-{init_date}-{end_date}.nc")
mws_150m_corrected.resample(time="1M").mean().to_netcdf(results_folder+fr"\mws-corrected-{init_date}-{end_date}.nc")
diff_mws_150_perc.resample(time="1M").mean().to_netcdf(results_folder+fr"\perc-diff{init_date}-{end_date}.nc")
print("resultados mensais salvos")

# %%
#plotting specific points

diff_mws_150_perc_pnt_1=diff_mws_150_perc.isel(latitude=pnt_1_stable[0],longitude=pnt_1_stable[1])
diff_mws_150_perc_pnt_2=diff_mws_150_perc.isel(latitude=pnt_2_stable[0],longitude=pnt_2_stable[1])
diff_mws_150_perc_pnt_3=diff_mws_150_perc.isel(latitude=pnt_3_normal[0],longitude=pnt_3_normal[1])

diff_mws_150_perc_pnt_1.plot()
# %%
#selecionar pontos específicos e salvar a série temporal, para analisar

pnt_1_data=diff_mws_150_perc.sel(latitude=pnt_1_stable[0],longitude=pnt_1_stable[1],method='nearest')
pnt_1_data.to_netcdf(results_folder+r'\Timeseries'+fr"\diff_mws_150_perc-{pnt_1_stable[0]}-{pnt_1_stable[1]}-{init_date}-{end_date}.nc")

pnt_2_data=diff_mws_150_perc.sel(latitude=pnt_2_stable[0],longitude=pnt_2_stable[1],method='nearest')
pnt_2_data.to_netcdf(results_folder+r'\Timeseries'+fr"\diff_mws_150_perc-{pnt_2_stable[0]}-{pnt_2_stable[1]}-{init_date}-{end_date}.nc")

pnt_2_data=diff_mws_150_perc.sel(latitude=pnt_3_normal[0],longitude=pnt_3_normal[1],method='nearest')
pnt_2_data.to_netcdf(results_folder+r'\Timeseries'+fr"\diff_mws_150_perc-{pnt_3_normal[0]}-{pnt_3_normal[1]}-{init_date}-{end_date}.nc")