####################################################################################################
##                                   LIBRARIES AND DEPENDENCIES                                   ##
####################################################################################################

# Tethys platform
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from tethys_sdk.routing import controller
from tethys_sdk.gizmos import PlotlyView

# Postgresql
import io
import os
import datetime as dt
import psycopg2
import pandas as pd
from sqlalchemy import create_engine
from pandas_geojson import to_geojson
from glob import glob

# App settings
from .app import SonicsHydroviewer as app 

# App models
from .models.data import *
from .models.plot import *



####################################################################################################
##                                       STATUS VARIABLES                                         ##
####################################################################################################

# Import enviromental variables 
DB_USER = app.get_custom_setting('DB_USER')
DB_PASS = app.get_custom_setting('DB_PASS')
DB_NAME = app.get_custom_setting('DB_NAME')
FOLDER =  app.get_custom_setting('FOLDER')

# Generate the conection token
tokencon = "postgresql+psycopg2://{0}:{1}@localhost:5432/{2}".format(DB_USER, DB_PASS, DB_NAME)



####################################################################################################
##                                   CONTROLLERS AND REST APIs                                    ##
####################################################################################################

@controller(name='home',url='sonics-hydroviewer/')
def home(request):
    forecast_nc_list = sorted(glob(os.path.join(FOLDER, "*.nc")))
    dates_array = []
    for file in forecast_nc_list:
        dates_array.append(file[len(FOLDER) + 1 + 23:-3])
    dates = []
    for date in dates_array:
        date_f = dt.datetime(int(date[0:4]), int(date[4:6]), int(date[6:8])).strftime('%Y-%m-%d')
        dates.append([date_f, date])
    context = {
        "server": app.get_custom_setting('SERVER'),
        "app_name": app.package,
        "start_date": dates[0][0],
        "end_date": dates[-1][0]
    }
    return render(request, 'sonics_hydroviewer/home.html', context) 




# Return alerts (in geojson format)
@controller(name='get_alerts',url='sonics-hydroviewer/get-alerts')
def get_alerts(request):
    # Establish connection to database
    db = create_engine(tokencon)
    conn = db.connect()
    # Query to database
    stations = pd.read_sql("select * from sonics_geoglows where alert != 'R0'", conn);
    conn.close()
    stations = to_geojson(
        df = stations,
        lat = "latitude",
        lon = "longitude",
        properties = ["comid", "latitude", "longitude", "loc1", "loc2", "alert"]
    )
    return JsonResponse(stations)


# Return rivers (in geojson format)
@controller(name='get_rivers',url='sonics-hydroviewer/get-rivers')
def get_rivers(request):
    # Establish connection to database
    db = create_engine(tokencon)
    conn = db.connect()
    # Query to database
    stations = pd.read_sql("select comid, latitude, longitude from sonics_geoglows", conn);
    conn.close()
    stations = to_geojson(
        df = stations,
        lat = "latitude",
        lon = "longitude",
        properties = ["comid", "latitude", "longitude"]
    )
    return JsonResponse(stations)



# Return streamflow station (in geojson format) 
@controller(name='get_data',url='sonics-hydroviewer/get-data')
def get_data(request):
    # Retrieving GET arguments
    station_comid = request.GET['comid']
    station_code = str(station_comid)
    forecast_date = request.GET['fecha']
    plot_width = float(request.GET['width']) - 12

    # Data series
    observed_data = get_sonic_historical(station_comid, FOLDER)

    # SONICS forecast
    initial_condition = observed_data.loc[observed_data.index == pd.to_datetime(observed_data.index[-1])]
    initial_condition.index = pd.to_datetime(initial_condition.index)
    initial_condition.index = initial_condition.index.to_series().dt.strftime("%Y-%m-%d")
    initial_condition.index = pd.to_datetime(initial_condition.index)
    initial_condition.rename(columns = {'Observed Streamflow':'Streamflow (m3/s)'}, inplace = True)
    gfs_data = get_gfs_data(station_comid, initial_condition, FOLDER)
    eta_eqm_data = get_eta_eqm_data(station_comid, initial_condition, FOLDER)
    eta_scal_data = get_eta_scal_data(station_comid, initial_condition, FOLDER)
    wrf_data = get_wrf_data(station_comid, initial_condition, FOLDER)

    # Historical data plot
    data_plot = plot_historical(observed_df = observed_data,station_code = station_code)
    forecast_plot = get_forecast_plot(
                        comid = station_comid, 
                        historical_sonics = observed_data, 
                        gfs = gfs_data, 
                        eta_eqm = eta_eqm_data, 
                        eta_scal = eta_scal_data, 
                        wrf = wrf_data)
    
    #returning
    context = {
        "corrected_data_plot": PlotlyView(data_plot.update_layout(width = plot_width)),
        "ensemble_forecast_plot": PlotlyView(forecast_plot.update_layout(width = plot_width)),
    }
    return render(request, 'sonics_hydroviewer/panel.html', context)





