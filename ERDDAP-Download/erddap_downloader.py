import urllib.request
from pathlib import Path
from time import time
from shutil import move
import erddap_downloader_functions as edf

cwd=Path.cwd()

datasetID=r"jplG1SST"
file_type=".nc"

variables=["SST"] #sea surface temperature

constraints={
    #quebra do dicionario em varios sets de constraints, para download de varios arquivos ou variaveis
    "set1":{
        "time>=": "(2011-01-01T00:00:00Z)",
        "time<=": "(2011-02-01T00:00:00Z)",
        "stride_time": ":1:",
        "latitude>=": "(-19.995)",
        "latitude<=": "(-25.985)",
        "longitude>=": "(-37.995)",
        "longitude<=": "(-45.995)",
        "stride_coordinates": ":1:"},
    "set2":{
        "time>=": "(2010-06-09T12:00:00Z)",
        "time<=": "(2011-09-04T00:00:00Z)",
        "stride_time": ":1:",
        "latitude>=": "(-19.995)",
        "latitude<=": "(-25.985)",
        "longitude>=": "(-37.995)",
        "longitude<=": "(-45.995)",
        "stride_coordinates": ":1:",}
}

url=edf.url_creator(datasetID=datasetID,file_type=file_type,var_name=variables,constraints=constraints["set1"])
print(url)

start=time()
print("\nstarted download!")
file_name="01-2011-ERDDAP.nc"

r=urllib.request.urlretrieve(url,file_name)
finish=time()
print(f"total download time was {(finish-start)} seconds")

destination=r"C:\Users\bllet\Documents\UFRGS\2022_2\03.TCC\03.Working\leitor_ERDDAP\downloaded_files" + file_name
print(destination)

move(file_name,(destination))
print("done")
