# -*- coding: utf-8 -*-
"""
Created on Thu Jan 13 09:17:45 2022

@author: JOSRODRI/SERJIM
"""


import cdsapi
import numpy as np
import pandas as pd
import xarray as xr
import math
import os
from get_era5_cdsapi import * #check path where terminal is executing the code. The file above should be in the same directory.



def download_era5(site, lat, lon, start_date, end_date, outputDir, windData,TandPData, otherData):
#Downloads ERA5 data for the selected variables from Copernicus Data Store via its API (cdsapi).
#First it prepares the latitude and longituded inputs and then passes those inputs along with the rest to the function that retrieves the data from CDS.
#After calling this function, the output will be a series of .nc files containing the downloaded data for each variable and year.

    if windData == True:    
        vars_wind = ['100m_u_component_of_wind','100m_v_component_of_wind']
    else:
        vars_wind = []
        
    if TandPData == True:    
        vars_tp = ['2m_temperature', 'surface_pressure']
    else:
        vars_tp =  []
    
    if otherData is not None:    
        vars_others = otherData
    else:
        vars_others = []    
    
    vars=[*vars_wind,*vars_tp,*vars_others]
    
    lat_d = round(lat/0.3,0)*0.3
    lon_d = round(lon/0.3,0)*0.3
        
    get_era5_9nodes_bydates(name = site, lon_d=lon_d, lat_d=lat_d, vars=vars, 
                                date_ini=start_date, date_end = end_date, 
                                grid_step=0.3, dir_out=outputDir)
    return vars, vars_others

def ingest_era5(start_date, end_date, vars, site, outputDir):
#Processes previously downloaded .nc files to dataframes for each variable and year.
#As inputs, it takes the start and finish date, as well as the variables that have been downloaded.
#Returns a dataframe on which operations and modifications can be more easily performed.

    yini=pd.to_datetime(start_date).year
    yend=pd.to_datetime(end_date).year
    df_data =pd.DataFrame() 
    for y in range(yini, yend+1): 
        df_datay =pd.DataFrame() 
        print(f'----Processing {y}\n')
        for v in vars:
          file_path= os.path.join(outputDir, f'era5_{site}_{v}_{y}.nc')
          dataset = xr.open_mfdataset(file_path, combine='by_coords')
          lons = dataset.longitude.values
          lats = dataset.latitude.values
          times = dataset.time.values
          v_shortname = list(dataset.var())[0]  
          if 'expver' in list(dataset.dims):
              data1 = dataset.sel(expver=1).to_dataframe().iloc[:,1:]
              data2 = dataset.sel(expver=5).to_dataframe().iloc[:,1:]
              data = pd.concat([data1,data2], axis=1)
              data.columns = [v_shortname +"_" + str(i) for i in range(1,3)]
              data[v_shortname] = data.iloc[:,0].combine_first(data.iloc[:,1])
              data = data.loc[:,[v_shortname]]
              df_datay = pd.concat([df_datay,data], axis=1)
          else:
              data = dataset.to_dataframe()
              data.columns = [v_shortname]  
              df_datay = pd.concat([df_datay,data], axis=1)
        df_data = pd.concat([df_data,df_datay], axis=0)
    vars_short = list(df_data.keys()) 
    
    return df_data, vars_short    
   