@controller(name='get_raw_forecast_date',url='sonics-hydroviewer/get-raw-forecast-date')
def get_raw_forecast_date(request):
    ## Variables
    station_comid = request.GET['comid']
    forecast_date = request.GET['fecha']
    plot_width = float(request.GET['width']) - 12

    # Data series
    observed_data = get_sonic_historical(station_comid, FOLDER, forecast_date)

    # SONICS forecast
    initial_condition = observed_data.loc[observed_data.index == pd.to_datetime(observed_data.index[-1])]
    initial_condition.index = pd.to_datetime(initial_condition.index)
    initial_condition.index = initial_condition.index.to_series().dt.strftime("%Y-%m-%d")
    initial_condition.index = pd.to_datetime(initial_condition.index)
    initial_condition.rename(columns = {'Observed Streamflow':'Streamflow (m3/s)'}, inplace = True)
    gfs_data = get_gfs_data(station_comid, initial_condition, FOLDER, forecast_date)
    eta_eqm_data = get_eta_eqm_data(station_comid, initial_condition, FOLDER, forecast_date)
    eta_scal_data = get_eta_scal_data(station_comid, initial_condition, FOLDER, forecast_date)
    wrf_data = get_wrf_data(station_comid, initial_condition, FOLDER, forecast_date)
    
    # Plotting raw forecast
    ensemble_forecast_plot = get_forecast_plot(
                                    comid = station_comid, 
                                    historical_sonics = observed_data, 
                                    gfs = gfs_data, 
                                    eta_eqm = eta_eqm_data, 
                                    eta_scal = eta_scal_data, 
                                    wrf = wrf_data).update_layout(width = plot_width).to_html() 


    
    return JsonResponse({
       'ensemble_forecast_plot': ensemble_forecast_plot,
    })
    




# Retrieve xlsx data
@controller(name='get_simulated_data_sonics_xlsx',url='sonics-hydroviewer/get-observed-data-xlsx')
def get_simulated_data_sonics_xlsx(request):
    # Retrieving GET arguments
    station_comid = request.GET['comid'] #9027406
    # Data series
    observed_data = get_sonic_historical(station_comid, FOLDER)
    observed_data = observed_data.rename(columns={"Observed Streamflow": "SONICS historical simulation (m3/s)"})
    # Crear el archivo Excel
    output = io.BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    observed_data.to_excel(writer, sheet_name='serie_historica_sonics', index=True)  # Aquí se incluye el índice 
    writer.save()
    output.seek(0)
    # Configurar la respuesta HTTP para descargar el archivo
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=serie_historica_sonics.xlsx'
    response.write(output.getvalue())
    return response

# Retrieve xlsx data
@controller(name='get_sonics_forecast_xlsx',url='sonics-hydroviewer/get-sonics-xlsx')
def get_sonics_forecast_xlsx(request):
    # Retrieving GET arguments
    station_comid = request.GET['comid'] #9027406
    forecast_date = request.GET['fecha']

    # Data series
    observed_data = get_sonic_historical(station_comid, FOLDER, forecast_date)

    # SONICS forecast
    initial_condition = observed_data.loc[observed_data.index == pd.to_datetime(observed_data.index[-1])]
    initial_condition.index = pd.to_datetime(initial_condition.index)
    initial_condition.index = initial_condition.index.to_series().dt.strftime("%Y-%m-%d")
    initial_condition.index = pd.to_datetime(initial_condition.index)
    initial_condition.rename(columns = {'Observed Streamflow':'Streamflow (m3/s)'}, inplace = True)
    gfs_data = get_gfs_data(station_comid, initial_condition, FOLDER, forecast_date)
    eta_eqm_data = get_eta_eqm_data(station_comid, initial_condition, FOLDER, forecast_date)
    eta_scal_data = get_eta_scal_data(station_comid, initial_condition, FOLDER, forecast_date)
    wrf_data = get_wrf_data(station_comid, initial_condition, FOLDER, forecast_date)

    gfs_data.rename(columns = {'Streamflow (m3/s)':'GFS (m3/S)'}, inplace = True)
    eta_eqm_data.rename(columns = {'Streamflow (m3/s)':'ETA EQM (m3/S)'}, inplace = True)
    eta_scal_data.rename(columns = {'Streamflow (m3/s)':'ETA SCAL (m3/S)'}, inplace = True)
    wrf_data.rename(columns = {'Streamflow (m3/s)':'WRF (m3/S)'}, inplace = True)

    # Combined data series
    sonics_forecast = gfs_data.merge(eta_eqm_data, on='datetime', how='inner')
    sonics_forecast = sonics_forecast.merge(eta_scal_data, on='datetime', how='inner')
    sonics_forecast = sonics_forecast.merge(wrf_data, on='datetime', how='inner')

    # Crear el archivo Excel
    output = io.BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    sonics_forecast.to_excel(writer, sheet_name='pronostico_sonics', index=True)  # Aquí se incluye el índice
    writer.save()
    output.seek(0)
    # Configurar la respuesta HTTP para descargar el archivo
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=pronostico_sonics.xlsx'
    response.write(output.getvalue())
    return response


