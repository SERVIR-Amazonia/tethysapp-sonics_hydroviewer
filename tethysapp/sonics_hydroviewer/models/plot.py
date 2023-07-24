####################################################################################################
##                                   LIBRARIES AND DEPENDENCIES                                   ##
####################################################################################################

# Geoglows
import geoglows
import numpy as np
import math
import hydrostats as hs
import hydrostats.data as hd
import HydroErr as he
import plotly.graph_objs as go
import datetime as dt
import pandas as pd
from plotly.offline import plot as offline_plot


####################################################################################################
##                                      PLOTTING FUNCTIONS                                        ##
####################################################################################################

# Historical data
def plot_historical(observed_df, station_code):
    observed_plot = go.Scatter(x=observed_df.index, y=observed_df.iloc[:, 0].values, name='SONICS', line=dict(color="#636EFA"))
    layout = go.Layout(
            title='Simulación histórica SONICS:<br>COMID: {0}'.format(station_code),
            xaxis=dict(title='Serie temporal', ), yaxis=dict(title='Caudal (m<sup>3</sup>/s)', autorange=True),
            showlegend=True)
    return(go.Figure(data=[observed_plot], layout=layout))


# Forecast plot
def get_forecast_plot(comid, historical_sonics, gfs, eta_eqm, eta_scal, wrf):
    forecast_gfs_df = gfs
    forecast_eta_eqm_df = eta_eqm
    forecast_eta_scal_df = eta_scal
    forecast_wrf_df = wrf
    #
    sonics_records = historical_sonics.loc[historical_sonics.index >= pd.to_datetime(historical_sonics.index[-1] - dt.timedelta(days=8))]
    sonics_records = sonics_records.loc[sonics_records.index <= pd.to_datetime(historical_sonics.index[-1] + dt.timedelta(days=2))]
    #
    sonics_records_plot = go.Scatter(
                                name='Pronóstico antecedente SONICS',
                                x=sonics_records.index,
                                y=sonics_records.iloc[:, 0].values,
                                line=dict(color='#FFA15A'))
    x_vals = (sonics_records.index[0], forecast_gfs_df.index[len(forecast_gfs_df.index) - 1],
               forecast_gfs_df.index[len(forecast_gfs_df.index) - 1], sonics_records.index[0])
    max_visible = max(sonics_records.max())
    #
    forecast_gfs_plot = go.Scatter(
                                name='Pronóstico GFS',
                                x=forecast_gfs_df.index,
                                y=forecast_gfs_df['Streamflow (m3/s)'],
                                showlegend=True,
                                line=dict(color='black', dash='dash'))
    max_visible = max(max(forecast_gfs_df.max()), max_visible)
    #
    forecast_eta_eqm_plot = go.Scatter(
                                name='Pronóstico ETA eqm',
                                x=forecast_eta_eqm_df.index,
                                y=forecast_eta_eqm_df['Streamflow (m3/s)'],
                                showlegend=True,
                                line=dict(color='blue', dash='dash'))
    max_visible = max(max(forecast_eta_eqm_df.max()), max_visible)
    #
    forecast_eta_scal_plot =go.Scatter(
                                name='Pronóstico ETA scal',
                                x=forecast_eta_scal_df.index,
                                y=forecast_eta_scal_df['Streamflow (m3/s)'],
                                showlegend=True,
                                line=dict(color='green', dash='dash'))
    max_visible = max(max(forecast_eta_scal_df.max()), max_visible)
    #
    forecast_wrf_plot = go.Scatter(
                                name='Pronóstico WRF',
                                x=forecast_wrf_df.index,
                                y=forecast_wrf_df['Streamflow (m3/s)'],
                                showlegend=True,
                                line=dict(color='brown', dash='dash'))
    max_visible = max(max(forecast_wrf_df.max()), max_visible)    
    #
    layout = go.Layout(title='Pronóstico SONICS <br>COMID:{0}'.format(comid),
						   xaxis=dict(title='Fechas', ),
						   yaxis=dict(title='Caudal (m<sup>3</sup>/s)', autorange=True),
						   showlegend=True)
    hydroviewer_figure = go.Figure(data=[
                                        sonics_records_plot,
                                        forecast_gfs_plot, 
                                        forecast_eta_eqm_plot, 
                                        forecast_eta_scal_plot, 
                                        forecast_wrf_plot], 
                                    layout=layout)
    return(hydroviewer_figure)