def transform_era5(df_data, windData, TandPData, otherData, vars_others, vars_short):
# Takes the ERA 5 dataframe, along with the variables downloaded, and performs two sequential operations.
# Step1: transforms wind data from cartesian to polar form, and changes units of temperature to ºC and pressure to mbar/hPa.
# Step2: transposes to match DNVGL 9 coord format to export.
# Returns the transformed dataframe, along with an array containing the 9 coordinates. 
    
    if windData == True:
        df_data['ws']= ((df_data['u100'])**2+(df_data['v100'])**2)**(1/2)
        df_data['wd']=np.arctan2(-df_data['u100'],-df_data['v100'])*180/math.pi
        for i in range(0,len(df_data)):
            if df_data.iloc[i,df_data.columns.get_loc('wd')]<0:
                df_data.iloc[i,df_data.columns.get_loc('wd')]=360+df_data.iloc[i,df_data.columns.get_loc('wd')]
        df_data['u100']=df_data['ws']
        df_data['v100']=df_data['wd']       
        df_data.drop(['ws','wd'], axis=1, inplace=True)
        df_data.rename(columns = {'u100':'ws','v100':'wd'}, inplace=True)
    
    if TandPData == True:
        if 't2m' in df_data :
            df_data['t2m']= df_data['t2m']-273.15
        if 'sp' in df_data:
            df_data['sp']= df_data['sp']/100
 
        
    # Assing node to coordinates
     
    df_data.reset_index(inplace=True)
    df_data['latitude']=round(df_data['latitude'],1)
    df_data['longitude']=round(df_data['longitude'],1)
    lons=sorted(pd.unique(df_data['longitude']))
    lats=sorted(pd.unique(df_data['latitude']), reverse=True)
    cpoints= np.array([(x,y) for y in lats for x in lons])
    cpoints=pd.DataFrame(cpoints)
    cpoints['points']=("nw","n","ne","w","c","e","sw","s","se")
    cpoints.columns=('longitude', 'latitude', 'points')
    df_data.set_index(['longitude','latitude'], inplace=True)
    cpoints.set_index(['longitude','latitude'], inplace=True)
    df_data=df_data.merge(cpoints, on=['longitude', 'latitude'])
    df_data.set_index('time','points', append=True, inplace=True)  
    
    return df_data, cpoints


def write_header(file_name, line):
#Write a header to the final .txt file
    with open(file_name, 'w') as write_obj:
        # Write given line to file
        write_obj.write(line + '\n')

