# -*- coding: utf-8 -*-
"""
Created on Sun Dec  9 10:26:08 2018
@author: SERJIM
"""

import cdsapi
import numpy as np
import pandas as pd
import datetime

def get_era5_year(lon,lat,var,year,file, months=['01', '02', '03', '04', '05', '06','07', '08', '09', '10', '11', '12'], 
                  days= ['01', '02', '03', '04', '05', '06',
                        '07', '08', '09', '10', '11', '12',
                        '13', '14', '15', '16', '17', '18',
                        '19', '20', '21', '22', '23', '24',
                        '25', '26', '27', '28', '29', '30','31'], grid_step=0.3):
    
    c = cdsapi.Client()
    c.retrieve(
        'reanalysis-era5-single-levels',
        {
            'variable':[
                var
                #'100m_v_component_of_wind'
                #'2m_temperature',
                #'surface_pressure'
            ],
            'product_type':'reanalysis',
            'year':[
                year
            ],
            'month': months
            ,
            'day': days
            ,
            'time':[
                '00:00','01:00','02:00',
                '03:00','04:00','05:00',
                '06:00','07:00','08:00',
                '09:00','10:00','11:00',
                '12:00','13:00','14:00',
                '15:00','16:00','17:00',
                '18:00','19:00','20:00',
                '21:00','22:00','23:00'
            ],
            'area': [lat+grid_step,lon-grid_step,lat-grid_step,lon+grid_step], # North, West, South, East. Default: global
            'grid': [grid_step,grid_step],
            'format':'netcdf'
        },
        file)

def get_era5_area_year(north,west,south,east,var,year,file,grid_step=0.25):
    c = cdsapi.Client()
    c.retrieve(
        'reanalysis-era5-single-levels',
        {
            'variable':[
                var
                #'100m_v_component_of_wind'
                #'2m_temperature',
                #'surface_pressure'
            ],
            'product_type':'reanalysis',
            'year':[
                year
            ],
            'month':[    
                 '01', '02', '03', '04', '05', '06',
                   '07', '08', '09', '10', '11', '12'
            ],
            'day':[
                '01', '02', '03', '04', '05', '06',
                    '07', '08', '09', '10', '11', '12',
                    '13', '14', '15', '16', '17', '18',
                    '19', '20', '21', '22', '23', '24',
                    '25', '26', '27', '28', '29', '30',
                    '31'
            ],
            'time':[
                '00:00','01:00','02:00',
                '03:00','04:00','05:00',
                '06:00','07:00','08:00',
                '09:00','10:00','11:00',
                '12:00','13:00','14:00',
                '15:00','16:00','17:00',
                '18:00','19:00','20:00',
                '21:00','22:00','23:00'
            ],
            'area': [north,west,south,east], # North, West, South, East. Default: global
            'grid': [grid_step,grid_step],
            'format':'netcdf'
        },
        file)




def get_era5(name,lon_d,lat_d,vars,yini,yend,months_last_year=['01','02','03','04','05','06','07','08','09','10','11','12'], 
    months=['01','02','03','04','05','06','07','08','09','10','11','12'], 
    days_last_month = ['01', '02', '03', '04', '05', '06',
            '07', '08', '09', '10', '11', '12',
            '13', '14', '15', '16', '17', '18',
            '19', '20', '21', '22', '23', '24',
            '25', '26', '27', '28', '29', '30','31'], 
    days= ['01', '02', '03', '04', '05', '06',
            '07', '08', '09', '10', '11', '12',
            '13', '14', '15', '16', '17', '18',
            '19', '20', '21', '22', '23', '24',
            '25', '26', '27', '28', '29', '30','31'], grid_step=0.3, dir_out="."):
    for y in range(yini,yend+1):
        for var in vars:
            print(str(y))
            file = f'{dir_out}/era5_{name}_{var}_{y}.nc'
            if y==yend:
                get_era5_year(lon_d,lat_d,var,str(y),file, months = months_last_year, days=days, grid_step=grid_step)
            else:
                get_era5_year(lon_d,lat_d,var,str(y),file, months= months, days=days, grid_step=grid_step)


def get_era5_9nodes_bydates(name, lon_d, lat_d,vars, date_ini, date_end, grid_step=0.3, dir_out="."):
    # Retrieves Data from 1st day of month of date_ini to last_day of month of date_end
    # date_ini = "2020-11-05"
    # date_end = "2021-02-04"
    date_ini = pd.to_datetime(date_ini)
    date_end = pd.to_datetime(date_end)
    yini = date_ini.year
    mini = date_ini.month
    yend = date_end.year
    mend = date_end.month
    days = [i for i in range(1,32)]
    if yini != yend:
        months_first_year = [i for i in range(mini,13)]
        months_last_year = [i for i in range(1,mend+1)]
    else:
        months_first_year = [i for i in range(mini,mend+1)]
        
    for y in range(yini,yend+1):
        for var in vars:
            print(f'--- Year: {y}\n')
            print(f'- Requesting var: {var}\n')
            print(f'Current Time:{datetime.datetime.now().strftime("%H:%M:%S")}')  
            file = f'{dir_out}/era5_{name}_{var}_{y}.nc'
            if y==yini:
                get_era5_year(lon_d,lat_d,var,str(y),file, months = months_first_year, days=days, grid_step=grid_step)
            elif y==yend:
                get_era5_year(lon_d,lat_d,var,str(y),file, months = months_last_year, days=days, grid_step=grid_step)
            else:
                get_era5_year(lon_d,lat_d,var,str(y),file, months = [i for i in range(1,13)] , days=days, grid_step=grid_step)
     
        
