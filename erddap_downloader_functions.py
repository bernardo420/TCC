#URL_FORMAT: https://coastwatch.pfeg.noaa.gov/erddap/griddap/datasetID.fileType{?query}
#EXAMPLE: https://coastwatch.pfeg.noaa.gov/erddap/griddap/jplG1SST.nc?SST%5B(2013-12-19T00:00:00Z):1:(2013-12-19T00:00:00Z)%5D%5B(-25.985):1:(-19.995)%5D%5B(-45.995):1:(-37.995)%5D
#Note: ERDDAP uses "%5B" as a marker for start of query, and "%5D" as a  as escape characters
#when more than one variable to be downloaded is specified, the URL Parser expects them to be separated by commas, as in this:
#https://coastwatch.pfeg.noaa.gov/erddap/griddap/jplG1SST.nc?SST%5B(2013-12-19T00:00:00Z):1:(2013-12-19T00:00:00Z)%5D%5B(-25.985):1:(-19.995)%5D%5B(-45.995):1:(-37.995)%5D,mask%5B(2013-12-19T00:00:00Z):1:(2013-12-19T00:00:00Z)%5D%5B(-25.985):1:(-19.995)%5D%5B(-45.995):1:(-37.995)%5D


def url_creator(datasetID,file_type,var_name,constraints):
    """Recebe os outros parametros da query e formata a url para download
    Argumento constraints deve ser um dicionário, e deve seguir a convencao de nomenclatura especifica"""

    base_url=r"https://coastwatch.pfeg.noaa.gov/erddap/griddap/"

    url=base_url+datasetID+file_type+"?"+var_name[0]+"%5B"+constraints["time>="]+constraints["stride_time"]+constraints["time<="]+"%5D"\
    "%5B"+constraints["latitude>="]+constraints["stride_coordinates"]+constraints["latitude<="]+"%5D"\
    "%5B"+constraints["longitude>="]+constraints["stride_coordinates"]+constraints["longitude<="]+"%5D"

    return url