def export_era5(df_data, cpoints, site, windData, TandPData, otherData, vars, vars_others, vars_short, outputDir):
#Takes the ERA 5 dataframe, the coordinates array and initial inputs
#Prepares and export .txt file with wind speed and direction data
#Then prepares and export .txt file with temperature and pressure data

    if windData == True:
        wsp=df_data[['ws','points']].pivot_table(index='time',columns='points', values='ws').round(2).add_suffix('_ws')
        wdp=df_data[['wd','points']].pivot_table(index='time',columns='points', values='wd').round(2).add_suffix('_wd')
        data_export=wsp.join(wdp, on='time').reset_index()
        data_export['time']=pd.to_datetime(data_export['time'], format='%Y-%m-%d %H:%M:%S')
        data_export['Date']=data_export['time'].dt.date
        data_export['Time']=data_export['time'].dt.time
        data_export.drop('time', axis=1, inplace=True)
        data_export=data_export.reindex(columns=['Date','Time','c_ws','c_wd','n_ws','n_wd','ne_ws','ne_wd','e_ws','e_wd','se_ws','se_wd','s_ws','s_wd','sw_ws','sw_wd','w_ws','w_wd','nw_ws','nw_wd'])
        cpoints_alt=cpoints.reset_index().set_index('points').reindex(index=["c","n","ne","e","se","s","sw","w","nw"])
        cpoints_alt['nodes coordinates']='['+cpoints_alt['longitude'].astype(str)+','+cpoints_alt['latitude'].astype(str)+']'
        export_head="# Nodes coordinates: "+",".join(cpoints_alt['nodes coordinates'])
        file_name=f"era5_{site}_{min(data_export.Date).strftime('%Y-%m-%d')}_{max(data_export.Date).strftime('%Y-%m-%d')}.txt"
        write_header(os.path.join(outputDir, file_name),export_head)
        data_export.to_csv(os.path.join(outputDir, file_name), mode= "a", sep='\t', index=False)
            
    #----------------------------------------------------------------------------------------------------------
    
    if TandPData == True:
        Tp=df_data[['t2m','points']].pivot_table(index='time',columns='points', values='t2m').round(2).add_suffix('_T')
        
        if 'sp' in df_data.columns: 
            Pp=df_data[['sp','points']].pivot_table(index='time',columns='points', values='sp').round(2).add_suffix('_P')
            data_export=Tp.join(Pp, on='time').reset_index()
            data_export['time']=pd.to_datetime(data_export['time'], format='%Y-%m-%d %H:%M:%S')
            data_export['Date']=data_export['time'].dt.date
            data_export['Time']=data_export['time'].dt.time
            data_export.drop('time', axis=1, inplace=True)
            data_export=data_export.reindex(columns=['Date','Time','c_T','c_P','n_T','n_P','ne_T','ne_P','e_T','e_P','se_T','se_P','s_T','s_P','sw_T','sw_P','w_T','w_P','nw_T','nw_P'])
            cpoints_alt=cpoints.reset_index().set_index('points').reindex(index=["c","n","ne","e","se","s","sw","w","nw"])
            cpoints_alt['nodes coordinates']='['+cpoints_alt['longitude'].astype(str)+','+cpoints_alt['latitude'].astype(str)+']'
            export_head="# Nodes coordinates: "+",".join(cpoints_alt['nodes coordinates'])
            file_name=f"era5_TandP_{site}_{min(data_export.Date).strftime('%Y-%m-%d')}_{max(data_export.Date).strftime('%Y-%m-%d')}.txt"
            write_header(os.path.join(outputDir, file_name),export_head)
            data_export.to_csv(os.path.join(outputDir, file_name), mode= "a", sep='\t', index=False)     
            
        else:   
            data_export=Tp.reset_index()
            data_export['time']=pd.to_datetime(data_export['time'], format='%Y-%m-%d %H:%M:%S')
            data_export['Date']=data_export['time'].dt.date
            data_export['Time']=data_export['time'].dt.time
            data_export.drop('time', axis=1, inplace=True)
            data_export=data_export.reindex(columns=['Date','Time','c_T','n_T','ne_T','e_T','se_T','s_T','sw_T','w_T','nw_T'])
            cpoints_alt=cpoints.reset_index().set_index('points').reindex(index=["c","n","ne","e","se","s","sw","w","nw"])
            cpoints_alt['nodes coordinates']='['+cpoints_alt['longitude'].astype(str)+','+cpoints_alt['latitude'].astype(str)+']'
            export_head="# Nodes coordinates: "+",".join(cpoints_alt['nodes coordinates'])
            file_name=f"era5_T_{site}_{min(data_export.Date).strftime('%Y-%m-%d')}_{max(data_export.Date).strftime('%Y-%m-%d')}.txt"    
            write_header(os.path.join(outputDir, file_name),export_head)
            data_export.to_csv(os.path.join(outputDir, file_name), mode= "a", sep='\t', index=False)
        
    #----------------------------------------------------------------------------------------------------------
    if otherData is not None:
        
        for i in range(len(vars)-len(vars_others),len(vars)):    
    
            oD=df_data[[vars_short[i],'points']].pivot_table(index='time',columns='points', values=vars_short[i]).round(2).add_suffix('_'+vars_short[i])
            data_export=oD.reset_index()
            data_export['time']=pd.to_datetime(data_export['time'], format='%Y-%m-%d %H:%M:%S')
            data_export['Date']=data_export['time'].dt.date
            data_export['Time']=data_export['time'].dt.time
            data_export.drop('time', axis=1, inplace=True)
            data_export=data_export.reindex(columns=['Date','Time','c_'+vars_short[i],'n_'+vars_short[i],'ne_'+vars_short[i],'e_'+vars_short[i],'se_'+vars_short[i],'s_'+vars_short[i],'sw_'+vars_short[i],'w_'+vars_short[i],'nw_'+vars_short[i]])
            cpoints_alt=cpoints.reset_index().set_index('points').reindex(index=["c","n","ne","e","se","s","sw","w","nw"])
            cpoints_alt['nodes coordinates']='['+cpoints_alt['longitude'].astype(str)+','+cpoints_alt['latitude'].astype(str)+']'
            export_head="# Nodes coordinates: "+",".join(cpoints_alt['nodes coordinates'])
            file_name=f"era5_{vars_short[i]}_{site}_{min(data_export.Date).strftime('%Y-%m-%d')}_{max(data_export.Date).strftime('%Y-%m-%d')}.txt"    
            write_header(os.path.join(outputDir, file_name),export_head)
            data_export.to_csv(os.path.join(outputDir, file_name), mode= "a", sep='\t', index=False)